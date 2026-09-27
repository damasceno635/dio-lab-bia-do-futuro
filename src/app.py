import json
import re
import unicodedata
import pandas as pd
import requests
import streamlit as st
from pathlib import Path

# --- Configurações ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "qwen2.5:0.5b"
DATA_DIR = Path(__file__).parent.parent / "data"

SYSTEM_PROMPT = """Você é o Fin, um educador financeiro amigável e didático.
Ensina conceitos de finanças pessoais com linguagem simples, como se explicasse para um amigo.
Nunca recomenda investimentos específicos.
Responda com no máximo 2 parágrafos curtos.
Nunca invente dados. Use apenas o contexto fornecido."""


# --- Utilidades ---
def normalizar(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    nfkd = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acento.lower().strip()


# --- Carregamento dos dados ---
@st.cache_data
def carregar_dados():
    perfil = json.loads((DATA_DIR / "perfil_investidor.json").read_text(encoding="utf-8"))
    produtos = json.loads((DATA_DIR / "produtos_financeiros.json").read_text(encoding="utf-8"))
    transacoes = pd.read_csv(DATA_DIR / "transacoes.csv")
    transacoes["valor"] = pd.to_numeric(transacoes["valor"], errors="coerce").fillna(0)
    return perfil, produtos, transacoes


def calcular_gastos_por_categoria(transacoes: pd.DataFrame) -> dict:
    if "tipo" in transacoes.columns:
        saidas = transacoes[transacoes["tipo"].str.lower() == "saida"]
    else:
        saidas = transacoes.copy()
    if "categoria" not in saidas.columns:
        return {}
    totais = saidas.groupby("categoria")["valor"].sum().round(2)
    return {normalizar(cat): float(val) for cat, val in totais.items()}


def montar_contexto(perfil, produtos, transacoes):
    gastos = calcular_gastos_por_categoria(transacoes)
    linhas_gastos = "\n".join(f"- {c}: R$ {v:.2f}" for c, v in sorted(gastos.items()))
    linhas_produtos = "\n".join(
        f"- {p.get('nome', '?')}: {p.get('descricao', '')}" for p in produtos
    )
    return f"""
Cliente: {perfil.get('nome', '?')} | Perfil: {perfil.get('perfil', '?')}
Gastos por categoria (saídas): {linhas_gastos}
Produtos disponíveis: {linhas_produtos}
"""


# ============================================================
# CLASSIFICADOR DE INTENÇÕES — retorna (intent, resposta|None)
# ============================================================
def classificar(pergunta: str, perfil, produtos, gastos):
    p = normalizar(pergunta)

    # 1) Dados sensíveis
    if any(t in p for t in ["senha", "outro cliente", "cliente x", "conta de outro", "cpf de outro"]):
        return "sensivel", (
            "Não tenho acesso a senhas nem a dados de outros clientes. "
            "Posso ajudar apenas com as suas próprias informações financeiras. Como posso ajudar?"
        )

    # 2) Fora do escopo
    if any(t in p for t in [
        "previsao do tempo", "clima", "vai chover", "temperatura",
        "politica", "presidente", "eleicao", "futebol",
        "receita de bolo", "piada", "conte uma historia",
    ]):
        return "fora_escopo", (
            "Sou especializado em educação financeira e não trato desse tipo de assunto. "
            "Posso ajudar com algo relacionado às suas finanças, como explicar um conceito, "
            "analisar seus gastos ou falar sobre produtos financeiros."
        )

    # 3) Recomendação de investimento
    if any(t in p for t in [
        "recomenda", "recomendacao", "onde investir", "onde devo investir",
        "melhor investimento", "o que investir", "me indique",
    ]):
        perfil_nome = perfil.get("perfil", "não informado")
        nomes = ", ".join(prod.get("nome", "?") for prod in produtos) or "nenhum produto cadastrado"
        return "recomendacao", (
            f"Eu não faço recomendações de investimento específicas — meu papel é educativo. "
            f"Mas posso explicar como funciona cada produto e ajudar você a decidir com base no seu perfil ({perfil_nome}). "
            f"Os produtos disponíveis são: {nomes}. Qual deles você quer entender melhor?"
        )

    # 4) Produto específico desconhecido
    m = re.search(r"\b(?:produto|investimento|fundo|acao|cdb|tesouro|titulo)\s+([a-z0-9]{2,})", p)
    if m:
        mencionado = m.group(1)
        nomes_norm = [normalizar(prod.get("nome", "")) for prod in produtos]
        if not any(mencionado in n or n in mencionado for n in nomes_norm):
            lista = ", ".join(prod.get("nome", "?") for prod in produtos) or "nenhum produto cadastrado"
            return "produto_desconhecido", (
                f"Não tenho informações sobre o produto '{mencionado.upper()}'. "
                f"Posso explicar sobre os produtos disponíveis na sua carteira: {lista}. "
                f"Qual deles você quer conhecer?"
            )

    # 5) Consulta de gasto por categoria
    gatilhos_gasto = ["quanto gastei", "quanto gasto", "gastei com", "gasto com", "quanto foi", "quanto gastei com"]
    if any(g in p for g in gatilhos_gasto):
        for cat_norm, valor in gastos.items():
            radical = cat_norm[:5] if len(cat_norm) >= 5 else cat_norm
            if radical and radical in p:
                return "consulta_gasto", (
                    f"Você gastou R$ {valor:.2f} com {cat_norm} nas transações registradas. "
                    f"Esse valor considera apenas saídas. Quer que eu explique como acompanhar melhor essa categoria?"
                )
        return "consulta_gasto_sem_categoria", (
            "Não identifiquei a categoria na sua pergunta. As categorias disponíveis são: "
            + ", ".join(sorted(gastos.keys()))
            + ". Sobre qual delas você quer saber?"
        )

    # 6) Fallback → LLM
    return "livre", None


# --- Chamada ao LLM (só para intenção 'livre') ---
def perguntar_stream(msg, contexto):
    prompt = f"{SYSTEM_PROMPT}\n\nCONTEXTO:\n{contexto}\n\nPergunta: {msg}"
    try:
        r = requests.post(OLLAMA_URL, json={
            "model": MODELO,
            "prompt": prompt,
            "stream": True,
            "keep_alive": "30m",
            "options": {
                "temperature": 0.2,
                "repeat_penalty": 1.3,
                "num_predict": 200,
            },
        }, stream=True, timeout=180)
        r.raise_for_status()
        for linha in r.iter_lines():
            if linha:
                try:
                    dados = json.loads(linha.decode("utf-8"))
                    if "response" in dados:
                        yield dados["response"]
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        yield f"Erro ao consultar o modelo: {e}"


# --- Interface ---
st.set_page_config(page_title="Fin - Educador Financeiro", page_icon="💰")
st.title("💰 Fin - Educador Financeiro")
st.caption("Pergunte sobre finanças pessoais. Eu explico, não recomendo.")

perfil, produtos, transacoes = carregar_dados()
contexto = montar_contexto(perfil, produtos, transacoes)
gastos = calcular_gastos_por_categoria(transacoes)

if "historico" not in st.session_state:
    st.session_state.historico = []

for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if pergunta := st.chat_input("Digite sua dúvida financeira..."):
    st.session_state.historico.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.write(pergunta)

    intent, resposta_fixa = classificar(pergunta, perfil, produtos, gastos)

    with st.chat_message("assistant"):
        if resposta_fixa is not None:
            # Resposta determinística, sem LLM
            st.write(resposta_fixa)
            st.session_state.historico.append({"role": "assistant", "content": resposta_fixa})
        else:
            # LLM só entra para perguntas educativas livres
            resposta = st.write_stream(perguntar_stream(pergunta, contexto))
            st.session_state.historico.append({"role": "assistant", "content": resposta})