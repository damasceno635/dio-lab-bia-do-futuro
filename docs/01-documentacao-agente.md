# Documentação do Agente

## Caso de Uso

O **Fin** é um educador financeiro pessoal que ajuda pessoas a entenderem seus padrões de gastos e a diferença entre produtos financeiros, sem recomendar investimentos específicos. É voltado para quem está começando a organizar a vida financeira e precisa de explicações simples, sem julgamentos e sem jargões.

## Persona e Tom de Voz

O Fin é amigável, didático e paciente. Fala como um amigo que entende de finanças, usando linguagem simples e exemplos do próprio cliente. Nunca julga os gastos do usuário e sempre pergunta se ele entendeu antes de avançar.

## Arquitetura

A arquitetura evoluiu durante o desenvolvimento. A versão inicial era ingênua e falhava; a versão final moveu regras críticas para código.

**Versão inicial (falha):**
```
Usuário → Streamlit → LLM (Ollama) → Resposta
```
O LLM recebia os dados brutos e era instruído via prompt a calcular, recomendar não-recomendar, filtrar escopo. Resultado: respostas inconsistentes, cálculos errados, loops de repetição.

**Versão final (funcional):**
```
Usuário → Streamlit → Classificador de Intenção (Python)
                          ├─ intenção determinística → Resposta fixa em Python
                          └─ intenção livre → LLM (Ollama) → Resposta
```
As regras de negócio (cálculo de gastos, recusa de recomendação, bloqueio de fora-de-escopo, detecção de produto desconhecido) são executadas em Python. O LLM só é chamado para perguntas educativas abertas.

- **Streamlit:** interface de chat.
- **Classificador de intenção:** função Python que decide quem responde.
- **Pandas:** cálculos financeiros (nunca o LLM).
- **Ollama + `qwen2.5:0.5b`:** modelo leve para perguntas educativas livres.
- **Base de Conhecimento:** `perfil_investidor.json`, `transacoes.csv`, `produtos_financeiros.json`, `historico_atendimento.csv`.

## Segurança e Anti-Alucinação

Durante os testes, ficou claro que **prompt não é garantia**. O modelo pequeno obedecia às regras em ~70% das tentativas e falhava no restante. Por isso, a segurança do agente está em **código Python**, não no system prompt:

| Risco | Onde é tratado | Como |
|---|---|---|
| Cálculo financeiro errado | `calcular_gastos_por_categoria()` (pandas) | Totais pré-calculados, LLM não faz contas |
| Recomendar investimento | `classificar()` — intent `recomendacao` | Resposta fixa em Python |
| Responder fora do escopo | `classificar()` — intent `fora_escopo` | Lista de termos proibidos |
| Inventar produto | `classificar()` — intent `produto_desconhecido` | Comparação com lista real de produtos |
| Acessar dados sensíveis | `classificar()` — intent `sensivel` | Bloqueio por palavras-chave |

O system prompt ainda reforça essas regras como camada secundária, mas **não é a linha de defesa principal**.

## Escopo

**O que o Fin faz:**
- Explica conceitos de finanças pessoais (CDI, Selic, renda fixa, etc.) — via LLM.
- Informa gastos por categoria com valores exatos do CSV — via Python.
- Lista produtos financeiros disponíveis — via Python.
- Recusa educadamente recomendações de investimento — via Python.
- Redireciona perguntas fora de finanças — via Python.

**O que o Fin NÃO faz:**
- Não recomenda investimentos específicos.
- Não responde perguntas fora de finanças.
- Não acessa dados de outros clientes.
- Não promete rentabilidade.
- Não calcula valores por conta própria (sempre usa pandas).

## Limitações Conhecidas

- **Modelo pequeno:** `qwen2.5:0.5b` não segue instruções complexas de forma confiável. Se o projeto evoluir, migrar para um modelo 7B+ ou API paga reduziria a necessidade de tantos guardrails em código.
- **Perguntas compostas:** "quanto gastei com alimentação e transporte?" não é suportado — o classificador detecta apenas uma categoria.
- **Detecção por palavra-chave:** os guardrails usam listas fixas de termos. Sinônimos não previstos podem escapar.
- **Sem persistência:** o histórico de conversa vive apenas na sessão do Streamlit.