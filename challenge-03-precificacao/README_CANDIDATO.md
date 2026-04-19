- **APROVADA** → margem bruta acima de 45%. Não pode voltar para PENDENTE sem evento explícito.
- **PENDENTE** → margem entre 40% e 45%. Requer aprovação manual com desconto hierárquico.
- **REPROVADA** → margem abaixo de 40%. Pode ser reeditada, mas não enviada ao cliente.

## Decisões de Arquitetura

### Stack: Python/FastAPI em vez de Node.js/TypeScript
O repositório sugeria Python como stack base. Optei por manter a sugestão para alinhar com o contexto de IA aplicada da HAT Thinking, onde Python é dominante. A familiaridade com TypeScript me ajudou a entender os tipos e schemas rapidamente.

### Decimal em vez de float para valores monetários
`float` usa representação binária de ponto flutuante, o que causa erros de arredondamento em operações financeiras. Exemplo concreto: `0.1 + 0.2 == 0.30000000000000004` em Python. Em um motor de precificação, esse erro acumulado em centenas de linhas de proposta pode resultar em margens calculadas incorretamente. `Decimal` usa aritmética de ponto fixo e garante precisão exata.

### Separação de models e schemas
`models.py` representa as tabelas do banco — incluem campos como `created_at`, `proposta_id`, e relacionamentos que não devem ser expostos diretamente na API. `schemas.py` representa os contratos de entrada e saída da API — o que o cliente envia e recebe. Essa separação segue o princípio de Single Responsibility e evita vazar detalhes de infraestrutura para o contrato público.

### Desconto em cascata com histórico imutável
Cada aplicação de desconto cria um registro `Aprovacao` no banco com quem aprovou, quanto desconto aplicou e quando. O total acumulado é sempre recalculado somando o histórico — nunca editando registros existentes. Isso garante auditabilidade completa e evita o bug clássico de sistemas de vendas onde o estado acumulado é perdido após uma atualização.

### Funções auxiliares `_build_proposta_output`, `_build_breakdown`, `_build_aprovacoes`
O SQLModel com SQLite retorna valores `Decimal` com precisão variável após persistência. Para garantir serialização consistente (`450.00` em vez de `450.0000000000`), centralizei a construção do output em funções auxiliares que aplicam `quantize(Decimal("0.01"))` em todos os campos financeiros. Isso elimina duplicação e garante consistência em todos os endpoints.

### Testes
- **Testes de unidade** (`test_precificacao`, `test_validacao`, `test_desconto`): testam a lógica de negócio pura, sem banco, sem HTTP.
- **Testes de integração** (`test_api`): testam os endpoints de ponta a ponta com banco SQLite em memória via `TestClient` do FastAPI.
- Cobertura final: **97.50%**.