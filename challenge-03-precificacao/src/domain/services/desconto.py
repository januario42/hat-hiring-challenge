from decimal import Decimal
from typing import List

from src.domain.enums import NivelAprovador
from src.domain.models import Aprovacao 


LIMITE_DESCONTO = {
    NivelAprovador.EXECUTIVO_VENDAS: Decimal("5.00"),
    NivelAprovador.GERENTE_COMERCIAL: Decimal("15.00"),
    NivelAprovador.DIRETOR: Decimal("25.00"),
    NivelAprovador.CEO: Decimal("40.00"),
}


def aplicar_desconto(
    desconto_pct: Decimal, 
    nivel: NivelAprovador, 
    aprovacoes_existentes: List[Aprovacao]
) -> Decimal:
    """
    Calcula o desconto acumulado e valida se o aprovador tem permissão 
    para o novo teto gerado.
    """
    desconto_acumulado_atual = sum(
        (aprovacao.desconto_aplicado for aprovacao in aprovacoes_existentes), 
        Decimal("0.00")
    )
    
    novo_desconto_acumulado = desconto_acumulado_atual + desconto_pct
    limite_permitido = LIMITE_DESCONTO[nivel]
    
    if novo_desconto_acumulado > limite_permitido:
        raise ValueError(
            f"Desconto negado: O desconto acumulado de {novo_desconto_acumulado}% "
            f"ultrapassa o limite de {limite_permitido}% do nível {nivel.name}."
        )
        
    return novo_desconto_acumulado