import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="QUANTUM ELITE", layout="wide")

# --- ESTILO VISUAL MINIMALISTA ---
st.markdown("""
    <style>
    .main { background-color: #05070a; }
    .stMetric { background-color: #11141c; padding: 20px; border-radius: 15px; border: 1px solid #1e222d; }
    .signal-card { padding: 40px; border-radius: 20px; text-align: center; margin-bottom: 25px; transition: 0.3s; }
    .buy { background: linear-gradient(135deg, #00c853 0%, #b2ff59 100%); color: #000; box-shadow: 0 10px 30px rgba(0,200,83,0.3); }
    .sell { background: linear-gradient(135deg, #d50000 0%, #ff5252 100%); color: #fff; box-shadow: 0 10px 30px rgba(213,0,0,0.3); }
    .wait { background-color: #11141c; color: #4e5566; border: 1px dashed #2d3341; }
    h1 { font-weight: 800 !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=10)
def buscar_dados(ticker, intervalo):
    try:
        df = yf.download(ticker, period="2d", interval=intervalo, progress=False, threads=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.columns = [str(col).capitalize() for col in df.columns]
        return df if not df.empty and len(df) > 25 else None
    except: return None

def calcular_sinal(df):
    if df is None: return 0
    close = df['Close'].astype(float)
    rsi = ta.rsi(close, length=14).iloc[-1]
    bb = ta.bbands(close, length=20, std=2.5)
    
    preco = close.iloc[-1]
    # 1 para Compra, -1 para Venda, 0 para Neutro
    if preco <= bb.iloc[-1, 0] and rsi < 30: return 1
    if preco >= bb.iloc[-1, 2] and rsi > 70: return -1
    return 0

# --- BARRA LATERAL ---
st.sidebar.title("💎 QUANTUM ELITE")
par = st.sidebar.selectbox("Escolha o Ativo:", ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X"])
st.sidebar.divider()
st.sidebar.caption("v2.0 - Interface Simplificada")

# --- CORPO PRINCIPAL ---
df_m1 = buscar_dados(par, "1m")
df_m5 = buscar_dados(par, "5m")

if df_m1 is not None and df_m5 is not None:
    s1 = calcular_sinal(df_m1)
    s5 = calcular_sinal(df_m5)
    
    # LÓGICA DE EXIBIÇÃO DO CARTÃO DE SINAL
    if s1 == 1 and s5 == 1:
        st.markdown('<div class="signal-card buy"><h1>⬆️ COMPRAR AGORA</h1><p>ALTA PROBABILIDADE DE SUBIDA</p></div>', unsafe_allow_html=True)
    elif s1 == -1 and s5 == -1:
        st.markdown('<div class="signal-card sell"><h1>⬇️ VENDER AGORA</h1><p>ALTA PROBABILIDADE DE QUEDA</p></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="signal-card wait"><h1>⌛ AGUARDANDO</h1><p>MERCADO SEM DIREÇÃO CLARA</p></div>', unsafe_allow_html=True)

    # MÉTRICAS EM LINHA
    m1, m2, m3 = st.columns(3)
    preco_formatado = f"{df_m1['Close'].iloc[-1]:.5f}" if "USD=" in par else f"{df_m1['Close'].iloc[-1]:.2f}"
    m1.metric("Preço", preco_formatado
