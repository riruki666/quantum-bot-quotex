import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz
import requests
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="QUANTUM BOT - Alta Precisão", layout="wide")

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #31333f; }
    .status-box { padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px; border: 2px solid #31333f; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES CORE COM CACHE (PREVENÇÃO DE TRAVAMENTO) ---
@st.cache_data(ttl=10)
def buscar_dados_seguro(ticker, intervalo):
    try:
        # Busca 2 dias para garantir que o cálculo de indicadores tenha massa de dados
        dados = yf.download(ticker, period="2d", interval=intervalo, progress=False, threads=False)
        if dados.empty:
            return None
        return dados
    except:
        return None

def analisar_estatisticas(df):
    if df is None or len(df) < 20: return 0, 50, 0, 0
    
    # Cálculos Técnicos
    df['RSI'] = ta.rsi(df['Close'], length=14)
    bb = ta.bbands(df['Close'], length=20, std=2)
    
    rsi = df['RSI'].iloc[-1]
    preco = df['Close'].iloc[-1]
    sup = df['Low'].rolling(window=20).min().iloc[-1]
    res = df['High'].rolling(window=20).max().iloc[-1]
    
    # Lógica de Decisão
    pontos = 0
    if (preco <= bb['BBL_20_2.0'].iloc[-1] or preco <= sup) and rsi < 35:
        pontos = 1 # Compra
    elif (preco >= bb['BBU_20_2.0'].iloc[-1] or preco >= res) and rsi > 65:
        pontos = -1 # Venda
    
    return pontos, rsi, sup, res

# --- SIDEBAR E PLACAR ---
if 'wins' not in st.session_state: st.session_state.wins = 0
if 'losses' not in st.session_state: st.session_state.losses = 0

st.sidebar.title("🎮 Quantum Control")
par = st.sidebar.selectbox("Ativo:", ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X", "AUDUSD=X"])
st.sidebar.subheader(f"🏆 Placar: {st.session_state.wins}W - {st.session_state.losses}L")

col_w, col_l = st.sidebar.columns(2)
if col_w.button("✅ WIN"): st.session_state.wins += 1
if col_l.button("❌ LOSS"): st.session_state.losses += 1

# Timer de Vela
segundos_agora = datetime.now().second
restante = 60 - segundos_agora
st.sidebar.metric("Fechamento M1", f"{restante}s")

# --- INTERFACE PRINCIPAL ---
st.title("📊 QUANTUM BOT - Pro Analysis")

# Processamento de Dados
df_m1 = buscar_dados_seguro(par, "1m")
df_m5 = buscar_dados_seguro(par, "5m")

if df_m1 is not None and not df_m1.empty:
    p_m1, rsi_val, sup_val, res_val = analisar_estatisticas(df_m1)
    p_m5, _, _, _ = analisar_estatisticas(df_m5)

    # Lógica de Confluência (Sinal)
    sinal = "ANALISANDO MERCADO..."
    cor_box = "#1e2130"
    
    if p_m1 == 1 and p_m5 == 1:
        sinal, cor_box = "🔥 COMPRA FORTE (CALL)", "#004d26"
    elif p_m1 == -1 and p_m5 == -1:
        sinal, cor_box = "❄️ VENDA FORTE (PUT)", "#4d0000"

    st.markdown(f"""<div class="status-box" style="background-color: {cor_box};">
                <h1 style="color: white; margin:0;">{sinal}</h1></div>""", unsafe_allow_html=True)

    # Métricas e Gráfico
    m1, m2, m3 = st.columns(3)
    m1.metric("Preço Atual", f"{df_m1['Close'].iloc[-1]:.5f}")
    m2.metric("RSI (14)", f"{rsi_val:.2f}")
    m3.metric("Resistência", f"{res_val:.5f}")

    fig = go.Figure(data=[go.Candlestick(
        x=df_m1.index, open=df_m1['Open'], high=df_m1['High'],
        low=df_m1['Low'], close=df_m1['Close'], name="Candles"
    )])
    fig.add_hline(y=sup_val, line_color="green", line_dash="dash")
    fig.add_hline(y=res_val, line_color="red", line_dash="dash")
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=10, r=10, t=10, b=10), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("📡 Erro de conexão com o Yahoo Finance. O mercado pode estar fechado ou instável.")
    if st.button("Tentar Novamente"):
        st.rerun()

st.caption("Aviso: Dados oficiais de Forex param no final de semana. Use pares de Cripto (BTC/ETH) para testar no sábado/domingo.")
