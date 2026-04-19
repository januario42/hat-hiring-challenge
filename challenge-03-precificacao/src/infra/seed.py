from datetime import date
from sqlmodel import Session

from src.infra.database import engine, create_db_and_tables
from src.domain.models import Proposta, Profissional
from src.domain.schemas import ProfissionalInput
from src.domain.enums import Senioridade
from src.domain.services.precificacao import calcular_proposta
from src.domain.services.validacao import avaliar_status_por_margem

PROPOSTAS_SEED = [
    {
        "cliente": "Itaú Unibanco",
        "descricao": "Migração de Sistema Core para AWS",
        "data_inicio": date(2026, 6, 1),
        "data_fim": date(2026, 12, 31),
        "profissionais": [
            ProfissionalInput(nome="Mariana Lima", senioridade=Senioridade.GERENTE, horas_estimadas=160),
            ProfissionalInput(nome="Lucas Pereira", senioridade=Senioridade.ESPECIALISTA, horas_estimadas=320),
            ProfissionalInput(nome="João Silva", senioridade=Senioridade.PLENO, horas_estimadas=400),
        ],
    },
    {
        "cliente": "Nubank",
        "descricao": "Desenvolvimento de App Mobile Internacional",
        "data_inicio": date(2026, 5, 10),
        "data_fim": date(2026, 10, 30),
        "profissionais": [
            ProfissionalInput(nome="Ana Souza", senioridade=Senioridade.SENIOR, horas_estimadas=480),
            ProfissionalInput(nome="Carlos Santos", senioridade=Senioridade.PLENO, horas_estimadas=480),
        ],
    },
    {
        "cliente": "Petrobras",
        "descricao": "Auditoria de Segurança da Informação",
        "data_inicio": date(2026, 7, 1),
        "data_fim": date(2026, 8, 15),
        "profissionais": [
            ProfissionalInput(nome="Roberto Alves", senioridade=Senioridade.ESPECIALISTA, horas_estimadas=120),
        ],
    },
    {
        "cliente": "Ambev",
        "descricao": "Implementação e Customização de ERP SAP",
        "data_inicio": date(2026, 8, 1),
        "data_fim": date(2027, 2, 28),
        "profissionais": [
            ProfissionalInput(nome="Fernanda Costa", senioridade=Senioridade.GERENTE, horas_estimadas=200),
            ProfissionalInput(nome="Tiago Mendes", senioridade=Senioridade.SENIOR, horas_estimadas=600),
            ProfissionalInput(nome="Beatriz Rocha", senioridade=Senioridade.JUNIOR, horas_estimadas=800),
        ],
    },
    {
        "cliente": "Natura",
        "descricao": "Estruturação de Data Warehouse para Marketing",
        "data_inicio": date(2026, 5, 15),
        "data_fim": date(2026, 7, 15),
        "profissionais": [
            ProfissionalInput(nome="Juliana Gomes", senioridade=Senioridade.ESPECIALISTA, horas_estimadas=180),
            ProfissionalInput(nome="Ricardo Barros", senioridade=Senioridade.PLENO, horas_estimadas=240),
        ],
    },
    {
        "cliente": "WEG S.A.",
        "descricao": "Desenvolvimento de Portal B2B de Peças",
        "data_inicio": date(2026, 9, 1),
        "data_fim": date(2026, 11, 30),
        "profissionais": [
            ProfissionalInput(nome="Marcos Dias", senioridade=Senioridade.SENIOR, horas_estimadas=300),
            ProfissionalInput(nome="Camila Freitas", senioridade=Senioridade.JUNIOR, horas_estimadas=400),
        ],
    },
    {
        "cliente": "Vale",
        "descricao": "Automação e Integração de Sistemas de Logística",
        "data_inicio": date(2026, 6, 15),
        "data_fim": date(2026, 12, 15),
        "profissionais": [
            ProfissionalInput(nome="Eduardo Martins", senioridade=Senioridade.ESPECIALISTA, horas_estimadas=500),
            ProfissionalInput(nome="Sofia Cardoso", senioridade=Senioridade.SENIOR, horas_estimadas=450),
        ],
    },
    {
        "cliente": "Embraer",
        "descricao": "Modernização de Legado C++ para Python",
        "data_inicio": date(2026, 8, 10),
        "data_fim": date(2027, 4, 10),
        "profissionais": [
            ProfissionalInput(nome="Fernando Neves", senioridade=Senioridade.GERENTE, horas_estimadas=200),
            ProfissionalInput(nome="Luiza Moreira", senioridade=Senioridade.ESPECIALISTA, horas_estimadas=800),
        ],
    },
    {
        "cliente": "TOTVS",
        "descricao": "Integração de APIs de RH",
        "data_inicio": date(2026, 5, 20),
        "data_fim": date(2026, 6, 20),
        "profissionais": [
            ProfissionalInput(nome="Pedro Henrique", senioridade=Senioridade.PLENO, horas_estimadas=160),
            ProfissionalInput(nome="Alice Castro", senioridade=Senioridade.JUNIOR, horas_estimadas=160),
        ],
    },
    {
        "cliente": "Grupo Boticário",
        "descricao": "Nova Plataforma de E-commerce",
        "data_inicio": date(2026, 7, 10),
        "data_fim": date(2026, 11, 10),
        "profissionais": [
            ProfissionalInput(nome="Rafael Teixeira", senioridade=Senioridade.SENIOR, horas_estimadas=400),
            ProfissionalInput(nome="Bruna Faria", senioridade=Senioridade.PLENO, horas_estimadas=400),
            ProfissionalInput(nome="Gabriel Nunes", senioridade=Senioridade.JUNIOR, horas_estimadas=300),
        ],
    },
]


def seed():
    create_db_and_tables()

    with Session(engine) as session:
        for index, blueprint in enumerate(PROPOSTAS_SEED, start=1):
            calculo = calcular_proposta(blueprint["profissionais"])
            status_inicial = avaliar_status_por_margem(calculo.margem_bruta_pct)

            nova_proposta = Proposta(
                cliente=blueprint["cliente"],
                descricao=blueprint["descricao"],
                data_inicio=blueprint["data_inicio"],
                data_fim=blueprint["data_fim"],
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
            print(f"[{index}/10] {blueprint['cliente']} | {status_inicial.name} | Margem: {calculo.margem_bruta_pct:.2f}%")

    print("Seed concluído.")


if __name__ == "__main__":
    seed()