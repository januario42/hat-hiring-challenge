import pytest
from decimal import Decimal
from src.domain.services.validacao import avaliar_status_por_margem, validar_transicao_status
from src.domain.enums import StatusProposta


def test_margem_abaixo_minimo_retorna_reprovada():
    assert avaliar_status_por_margem(Decimal("10.00")) == StatusProposta.REPROVADA
    assert avaliar_status_por_margem(Decimal("39.99")) == StatusProposta.REPROVADA


def test_margem_no_limite_retorna_pendente():
    assert avaliar_status_por_margem(Decimal("40.00")) == StatusProposta.PENDENTE
    assert avaliar_status_por_margem(Decimal("42.50")) == StatusProposta.PENDENTE
    assert avaliar_status_por_margem(Decimal("45.00")) == StatusProposta.PENDENTE


def test_margem_acima_limite_retorna_aprovada():
    assert avaliar_status_por_margem(Decimal("45.01")) == StatusProposta.APROVADA
    assert avaliar_status_por_margem(Decimal("60.00")) == StatusProposta.APROVADA


def test_transicao_aprovada_para_pendente_lanca_excecao():
    with pytest.raises(ValueError, match="evento explícito"):
        validar_transicao_status(StatusProposta.APROVADA, StatusProposta.PENDENTE)