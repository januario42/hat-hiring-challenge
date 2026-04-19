import pytest
from uuid import uuid4
from decimal import Decimal

from src.domain.enums import NivelAprovador
from src.domain.models import Aprovacao
from src.domain.services.desconto import aplicar_desconto

def test_desconto_dentro_do_limite_retorna_valor():
    resultado = aplicar_desconto(
        desconto_pct=Decimal("5.00"),
        nivel=NivelAprovador.EXECUTIVO_VENDAS,
        aprovacoes_existentes=[]
    )
    assert resultado == Decimal("5.00")

def test_desconto_acumulado_valido_soma_valores():
    aprovacao_existente = Aprovacao(
        id=uuid4(),
        proposta_id=uuid4(),
        aprovador="João",
        nivel=NivelAprovador.EXECUTIVO_VENDAS,
        desconto_aplicado=Decimal("5.00")
    )
    
    resultado = aplicar_desconto(
        desconto_pct=Decimal("8.00"),
        nivel=NivelAprovador.GERENTE_COMERCIAL,
        aprovacoes_existentes=[aprovacao_existente]
    )
    assert resultado == Decimal("13.00")

def test_desconto_acumulado_invalido_lanca_excecao():
    aprovacao_existente = Aprovacao(
        id=uuid4(),
        proposta_id=uuid4(),
        aprovador="João",
        nivel=NivelAprovador.EXECUTIVO_VENDAS,
        desconto_aplicado=Decimal("5.00")
    )
    with pytest.raises(ValueError, match="ultrapassa o limite"):
        aplicar_desconto(
            desconto_pct=Decimal("12.00"),
            nivel=NivelAprovador.GERENTE_COMERCIAL,
            aprovacoes_existentes=[aprovacao_existente]
        )