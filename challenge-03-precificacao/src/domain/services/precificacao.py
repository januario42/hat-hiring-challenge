from decimal import Decimal, ROUND_HALF_UP
from typing import List
from dataclasses import dataclass

from src.domain.enums import Senioridade
from src.domain.schemas import ProfissionalInput, ProfissionalBreakdown

PRECISAO = Decimal("0.01")

TABELA_PRECOS = {
    Senioridade.JUNIOR: {"custo": Decimal("45.00"), "venda": Decimal("95.00")},
    Senioridade.PLENO: {"custo": Decimal("75.00"), "venda": Decimal("155.00")},
    Senioridade.SENIOR: {"custo": Decimal("120.00"), "venda": Decimal("245.00")},
    Senioridade.ESPECIALISTA: {"custo": Decimal("180.00"), "venda": Decimal("380.00")},
    Senioridade.GERENTE: {"custo": Decimal("250.00"), "venda": Decimal("520.00")},
}


@dataclass
class ResultadoCalculo:
    custo_total: Decimal
    valor_venda: Decimal
    margem_bruta_pct: Decimal
    breakdown: List[ProfissionalBreakdown]


def calcular_proposta(profissionais: List[ProfissionalInput]) -> ResultadoCalculo:
    custo_total = Decimal("0.00")
    valor_venda_total = Decimal("0.00")
    breakdown = []

    for prof in profissionais:
        taxas = TABELA_PRECOS[prof.senioridade]

        custo_prof = (taxas["custo"] * Decimal(prof.horas_estimadas)).quantize(PRECISAO, rounding=ROUND_HALF_UP)
        venda_prof = (taxas["venda"] * Decimal(prof.horas_estimadas)).quantize(PRECISAO, rounding=ROUND_HALF_UP)

        custo_total += custo_prof
        valor_venda_total += venda_prof

        breakdown.append(
            ProfissionalBreakdown(
                nome=prof.nome,
                senioridade=prof.senioridade,
                horas_estimadas=prof.horas_estimadas,
                custo=custo_prof,
                valor_venda=venda_prof,
            )
        )

    if valor_venda_total > 0:
        margem = ((valor_venda_total - custo_total) / valor_venda_total * Decimal("100")).quantize(PRECISAO, rounding=ROUND_HALF_UP)
    else:
        margem = Decimal("0.00")

    return ResultadoCalculo(
        custo_total=custo_total.quantize(PRECISAO, rounding=ROUND_HALF_UP),
        valor_venda=valor_venda_total.quantize(PRECISAO, rounding=ROUND_HALF_UP),
        margem_bruta_pct=margem,
        breakdown=breakdown,
    )