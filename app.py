import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="QUANTUM BOT PRO", layout="wide")

# --- CSS ---
st.markdown("<style>.stMetric {background-color: #1e2130; padding: 10px; border-radius: 10px;}</style>", unsafe_allow_html=True)

# --- FUNÇÃO DE BUSCA (BLINDADA) ---
@st.cache_data(ttl=15)
def buscar_dados(ticker, intervalo):
    try:
        df = yf.download(ticker, period="2d", interval=intervalo, progress=False, threads=False)
        
        # Limpeza de MultiIndex (Causa do KeyError)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        # Garante que as colunas sejam strings simples
        df.columns = [str(col).capitalize() for col in df.columns]
        
        if df.empty or len(df) < 20:
            return None
        return df
    except:
        return None

def analisar(df):
    if df is None: return 0, 50, 0, 0
    
    try:
        # Cálculo manual/seguro para evitar KeyError no pandas_ta
        close = df['Close']
        low = df['Low']
        high = df['High']
        
        rsi = ta.rsi(close, length=14).iloc[-1]
        bb = ta.bbands(close, length=20, std=2)
        
        # Nomes das colunas das bandas podem variar, pegamos pelo índice
        bb_inf = bb.iloc[:, 0].iloc[-1] # Banda Inferior
        bb_sup = bb.iloc[:, 2].iloc[-1] # Banda Superior
        
        sup = low.rolling(window=20).min().iloc[-1]
        res = high.rolling(window=20).max().iloc[-1]
        preco = close.iloc[-1]
        
        pontos = 0
        if (preco <= bb_inf or preco <= sup) and rsi < 35: pontos = 1
        elif (preco >= bb_sup or preco >= res) and rsi > 65: pontos = -1
        
        return pontos, rsi, sup, res
    except:
        return 0, 50, 0, 0

# --- INTERFACE ---
st.sidebar.title("🎮 Quantum Bot")
par = st.sidebar.selectbox("Ativo:", ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X"])

st.title("📊 Painel de Análise")

df_m1 = buscar_dados(par, "1m")
df_m5 = buscar_dados(par, "5m")

if df_m1 is not None and 'Close' in df_m1.columns:
    p_m1, rsi_val, sup_val, res_val = analisar(df_m1)
    p_m5, _, _, _ = analisar(df_m5)

    # Sinal
    sinal = "AGUARDANDO"
    cor = "#1e2130"
    if p_m1 == 1 and p_m5 == 1: sinal, cor = "🔥 COMPRA FORTE", "#004d26"
    if p_m1 == -1 and p_m5 == -1: sinal, cor = "❄️ VENDA FORTE", "#4d0000"

    st.markdown(f"<div style='background:{cor}; padding:20px; border-radius:10px; text-align:center;'><h1>{sinal}</h1></div>", unsafe_allow_html=True)

    # Gráfico simples
    fig = go.Figure(data=[go.Candlestick(x=df_m1.index, open=df_m1['Open'], high=df_m1['High'], low=df_m1['Low'], close=df_m1['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    col1.metric("RSI", f"{rsi_val:.2f}")
    col2.metric("Preço", f"{df_m1['Close'].iloc[-1]:.5f}")
else:
    st.warning("Aguardando dados... Se estiver no fim de semana, use BTC-USD.")

if st.button("Atualizar"):
    st.rerun()
