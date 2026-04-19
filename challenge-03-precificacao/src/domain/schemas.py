from pydantic import BaseModel
from typing import List
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from src.domain.enums import StatusProposta, Senioridade, NivelAprovador

class ProfissionalInput(BaseModel):
    nome: str
    senioridade: Senioridade
    horas_estimadas: int

class PropostaInput(BaseModel):
    cliente: str
    descricao: str
    data_inicio: date
    data_fim: date
    profissionais: List[ProfissionalInput]

class DescontoInput(BaseModel):
    aprovador: str
    nivel: NivelAprovador
    desconto_pct: Decimal

class ProfissionalBreakdown(BaseModel):
    nome: str
    senioridade: Senioridade
    horas_estimadas: int
    custo: Decimal
    valor_venda: Decimal
    model_config = {"from_attributes": True}

class AprovacaoOutput(BaseModel):
    aprovador: str
    nivel: NivelAprovador
    desconto_aplicado: Decimal
    timestamp: datetime
    model_config = {"from_attributes": True}

class PropostaOutput(BaseModel):
    id: UUID
    cliente: str
    descricao: str
    data_inicio: date
    data_fim: date
    status: StatusProposta
    custo_total: Decimal
    valor_venda: Decimal
    margem_bruta_pct: Decimal
    desconto_aplicado: Decimal
    created_at: datetime
    breakdown: List[ProfissionalBreakdown]
    aprovacoes: List[AprovacaoOutput]
    alertas: List[str]
    model_config = {"from_attributes": True}