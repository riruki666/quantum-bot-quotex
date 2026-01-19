import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="QUANTUM MULTI-ATIVOS", layout="wide")

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

# --- BUSCA DE DADOS ---
@st.cache_data(ttl=5)
def buscar_dados(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, threads=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[['Open', 'High', 'Low', 'Close']].copy()
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna()
    except: return None

# --- SIDEBAR COM TODOS OS ATIVOS ---
st.sidebar.title("💎 MENU DE ATIVOS")

# Organizado por categorias para facilitar
categoria = st.sidebar.radio("Filtrar por:", ["Forex (Moedas)", "Criptomoedas", "Commodities"])

if categoria == "Forex (Moedas)":
    lista_ativos = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "JPY=X",
        "AUD/USD": "AUDUSD=X",
        "USD/CAD": "CAD=X",
        "EUR/GBP": "EURGBP=X"
    }
elif categoria == "Criptomoedas":
    lista_ativos = {
        "Bitcoin": "BTC-USD",
        "Ethereum": "ETH-USD",
        "Solana": "SOL-USD",
        "Binance Coin": "BNB-USD",
        "Ripple (XRP)": "XRP-USD"
    }
else: # Commodities
    lista_ativos = {
        "Ouro (Gold)": "GC=F",
        "Prata (Silver)": "SI=F",
        "Petróleo (Oil)": "CL=F"
    }

nome_exibicao = st.sidebar.selectbox("Selecione o Ativo:", list(lista_ativos.keys()))
par = lista_ativos[nome_exibicao]

# --- LÓGICA DO SINAL ---
df = buscar_dados(par)

if df is not None and len(df) > 14:
    try:
        rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
        bb = ta.bbands(df['Close'], length=20, std=2.5)
        banda_inf, banda_sup = float(bb.iloc[-1, 0]), float(bb.iloc[-1, 2])
        preco = float(df['Close'].iloc[-1])
        
        sinal = 0
        if preco <= banda_inf and rsi < 30: sinal = 1 
        elif preco >= banda_sup and rsi > 70: sinal = -1

        # --- INTERFACE ---
        st.subheader(f"Analisando: {nome_exibicao}")
        
        segundos_restantes = 60 - datetime.now().second
        
        if sinal == 1:
            st.markdown('<div class="signal-card buy"><h1>⬆️ COMPRAR AGORA (CALL)</h1></div>', unsafe_allow_html=True)
        elif sinal == -1:
            st.markdown('<div class="signal-card sell"><h1>⬇️ VENDER AGORA (PUT)</h1></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="signal-card wait"><h1>⌛ AGUARDANDO EXAUSTÃO</h1></div>', unsafe_allow_html=True)

        st.markdown(f'<div class="timer-text">{segundos_restantes}s</div>', unsafe_allow_html=True)

        if sinal != 0 and 2 <= segundos_restantes <= 8:
            st.markdown('<div class="entry-alert">⚠️ PREPARE SUA ENTRADA!</div>', unsafe_allow_html=True)
            play_sound()

        # Gráfico e Métricas
        c1, c2 = st.columns(2)
        c1.metric("Preço Atual", f"{preco:.5f}")
        c2.metric("Força RSI", f"{rsi:.0f}%")

        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=350, margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True)
        
    except: st.error("Erro técnico no ativo selecionado.")
    
    time.sleep(1)
    st.rerun()
else:
    st.info(f"Sincronizando {nome_exibicao}... Verifique se o mercado está aberto.")
    time.sleep(2)
    st.rerun()
