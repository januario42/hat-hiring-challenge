# Motor de Precificação de Propostas — HAT Challenge 03

## Como rodar o projeto

### Com Docker (recomendado)

```bash
docker-compose up --build
```

A API estará disponível em `http://localhost:8000`.
Documentação interativa em `http://localhost:8000/docs`.

### Sem Docker

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

pip install -e ".[dev]"
uvicorn main:app --reload
```

## Como popular o banco

```bash
python -m src.infra.seed
```

Insere 10 propostas realistas com profissionais de diferentes senioridades.

## Como rodar os testes

```bash
pytest src/tests/ -v
```

21 testes, cobertura de 97.50%.

## Fluxo de estados da proposta
