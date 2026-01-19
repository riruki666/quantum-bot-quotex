import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="QUANTUM ELITE TIMER", layout="wide")

def play_sound():
    sound_file = "https://www.soundjay.com/buttons/sounds/button-3.mp3"
    st.components.v1.html(f'<audio autoplay><source src="{sound_file}"></audio>', height=0)

# --- ESTILO ---
st.markdown("""
    <style>
    .main { background-color: #05070a; }
    .signal-card { padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 10px; }
    .buy { background: linear-gradient(135deg, #00c853 0%, #b2ff59 100%); color: #000; }
    .sell { background: linear-gradient(135deg, #d50000 0%, #ff5252 100%); color: #fff; }
    .wait { background-color: #11141c; color: #4e5566; border: 1px dashed #2d3341; }
    .timer-text { font-size: 50px; font-weight: bold; color: #ffffff; text-align: center; margin-top: -10px; }
    .entry-alert { color: #ffeb3b; font-weight: bold; text-align: center; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=5)
def buscar_dados(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, threads=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(col).capitalize() for col in df.columns]
        return df
    except: return None

# --- LÓGICA DE SINAL ---
par = st.sidebar.selectbox("Ativo:", ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X"])
df = buscar_dados(par)

if df is not None and not df.empty:
    # Cálculos básicos
    rsi = ta.rsi(df['Close'], length=14).iloc[-1]
    bb = ta.bbands(df['Close'], length=20, std=2.5)
    preco = df['Close'].iloc[-1]
    
    sinal = 0
    if preco <= bb.iloc[-1, 0] and rsi < 30: sinal = 1 # Compra
    elif preco >= bb.iloc[-1, 2] and rsi > 70: sinal = -1 # Venda

    # --- CRONÔMETRO DE VELA ---
    agora = datetime.now()
    segundos_restantes = 60 - agora.second
    
    # Exibição do Cartão de Sinal
    if sinal == 1:
        st.markdown('<div class="signal-card buy"><h1>⬆️ COMPRAR AGORA</h1></div>', unsafe_allow_html=True)
    elif sinal == -1:
        st.markdown('<div class="signal-card sell"><h1>⬇️ VENDER AGORA</h1></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="signal-card wait"><h1>⌛ AGUARDANDO EXAUSTÃO</h1></div>', unsafe_allow_html=True)

    # Exibição do Cronômetro Grande
    st.markdown(f'<div class="timer-text">{segundos_restantes}s</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#888;">Tempo para o fechamento da vela</p>', unsafe_allow_html=True)

    # ALERTA DE ENTRADA (O Pulo do Gato)
    if sinal != 0 and 2 <= segundos_restantes <= 7:
        st.markdown('<div class="entry-alert">⚠️ PREPARE SUA ENTRADA! CLIQUE EM 2 SEGUNDOS!</div>', unsafe_allow_html=True)
        if 'played' not in st.session_state or st.session_state.played != agora.minute:
            play_sound()
            st.session_state.played = agora.minute

    # Gráfico e Métricas
    c1, c2 = st.columns(2)
    c1.metric("Preço", f"{preco:.5f}")
    c2.metric("Força RSI", f"{rsi:.0f}%")

    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=300, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

    # Auto-refresh para o cronômetro rodar
    time.sleep(1)
    st.rerun()
