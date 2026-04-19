from uuid import uuid4


PAYLOAD_BASE = {
    "cliente": "Empresa Teste",
    "descricao": "Projeto Teste",
    "data_inicio": "2025-01-01",
    "data_fim": "2025-06-01",
    "profissionais": [
        {"nome": "Ana", "senioridade": "SENIOR", "horas_estimadas": 320},
        {"nome": "Bruno", "senioridade": "PLENO", "horas_estimadas": 480},
        {"nome": "Carla", "senioridade": "JUNIOR", "horas_estimadas": 200},
    ],
}


def test_criar_proposta_retorna_200_e_status_aprovada(client):
    response = client.post("/propostas/", json=PAYLOAD_BASE)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "APROVADA"
    assert data["cliente"] == "Empresa Teste"
    assert len(data["breakdown"]) == 3


def test_obter_proposta_inexistente_retorna_404(client):
    response = client.get(f"/propostas/{uuid4()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Proposta não encontrada"


def test_aplicar_desconto_acima_do_limite_retorna_400(client):
    proposta_id = client.post("/propostas/", json=PAYLOAD_BASE).json()["id"]
    response = client.post(f"/propostas/{proposta_id}/aplicar-desconto", json={
        "aprovador": "João",
        "nivel": "EXECUTIVO_VENDAS",
        "desconto_pct": "99.00",
    })
    assert response.status_code == 400


def test_listar_propostas_retorna_lista(client):
    client.post("/propostas/", json=PAYLOAD_BASE)
    response = client.get("/propostas/")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_listar_propostas_com_filtro_status(client):
    client.post("/propostas/", json=PAYLOAD_BASE)
    response = client.get("/propostas/?status=APROVADA")
    assert response.status_code == 200
    assert all(p["status"] == "APROVADA" for p in response.json())


def test_listar_propostas_com_filtro_cliente(client):
    client.post("/propostas/", json=PAYLOAD_BASE)
    response = client.get("/propostas/?cliente=Empresa")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_obter_proposta_existente_retorna_200(client):
    proposta_id = client.post("/propostas/", json=PAYLOAD_BASE).json()["id"]
    response = client.get(f"/propostas/{proposta_id}")
    assert response.status_code == 200
    assert response.json()["id"] == proposta_id


def test_aplicar_desconto_valido_retorna_200(client):
    proposta_id = client.post("/propostas/", json=PAYLOAD_BASE).json()["id"]
    response = client.post(f"/propostas/{proposta_id}/aplicar-desconto", json={
        "aprovador": "João",
        "nivel": "EXECUTIVO_VENDAS",
        "desconto_pct": "5.00",
    })
    assert response.status_code == 200
    assert response.json()["desconto_aplicado"] == "5.00"