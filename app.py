import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAÇÃO DA TELA ---
st.set_page_config(page_title="QUANTUM BOT - FACILITADO", layout="wide")

# --- ESTILO VISUAL (CORES FORTES PARA SINAIS) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #31333f; }
    .buy-box { background-color: #00ff00; color: black; padding: 30px; border-radius: 15px; text-align: center; font-weight: bold; }
    .sell-box { background-color: #ff0000; color: white; padding: 30px; border-radius: 15px; text-align: center; font-weight: bold; }
    .wait-box { background-color: #1e2130; color: #888; padding: 30px; border-radius: 15px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=10)
def buscar_dados(ticker, intervalo):
    try:
        df = yf.download(ticker, period="2d", interval=intervalo, progress=False, threads=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.columns = [str(col).capitalize() for col in df.columns]
        return df if not df.empty and len(df) > 30 else None
    except: return None

def calcular_sinal(df):
    if df is None: return 0, 50
    close = df['Close'].astype(float)
    rsi = ta.rsi(close, length=14).iloc[-1]
    bb = ta.bbands(close, length=20, std=2.5)
    
    preco_atual = close.iloc[-1]
    banda_inf = bb.iloc[-1, 0]
    banda_sup = bb.iloc[-1, 2]
    
    # Lógica Simplificada
    if preco_atual <= banda_inf and rsi < 30: return 1, rsi # COMPRA
    if preco_atual >= banda_sup and rsi > 70: return -1, rsi # VENDA
    return 0, rsi

# --- INTERFACE ---
st.title("🚀 Quantum Bot - Modo Iniciante")
st.write("Siga as instruções coloridas abaixo para operar na Quotex/IQ Option.")

par = st.sidebar.selectbox("ESCOLHA O PAR DE MOEDAS:", ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X"])
st.sidebar.divider()
st.sidebar.info("💡 DICA: Só entre quando o sinal estiver VERDE ou VERMELHO vibrante.")

df_m1 = buscar_dados(par, "1m")
df_m5 = buscar_dados(par, "5m")

if df_m1 is not None and df_m5 is not None:
    s1, rsi1 = calcular_sinal(df_m1)
    s5, _ = calcular_sinal(df_m5)
    
    # --- LOGICA DE DECISÃO VISUAL ---
    if s1 == 1 and s5 == 1:
        st.markdown("""<div class="buy-box"><h1>⬆️ COMPRE AGORA (CALL)</h1><p>Confluência detectada em M1 e M5!</p></div>""", unsafe_allow_html=True)
    elif s1 == -1 and s5 == -1:
        st.markdown("""<div class="sell-box"><h1>⬇️ VENDA AGORA (PUT)</h1><p>Confluência detectada em M1 e M5!</p></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="wait-box"><h1>⌛ AGUARDANDO SINAL...</h1><p>O mercado não está seguro para entrar agora.</p></div>""", unsafe_allow_html=True)

    # --- MÉTRICAS FACILITADAS ---
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Preço Atual", f"{df_m1['Close'].iloc[-1]:.5f}")
    
    # RSI traduzido para iniciante
    status_rsi = "Normal"
    if rsi1 > 70: status_rsi = "Muito Caro (Vender)"
    if rsi1 < 30: status_rsi = "Muito Barato (Comprar)"
    c2.metric("Estado do Preço", status_rsi)
    
    restante = 60 - datetime.now().second
    c3.metric("Tempo para Próxima Vela", f"{restante}s")

    # Gráfico limpo
    fig = go.Figure(data=[go.Candlestick(x=df_m1.index, open=df_m1['Open'], high=df_m1['High'], low=df_m1['Low'], close=df_m1['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ Carregando dados do mercado... (Se for fim de semana, selecione BTC-USD)")

if st.button("🔄 ATUALIZAR AGORA"):
    st.rerun()
