# Motor de Precificação de Propostas — HAT Challenge 03

API REST para criação, validação e aprovação de propostas comerciais de Professional Services, com motor de precificação automático, máquina de estados e desconto em cascata com histórico de aprovações.

---

## Como rodar o projeto

### Com Docker (recomendado)

```bash
docker-compose up --build
```

- API: `http://localhost:8000`
- Documentação interativa: `http://localhost:8000/docs`

### Sem Docker

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
source .venv/bin/activate    # Linux/Mac

pip install -e ".[dev]"
uvicorn main:app --reload
```

---

## Como popular o banco

```bash
python -m src.infra.seed
```

Insere 10 propostas realistas com profissionais de diferentes senioridades e clientes como Itaú, Nubank, Embraer e Petrobras.

---

## Como rodar os testes

```bash
pytest src/tests/ -v
```

21 testes — cobertura de **97.50%**.

---

## Endpoints disponíveis

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/propostas` | Cria e valida uma proposta |
| `GET` | `/propostas` | Lista propostas com filtros opcionais |
| `GET` | `/propostas/{id}` | Detalhe de uma proposta |
| `POST` | `/propostas/{id}/aplicar-desconto` | Aplica desconto com validação hierárquica |
| `GET` | `/tabela-precos` | Retorna a tabela de preços vigente |

---

## Fluxo de estados da proposta

O status é definido automaticamente na criação com base na margem bruta calculada:

| Margem bruta | Status |
|---|---|
| Acima de 45% | `APROVADA` |
| Entre 40% e 45% | `PENDENTE` |
| Abaixo de 40% | `REPROVADA` |

**Regras de transição:**
- `APROVADA` → não pode voltar para `PENDENTE` sem evento explícito de rejeição
- `PENDENTE` → pode receber desconto hierárquico para ser aprovada manualmente
- `REPROVADA` → pode ser reeditada, mas nunca enviada ao cliente

---

## Decisões de Arquitetura

### Stack: Python/FastAPI
O repositório sugeria Python como stack base. Optei por manter para alinhar com o contexto de IA aplicada da HAT Thinking, onde Python é dominante. A familiaridade com TypeScript/Node.js me ajudou a entender os contratos de tipos e schemas rapidamente.

### `Decimal` em vez de `float` para valores monetários
`float` usa representação binária de ponto flutuante, causando erros de arredondamento. Exemplo: `0.1 + 0.2 == 0.30000000000000004` em Python. Em um motor de precificação, esse erro acumulado em centenas de linhas pode resultar em margens calculadas incorretamente. `Decimal` usa aritmética de ponto fixo e garante precisão exata.

### Separação de `models` e `schemas`
`models.py` representa as tabelas do banco — expõe campos internos como `proposta_id`, `created_at` e relacionamentos que não devem vazar para a API. `schemas.py` representa os contratos públicos de entrada e saída. Essa separação segue Single Responsibility e protege o contrato da API de mudanças internas no banco.

### Desconto em cascata com histórico imutável
Cada desconto aplicado cria um registro `Aprovacao` no banco — quem aprovou, quanto aplicou e quando. O total acumulado é sempre recalculado somando o histórico, nunca editando registros existentes. Isso garante auditabilidade completa e evita o bug clássico onde o estado acumulado é perdido após uma atualização.

### Funções auxiliares `_build_*` no router
O SQLModel com SQLite retorna `Decimal` com precisão variável após persistência (`450.0000000000` em vez de `450.00`). Centralizei a construção do output em funções auxiliares que aplicam `quantize(Decimal("0.01"))` em todos os campos financeiros, eliminando duplicação e garantindo consistência em todos os endpoints.

### Testes
- **Unidade** (`test_precificacao`, `test_validacao`, `test_desconto`): lógica de negócio pura, sem banco e sem HTTP
- **Integração** (`test_api`): endpoints de ponta a ponta com banco SQLite em memória via `TestClient`
- Cobertura final: **97.50%**
