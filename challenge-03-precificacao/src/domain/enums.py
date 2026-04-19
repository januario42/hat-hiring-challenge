from enum import Enum

class StatusProposta(str, Enum):
    APROVADA = "APROVADA"
    PENDENTE = "PENDENTE"
    REPROVADA = "REPROVADA"

class Senioridade(str, Enum):
    JUNIOR ="JUNIOR"
    PLENO = "PLENO"
    SENIOR = "SENIOR"
    ESPECIALISTA = "ESPECIALISTA"
    GERENTE = "GERENTE"

class NivelAprovador(str, Enum):
    EXECUTIVO_VENDAS = "EXECUTIVO_VENDAS"
    GERENTE_COMERCIAL = "GERENTE_COMERCIAL"
    DIRETOR = "DIRETOR"
    CEO = "CEO"