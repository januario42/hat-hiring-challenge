from decimal import Decimal
from src.domain.enums import StatusProposta


def avaliar_status_por_margem(margem: Decimal) -> StatusProposta:
    """Determina o status da proposta com base na margem bruta calculada."""
    if margem < Decimal("40.00"):
        return StatusProposta.REPROVADA
    elif margem <= Decimal("45.00"):
        return StatusProposta.PENDENTE
    return StatusProposta.APROVADA


def validar_transicao_status(status_atual: StatusProposta, novo_status: StatusProposta) -> None:
    """Garante que transições de estado inválidas sejam bloqueadas."""
    if status_atual == StatusProposta.APROVADA and novo_status == StatusProposta.PENDENTE:
        raise ValueError("Proposta APROVADA não pode retornar para PENDENTE sem evento explícito.")