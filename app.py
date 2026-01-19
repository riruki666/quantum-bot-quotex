import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import base64

# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="QUANTUM ELITE + SOM", layout="wide")

# --- FUNÇÃO PARA TOCAR SOM ---
def play_sound():
    # Som de notificação curto em formato base64
    sound_file = "https://www.soundjay.com/buttons/sounds/button-3.mp3"
    html_string = f"""
        <audio autoplay>
            <source src="{sound_file}" type="audio/mp3">
        </audio>
    """
    st.components.v1.html(html_string, height=0)

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .main { background-color: #05070a; }
    .stMetric { background-color: #11141c; padding: 20px; border-radius: 15px; border: 1px solid #1e222d; }
    .signal-card { padding: 40px; border-radius: 20px; text-align: center; margin-bottom: 25px; }
    .buy { background: linear-gradient(135deg, #00c853 0%, #b2ff59 100%); color: #000; box-shadow: 0 10px 30px rgba(0,200,83,0.3); }
    .sell { background: linear-gradient(135deg, #d50000 0%, #ff5252 100%); color: #fff; box-shadow: 0 10px 30px rgba(213,0,0,0.3); }
    .wait { background-color: #11141c; color: #4e5566; border: 1px dashed #2d3341; }
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
    if preco <= bb.iloc[-1, 0] and rsi < 30: return 1
    if preco >= bb.iloc[-1, 2] and rsi > 70: return -1
    return 0

# --- LÓGICA DO APP ---
st.sidebar.title("💎 QUANTUM ELITE")
par = st.sidebar.selectbox("Escolha o Ativo:", ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X"])

df_m1 = buscar_dados(par, "1m")
df_m5 = buscar_dados(par, "5m")

if df_m1 is not None and df_m5 is not None:
    s1 = calcular_sinal(df_m1)
    s5 = calcular_sinal(df_m5)
    
    # Estado para controlar o som (tocar apenas na mudança)
    if 'last_signal' not in st.session_state:
        st.session_state.last_signal = 0

    # LÓGICA DE EXIBIÇÃO E SOM
    current_signal = 0
    if s1 == 1 and s5 == 1:
        st.markdown('<div class="signal-card buy"><h1>⬆️ COMPRAR AGORA</h1></div>', unsafe_allow_html=True)
        current_signal = 1
    elif s1 == -1 and s5 == -1:
        st.markdown('<div class="signal-card sell"><h1>⬇️ VENDER AGORA</h1></div>', unsafe_allow_html=True)
        current_signal = -1
    else:
        st.markdown('<div class="signal-card wait"><h1>⌛ AGUARDANDO</h1></div>', unsafe_allow_html=True)
        current_signal = 0

    # Tocar som se o sinal mudou para Compra ou Venda
    if current_signal != 0 and current_signal != st.session_state.last_signal:
        play_sound()
        st.session_state.last_signal = current_signal
    elif current_signal == 0:
        st.session_state.last_signal = 0

    # MÉTRICAS
    m1, m2, m3 = st.columns(3)
    m1.metric("Preço", f"{df_m1['Close'].iloc[-1]:.5f}")
    m2.metric("RSI", f"{ta.rsi(df_m1['Close'], length=14).iloc[-1]:.0f}%")
    m3.metric("Vela", f"{60 - datetime.now().second}s")

    # GRÁFICO
    fig = go.Figure(data=[go.Candlestick(x=df_m1.index, open=df_m1['Open'], high=df_m1['High'], low=df_m1['Low'], close=df_m1['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=350, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Conectando... Use BTC-USD no fim de semana.")

if st.button("🔄 ATUALIZAR AGORA", use_container_width=True):
    st.rerun()
