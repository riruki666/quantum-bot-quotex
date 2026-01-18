import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="QUANTUM PRECISION", layout="wide")

@st.cache_data(ttl=10)
def buscar_dados(ticker, intervalo):
    try:
        df = yf.download(ticker, period="2d", interval=intervalo, progress=False, threads=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.columns = [str(col).capitalize() for col in df.columns]
        return df if not df.empty and len(df) > 30 else None
    except:
        return None

def calcular_precisao(df):
    if df is None: return 0, 50
    
    # Indicadores de Alta Precisão
    close = df['Close'].astype(float)
    rsi = ta.rsi(close, length=14).iloc[-1]
    bb = ta.bbands(close, length=20, std=2.5) # Aumentado para 2.5 para pegar extremos
    
    # Níveis de Suporte/Resistência de Preço (Price Action)
    sup = df['Low'].rolling(window=30).min().iloc[-1]
    res = df['High'].rolling(window=30).max().iloc[-1]
    preco_atual = close.iloc[-1]
    
    # Score de Confiança (0 a 100)
    score = 0
    tendencia = 0 # 1 para Call, -1 para Put
    
    # LÓGICA DE COMPRA (CALL) - FILTROS RÍGIDOS
    if preco_atual <= bb.iloc[-1, 0] or preco_atual <= sup:
        score += 40
        if rsi <= 30: score += 40
        if rsi <= 20: score += 20 # Exaustão Extrema
        tendencia = 1

    # LÓGICA DE VENDA (PUT) - FILTROS RÍGIDOS
    elif preco_atual >= bb.iloc[-1, 2] or preco_atual >= res:
        score += 40
        if rsi >= 70: score += 40
        if rsi >= 80: score += 20 # Exaustão Extrema
        tendencia = -1
        
    return tendencia, score, rsi

# --- UI ---
st.title("🎯 Quantum Precision - Filtro de Exaustão")
par = st.sidebar.selectbox("Ativo:", ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X"])

df_m1 = buscar_dados(par, "1m")
df_m5 = buscar_dados(par, "5m")

if df_m1 is not None and df_m5 is not None:
    t1, s1, rsi1 = calcular_precisao(df_m1)
    t5, s5, _ = calcular_precisao(df_m5)
    
    # CONFLUÊNCIA M1 + M5 (O filtro de precisão)
    confianca_final = 0
    decisao = "AGUARDANDO EXAUSTÃO"
    cor = "#1e2130"
    
    if t1 == t5 and t1 != 0:
        confianca_final = (s1 + s5) / 2
        if confianca_final >= 80:
            decisao = "🔥 ENTRADA ALTAMENTE CONFIAVEL"
            cor = "#004d26" if t1 == 1 else "#4d0000"
        elif confianca_final >= 50:
            decisao = "⚠️ ENTRADA MODERADA"
            cor = "#856404"

    st.markdown(f"""<div style='background:{cor}; padding:30px; border-radius:15px; text-align:center; border: 2px solid white;'>
                <h1 style='color:white;'>{decisao}</h1>
                <h2 style='color:white;'>Confiança: {confianca_final:.0f}%</h2>
                </div>""", unsafe_allow_html=True)

    # Dashboard de Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("Preço Atual", f"{df_m1['Close'].iloc[-1]:.5f}")
    col2.metric("RSI M1", f"{rsi1:.2f}", delta="EXAUSTÃO" if rsi1 > 70 or rsi1 < 30 else None)
    col3.metric("Tempo M1", f"{60 - datetime.now().second}s")

    # Gráfico Visual
    fig = go.Figure(data=[go.Candlestick(x=df_m1.index, open=df_m1['Open'], high=df_m1['High'], low=df_m1['Low'], close=df_m1['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Conectando aos servidores de precisão... Selecione BTC-USD para teste imediato.")

if st.button("REESCANEAR MERCADO"):
    st.rerun()
