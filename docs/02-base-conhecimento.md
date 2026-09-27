# Base de Conhecimento

## Dados Utilizados

| Arquivo | Formato | Utilização no Agente | Quem processa |
|---------|---------|---------------------|---------------|
| `transacoes.csv` | CSV | Calcular gastos por categoria (apenas `tipo=saida`) | Python (pandas) |
| `perfil_investidor.json` | JSON | Contextualizar perfil e objetivo do cliente | Python (lê) + LLM (usa no texto) |
| `produtos_financeiros.json` | JSON | Listar produtos disponíveis e detectar produtos inexistentes | Python (compara) + LLM (explica) |
| `historico_atendimento.csv` | CSV | *(não utilizado na versão atual — ver "Adaptações")* | — |

> [!TIP]
> A separação "quem processa" é essencial. Dados que exigem exatidão (números) são processados em Python. Dados que exigem explicação textual (conceitos) vão para o LLM.

---

## Adaptações nos Dados

**Não modifiquei os arquivos originais**, mas precisei tratar duas particularidades do CSV:

1. **Coluna `tipo`:** o CSV tem transações de `entrada` (ex: salário) e `saida` (ex: aluguel). Só as `saida` entram no cálculo de gastos. Ignorar isso foi o primeiro bug do projeto — o agente somava o salário junto com os gastos.

2. **Nome das categorias:** os nomes no CSV não têm acento (ex: `alimentacao`, não `alimentação`). Criei uma função `normalizar()` que remove acentos e coloca em minúsculo para comparar a pergunta do usuário com as categorias do CSV sem erro.

O arquivo `historico_atendimento.csv` não foi usado na versão atual. Ele seria útil para contextualizar conversas anteriores, mas isso exigiria persistência de sessão, o que ficou fora do escopo do protótipo.

---

## Estratégia de Integração

### Como os dados são carregados?

Os arquivos são carregados uma vez no início da sessão com `pandas` e `json`, dentro de uma função decorada com `@st.cache_data` (para não recarregar a cada interação).

### Como os dados são usados?

**Em Python:**
- `transacoes.csv` → `calcular_gastos_por_categoria()` gera um dicionário `{categoria: total_gasto}`.
- `produtos_financeiros.json` → lista usada para detectar produtos inexistentes.
- `perfil_investidor.json` → lido para contexto.

**No LLM:**
- Um resumo compacto do contexto é injetado no prompt, mas o LLM **não é instruído a fazer contas** — apenas a usar os valores já calculados.
- O LLM também recebe a lista de produtos, mas apenas para explicar conceitos, não para inventar detalhes.

### O que mudou da versão inicial

Na primeira versão, o LLM recebia o CSV inteiro como texto e era instruído a somar. Isso gerou respostas erradas (ex: R$ 570 em vez de R$ 530) porque **LLMs não são calculadoras**. A solução foi pré-calcular tudo em pandas e entregar pronto.

---

## Exemplo de Contexto Montado

Contexto enviado ao LLM (compacto, só o que ele precisa):

```
Cliente: João Silva | Perfil: Moderado
Gastos por categoria (saídas):
- alimentacao: R$ 530.00
- moradia: R$ 1200.00
- transporte: R$ 200.00
- TOTAL: R$ 1930.00
Produtos disponíveis:
- CDB: Renda fixa, baixo risco, indicado para reserva de emergência.
- Tesouro Selic: Título público, liquidez diária, baixo risco.
- Fundo de Ações: Renda variável, alto risco, para longo prazo.
```

Observe que o **cálculo já vem feito**. O LLM só precisa formatar a resposta.

---

## Limitações dos Dados

- **Base pequena:** o CSV tem poucas dezenas de transações. Em produção, seria necessário lidar com milhares de linhas (paginação, agregações mensais, filtros por período).
- **Categorias fixas:** se o usuário perguntar por uma categoria que não existe no CSV, o agente responde com a lista de categorias disponíveis, mas não cria novas.
- **Produtos com descrição curta:** a `descricao` em `produtos_financeiros.json` é sucinta. Se o LLM tentar detalhar demais, pode inventar. Por isso, o agente foi instruído a apenas listar e explicar superficialmente.