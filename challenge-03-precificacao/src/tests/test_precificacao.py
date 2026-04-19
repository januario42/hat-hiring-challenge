from decimal import Decimal
from src.domain.enums import Senioridade, StatusProposta
from src.domain.schemas import ProfissionalInput
from src.domain.services.precificacao import calcular_proposta, TABELA_PRECOS
from src.domain.services.validacao import avaliar_status_por_margem


def test_zero_horas_retorna_margem_zero_e_status_reprovado():
    profissionais = [
        ProfissionalInput(nome="Teste Zero", senioridade=Senioridade.JUNIOR, horas_estimadas=0)
    ]
    resultado = calcular_proposta(profissionais)
    status = avaliar_status_por_margem(resultado.margem_bruta_pct)
    assert resultado.custo_total == Decimal("0.00")
    assert resultado.valor_venda == Decimal("0.00")
    assert resultado.margem_bruta_pct == Decimal("0.00")
    assert status == StatusProposta.REPROVADA


def test_calculo_correto_para_um_junior_com_dez_horas():
    profissionais = [
        ProfissionalInput(nome="Dev Junior", senioridade=Senioridade.JUNIOR, horas_estimadas=10)
    ]
    resultado = calcular_proposta(profissionais)
    assert resultado.custo_total == Decimal("450.00")
    assert resultado.valor_venda == Decimal("950.00")


def test_mix_de_senioridades_calcula_totais_corretamente():
    profissionais = [
        ProfissionalInput(nome="Ana", senioridade=Senioridade.SENIOR, horas_estimadas=320),
        ProfissionalInput(nome="Bruno", senioridade=Senioridade.PLENO, horas_estimadas=480),
        ProfissionalInput(nome="Carla", senioridade=Senioridade.JUNIOR, horas_estimadas=200)
    ]
    resultado = calcular_proposta(profissionais)
    assert resultado.custo_total == Decimal("83400.00")
    assert resultado.valor_venda == Decimal("171800.00")


def test_tabela_precos_contem_todas_as_senioridades():
    assert Senioridade.JUNIOR in TABELA_PRECOS
    assert Senioridade.PLENO in TABELA_PRECOS
    assert Senioridade.SENIOR in TABELA_PRECOS
    assert Senioridade.ESPECIALISTA in TABELA_PRECOS
    assert Senioridade.GERENTE in TABELA_PRECOS


def test_breakdown_contem_todos_os_profissionais():
    profissionais = [
        ProfissionalInput(nome="Ana", senioridade=Senioridade.SENIOR, horas_estimadas=100),
        ProfissionalInput(nome="Bruno", senioridade=Senioridade.JUNIOR, horas_estimadas=50),
    ]
    resultado = calcular_proposta(profissionais)
    assert len(resultado.breakdown) == 2
    assert resultado.breakdown[0].nome == "Ana"
    assert resultado.breakdown[1].nome == "Bruno"


def test_margem_calculada_corretamente():
    profissionais = [
        ProfissionalInput(nome="Dev", senioridade=Senioridade.JUNIOR, horas_estimadas=10)
    ]
    resultado = calcular_proposta(profissionais)
    margem_esperada = ((Decimal("950.00") - Decimal("450.00")) / Decimal("950.00") * Decimal("100")).quantize(Decimal("0.01"))
    assert resultado.margem_bruta_pct == margem_esperada