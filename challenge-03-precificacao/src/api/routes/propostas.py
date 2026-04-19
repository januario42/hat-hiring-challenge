from typing import Optional, List
from datetime import date
from uuid import UUID
from decimal import Decimal, ROUND_HALF_UP

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from src.infra.database import get_session
from src.domain.models import Proposta, Profissional, Aprovacao
from src.domain.schemas import PropostaInput, PropostaOutput, DescontoInput, ProfissionalBreakdown, AprovacaoOutput
from src.domain.enums import StatusProposta
from src.domain.services.precificacao import calcular_proposta
from src.domain.services.validacao import avaliar_status_por_margem
from src.domain.services.desconto import aplicar_desconto

router = APIRouter(tags=["Propostas"])

PRECISAO = Decimal("0.01")


def _quantize(value: Decimal) -> Decimal:
    return Decimal(str(value)).quantize(PRECISAO, rounding=ROUND_HALF_UP)


def _build_proposta_output(proposta: Proposta, breakdown, aprovacoes) -> PropostaOutput:
    return PropostaOutput(
        id=proposta.id,
        cliente=proposta.cliente,
        descricao=proposta.descricao,
        data_inicio=proposta.data_inicio,
        data_fim=proposta.data_fim,
        status=proposta.status,
        custo_total=_quantize(proposta.custo_total),
        valor_venda=_quantize(proposta.valor_venda),
        margem_bruta_pct=_quantize(proposta.margem_bruta_pct),
        desconto_aplicado=_quantize(proposta.desconto_aplicado),
        created_at=proposta.created_at,
        breakdown=breakdown,
        aprovacoes=aprovacoes,
        alertas=["Margem próxima do limite mínimo"] if proposta.margem_bruta_pct <= Decimal("45.00") else [],
    )


def _build_breakdown(profissionais) -> List[ProfissionalBreakdown]:
    return [
        ProfissionalBreakdown(
            nome=p.nome,
            senioridade=p.senioridade,
            horas_estimadas=p.horas_estimadas,
            custo=_quantize(p.custo),
            valor_venda=_quantize(p.valor_venda),
        ) for p in profissionais
    ]


def _build_aprovacoes(aprovacoes) -> List[AprovacaoOutput]:
    return [
        AprovacaoOutput(
            aprovador=a.aprovador,
            nivel=a.nivel,
            desconto_aplicado=_quantize(a.desconto_aplicado),
            timestamp=a.timestamp,
        ) for a in aprovacoes
    ]


@router.post("/", response_model=PropostaOutput)
def criar_proposta(payload: PropostaInput, session: Session = Depends(get_session)):
    calculo = calcular_proposta(payload.profissionais)
    status_inicial = avaliar_status_por_margem(calculo.margem_bruta_pct)

    nova_proposta = Proposta(
        cliente=payload.cliente,
        descricao=payload.descricao,
        data_inicio=payload.data_inicio,
        data_fim=payload.data_fim,
        status=status_inicial,
        custo_total=calculo.custo_total,
        valor_venda=calculo.valor_venda,
        margem_bruta_pct=calculo.margem_bruta_pct,
    )

    session.add(nova_proposta)
    session.commit()
    session.refresh(nova_proposta)

    for p in calculo.breakdown:
        session.add(Profissional(
            proposta_id=nova_proposta.id,
            nome=p.nome,
            senioridade=p.senioridade,
            horas_estimadas=p.horas_estimadas,
            custo=p.custo,
            valor_venda=p.valor_venda,
        ))

    session.commit()

    return _build_proposta_output(nova_proposta, calculo.breakdown, [])


@router.get("/", response_model=List[PropostaOutput])
def listar_propostas(
    status: Optional[StatusProposta] = None,
    cliente: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    session: Session = Depends(get_session),
):
    query = select(Proposta)

    if status:
        query = query.where(Proposta.status == status)
    if cliente:
        query = query.where(Proposta.cliente.ilike(f"%{cliente}%"))
    if data_inicio:
        query = query.where(Proposta.data_inicio >= data_inicio)
    if data_fim:
        query = query.where(Proposta.data_fim <= data_fim)

    propostas_db = session.exec(query).all()

    resultado = []
    for p in propostas_db:
        profissionais = session.exec(select(Profissional).where(Profissional.proposta_id == p.id)).all()
        aprovacoes = session.exec(select(Aprovacao).where(Aprovacao.proposta_id == p.id)).all()
        resultado.append(_build_proposta_output(p, _build_breakdown(profissionais), _build_aprovacoes(aprovacoes)))

    return resultado


@router.get("/{id}", response_model=PropostaOutput)
def obter_proposta(id: UUID, session: Session = Depends(get_session)):
    proposta = session.get(Proposta, id)
    if not proposta:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")

    profissionais = session.exec(select(Profissional).where(Profissional.proposta_id == id)).all()
    aprovacoes = session.exec(select(Aprovacao).where(Aprovacao.proposta_id == id)).all()

    return _build_proposta_output(proposta, _build_breakdown(profissionais), _build_aprovacoes(aprovacoes))


@router.post("/{id}/aplicar-desconto", response_model=PropostaOutput)
def aplicar_desconto_proposta(id: UUID, payload: DescontoInput, session: Session = Depends(get_session)):
    proposta = session.get(Proposta, id)
    if not proposta:
        raise HTTPException(status_code=404, detail="Proposta não encontrada")

    aprovacoes_existentes = session.exec(select(Aprovacao).where(Aprovacao.proposta_id == id)).all()

    try:
        novo_desconto_acumulado = aplicar_desconto(
            desconto_pct=payload.desconto_pct,
            nivel=payload.nivel,
            aprovacoes_existentes=aprovacoes_existentes,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    nova_aprovacao = Aprovacao(
        proposta_id=proposta.id,
        aprovador=payload.aprovador,
        nivel=payload.nivel,
        desconto_aplicado=payload.desconto_pct,
    )

    proposta.desconto_aplicado = novo_desconto_acumulado
    session.add(nova_aprovacao)
    session.add(proposta)
    session.commit()
    session.refresh(proposta)

    profissionais = session.exec(select(Profissional).where(Profissional.proposta_id == id)).all()

    return _build_proposta_output(
        proposta,
        _build_breakdown(profissionais),
        _build_aprovacoes(list(aprovacoes_existentes) + [nova_aprovacao]),
    )