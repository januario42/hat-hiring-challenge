from uuid import UUID, uuid4
from datetime import datetime, date, timezone
from decimal import Decimal
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship

from src.domain.enums import StatusProposta, Senioridade, NivelAprovador


class Proposta(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    cliente: str
    descricao: str
    data_inicio: date
    data_fim: date
    status: StatusProposta = Field(default=StatusProposta.PENDENTE)
    custo_total: Decimal = Field(default=Decimal("0.00"))
    valor_venda: Decimal = Field(default=Decimal("0.00"))
    margem_bruta_pct: Decimal = Field(default=Decimal("0.00"))
    desconto_aplicado: Decimal = Field(default=Decimal("0.00"))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    profissionais: List["Profissional"] = Relationship(back_populates="proposta")
    aprovacoes: List["Aprovacao"] = Relationship(back_populates="proposta")


class Profissional(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    proposta_id: UUID = Field(foreign_key="proposta.id")
    nome: str
    senioridade: Senioridade
    horas_estimadas: int
    custo: Decimal = Field(default=Decimal("0.00"))
    valor_venda: Decimal = Field(default=Decimal("0.00"))

    proposta: Optional[Proposta] = Relationship(back_populates="profissionais")


class Aprovacao(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    proposta_id: UUID = Field(foreign_key="proposta.id")
    aprovador: str
    nivel: NivelAprovador
    desconto_aplicado: Decimal = Field(default=Decimal("0.00"))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    proposta: Optional[Proposta] = Relationship(back_populates="aprovacoes")