# 💰 Fin — Educador Financeiro Inteligente

Assistente virtual com IA generativa que **educa** sobre finanças pessoais usando os próprios dados do usuário como exemplo. Nunca recomenda investimentos — apenas explica, contextualiza e ajuda a pessoa a tomar decisões melhores.

> Projeto desenvolvido como parte do Lab **"Construa Seu Assistente Virtual Com Inteligência Artificial"** da [DIO](https://github.com/digitalinnovationone/dio-lab-bia-do-futuro).

---

## 📌 O Problema

Muitas pessoas começam a ganhar dinheiro mas não sabem se organizar financeiramente. Têm dúvidas simples ("quanto gastei esse mês?", "o que é CDI?", "onde investir?") mas não têm com quem conversar sem julgamento ou letras miúdas.

O Fin preenche essa lacuna com uma abordagem **educativa, segura e personalizada**.

---

## 🎯 O Que o Fin Faz

| Pergunta do usuário | Como o Fin responde |
|---|---|
| "Quanto gastei com alimentação?" | Valor exato calculado em **pandas** a partir do CSV |
| "Qual investimento você recomenda?" | Recusa educadamente e lista produtos disponíveis |
| "Qual a previsão do tempo?" | Informa que só trata de finanças |
| "Quanto rende o produto XYZ?" | Admite não ter a informação e oferece os produtos reais |
| "O que é CDI?" | Explica com **LLM** (pergunta educativa livre) |

---

## 🏗️ Arquitetura

```
Usuário → Streamlit → Classificador de Intenção (Python)
                          ├─ intenção determinística → Resposta fixa em Python
                          └─ intenção livre → LLM (Ollama) → Resposta
```

**Decisão de design central:** tudo que precisa ser **confiável** (cálculos, regras de compliance, bloqueios de segurança) é feito em **Python**. O LLM só é usado para perguntas educativas abertas, onde criatividade e linguagem natural agregam valor.

Essa arquitetura surgiu **depois de várias iterações**. A primeira versão deixava tudo para o LLM e falhava: calculava errado, recomendava investimentos, respondia sobre clima, inventava produtos. A lição: **prompt é orientação, não garantia**.

---

## 📂 Estrutura do Projeto

```
dio-lab-bia-do-futuro/
├── README.md                    # Este arquivo
├── requirements.txt             # Dependências
├── data/                        # Base de conhecimento
│   ├── transacoes.csv
│   ├── perfil_investidor.json
│   ├── produtos_financeiros.json
│   └── historico_atendimento.csv
├── docs/                        # Documentação do desafio
│   ├── 01-documentacao-agente.md
│   ├── 02-base-conhecimento.md
│   ├── 03-prompts.md
│   ├── 04-metricas.md
│   └── 05-pitch.md
└── src/
    └── app.py                   # Aplicação Streamlit
```

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.10+
- [Ollama](https://ollama.com/) instalado

### Passo a passo

```bash
# 1. Clonar o repositório
git clone https://github.com/damasceno635/dio-lab-bia-do-futuro.git
cd dio-lab-bia-do-futuro

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Instalar e iniciar o Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &

# 4. Baixar o modelo leve
ollama pull qwen2.5:0.5b

# 5. Rodar o app
streamlit run src/app.py
```

O Streamlit abrirá uma porta (geralmente 8501). No Codespaces, clique em **"Open in Browser"**.

---

## 🧪 Testes

Os 4 cenários abaixo foram validados:

| # | Pergunta | Comportamento esperado | Status |
|---|---|---|---|
| 1 | "Quanto gastei com alimentação?" | Valor exato do CSV, calculado em pandas | ✅ |
| 2 | "Qual investimento você recomenda?" | Recusa + lista de produtos | ✅ |
| 3 | "Qual a previsão do tempo?" | Informa que só trata de finanças | ✅ |
| 4 | "Quanto rende o produto XYZ?" | Admite não saber + lista produtos reais | ✅ |

Detalhes completos em [`docs/04-metricas.md`](docs/04-metricas.md).

---

## ⚠️ Limitações Conhecidas

- **Modelo pequeno:** `qwen2.5:0.5b` roda em Codespaces gratuitos, mas não segue instruções complexas de forma confiável. Por isso os guardrails em código.
- **Perguntas compostas** ("alimentação e transporte") não são suportadas — o classificador detecta uma categoria por vez.
- **Detecção por palavra-chave:** sinônimos não previstos podem escapar dos guardrails.
- **Sem persistência:** o histórico de conversa vive apenas na sessão.

---

## 📚 Aprendizados

1. **LLMs não são calculadoras.** Pedir para o modelo somar valores de um CSV gera erros. Cálculos vão em Python.
2. **Prompt não é garantia.** Modelos pequenos obedecem regras complexas de forma inconsistente. Regras críticas vão em código.
3. **Arquitetura híbrida é mais robusta** que "só LLM" ou "só código". Cada ferramenta no seu lugar.
4. **Documentar falhas é tão importante quanto documentar acertos.** O processo de iteração é o que dá valor ao projeto.

---

## 🔗 Links

- [Repositório base do desafio](https://github.com/digitalinnovationone/dio-lab-bia-do-futuro)
- [Repositório de exemplo (Edu)](https://github.com/falvojr/dio-lab-bia-do-futuro)
- [DIO Agent](https://github.com/digitalinnovationone/dio-agent)
- [Link Pitch](https://drive.google.com/file/d/1gcybnDl0PGq8422fq0FqN6qBrjprwRhe/view?usp=sharing)

---

## 👤 Autor

**Damasceno**
Projeto desenvolvido para o Lab "Construa Seu Assistente Virtual Com Inteligência Artificial" da DIO.
