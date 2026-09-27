# Pitch (3 minutos)

> [!TIP]
> Use slides simples de apoio. A gravação de tela do Fin respondendo às 4 perguntas de teste é o coração da demonstração.

## Roteiro Sugerido

### 1. O Problema (30 seg)

> Qual dor do cliente você resolve?

Muitas pessoas começam a ganhar o próprio dinheiro mas não sabem por onde começar a se organizar financeiramente. Elas têm dúvidas simples — "quanto gastei esse mês?", "o que é CDI?", "onde devo investir?" — mas não têm com quem conversar de forma acessível, sem julgamentos e sem letras miúdas. Os apps de banco mostram números, mas não educam. Os consultores cobram caro. E o ChatGPT responde qualquer coisa, inclusive o que não deveria.

O **Fin** resolve essa lacuna: é um educador financeiro pessoal, acessível e seguro, que explica conceitos usando os **próprios dados do usuário** como exemplo.

---

### 2. A Solução (1 min)

> Como seu agente resolve esse problema?

O Fin é um assistente virtual construído em **Streamlit + Ollama + Python**. Ele não é um chatbot genérico — é um agente com objetivo claro: **educar, nunca recomendar**.

A arquitetura dele tem uma decisão de design central que surgiu depois de várias iterações:

**O LLM não é a linha de defesa principal.**

Durante o desenvolvimento, descobri que um modelo pequeno (o `qwen2.5:0.5b` que roda gratuitamente em Codespaces) **não segue regras complexas de forma consistente**. Ele obedecia ao "nunca recomende investimentos" em ~70% das tentativas, calculava errado os valores do CSV, entrava em loop e inventava informações sobre produtos que não existem.

A solução foi mover **tudo que precisa ser confiável para código Python**:

- **Cálculo de gastos** → pandas, não LLM.
- **Recusa de recomendação** → regra fixa em Python.
- **Bloqueio de perguntas fora de escopo** → lista de termos proibidos.
- **Detecção de produto inexistente** → comparação com a lista real.
- **Proteção de dados sensíveis** → bloqueio por palavras-chave.

O LLM passou a ser usado **apenas para o que ele faz bem**: explicar conceitos educativos abertos, como "o que é CDI?" ou "como funciona renda fixa?".

---

### 3. Demonstração (1 min)

> Mostre o agente funcionando (pode ser gravação de tela)

A gravação mostra as 4 perguntas críticas sendo feitas ao Fin, todas respondendo **instantaneamente e de forma consistente**:

1. **"Quanto gastei com alimentação?"** → O Fin responde com o valor exato calculado pelo pandas a partir do `transacoes.csv` (somando apenas as saídas), sem inventar.

2. **"Qual investimento você recomenda para mim?"** → O Fin recusa educadamente: "Não faço recomendações de investimento específicas — meu papel é educativo", e lista os produtos disponíveis para o usuário escolher o que quer entender.

3. **"Qual a previsão do tempo?"** → Resposta imediata: "Sou especializado em educação financeira e não trato desse tipo de assunto."

4. **"Quanto rende o produto XYZ?"** → O Fin admite não ter essa informação e oferece a lista de produtos reais da carteira do cliente.

> 🔗 Link do vídeo: [inserir link aqui]

---

### 4. Diferencial e Impacto (30 seg)

> Por que essa solução é inovadora e qual é o impacto dela na sociedade?

O diferencial do Fin não é a IA generativa em si — é a **arquitetura híbrida** que reconhece o que o LLM faz bem e o que ele faz mal. Essa decisão é o que torna o agente **confiável** em um domínio sensível como finanças, onde uma resposta errada pode levar a uma decisão ruim.

O impacto é tornar a educação financeira **acessível, segura e personalizada** para quem não tem acesso a consultores. E a lição técnica — "regras críticas vão em código, não em prompt" — é aplicável a qualquer agente de IA em produção, não só neste projeto.

---

## Checklist do Pitch

- [x] Duração máxima de 3 minutos
- [x] Problema claramente definido
- [x] Solução demonstrada na prática
- [x] Diferencial explicado
- [x] Áudio e vídeo com boa qualidade

---

## Link do Vídeo

> Cole aqui o link do seu pitch (YouTube, Loom, Google Drive, etc.)

https://drive.google.com/file/d/1gcybnDl0PGq8422fq0FqN6qBrjprwRhe/view?usp=sharing
