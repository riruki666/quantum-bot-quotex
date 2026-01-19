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

# --- BUSCA DE DADOS COM LIMPEZA PROFUNDA ---
@st.cache_data(ttl=5)
def buscar_dados(ticker):
    try:
        # Baixa os dados limpando o formato do Yahoo Finance
        df = yf.download(ticker, period="1d", interval="1m", progress=False, threads=False)
        
        if df.empty: return None
        
        # Correção do Erro: Remove níveis extras de colunas (MultiIndex)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Força os nomes das colunas e converte para float para evitar AttributeError
        df = df[['Open', 'High', 'Low', 'Close']].copy()
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        return df.dropna()
    except Exception as e:
        return None

# --- LÓGICA DO APP ---
par = st.sidebar.selectbox("Ativo:", ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X"])
df = buscar_dados(par)

if df is not None and len(df) > 14:
    # Cálculos usando nomes de colunas limpos
    try:
        rsi_series = ta.rsi(df['Close'], length=14)
        rsi = float(rsi_series.iloc[-1])
        
        bb = ta.bbands(df['Close'], length=20, std=2.5)
        # Pega as bandas pela posição para não errar o nome da coluna
        banda_inf = float(bb.iloc[-1, 0]) 
        banda_sup = float(bb.iloc[-1, 2])
        
        preco = float(df['Close'].iloc[-1])
        
        sinal = 0
        if preco <= banda_inf and rsi < 30: sinal = 1 
        elif preco >= banda_sup and rsi > 70: sinal = -1

        # --- EXIBIÇÃO ---
        agora = datetime.now()
        segundos_restantes = 60 - agora.second
        
        if sinal == 1:
            st.markdown('<div class="signal-card buy"><h1>⬆️ COMPRAR AGORA</h1></div>', unsafe_allow_html=True)
        elif sinal == -1:
            st.markdown('<div class="signal-card sell"><h1>⬇️ VENDER AGORA</h1></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="signal-card wait"><h1>⌛ AGUARDANDO EXAUSTÃO</h1></div>', unsafe_allow_html=True)

        st.markdown(f'<div class="timer-text">{segundos_restantes}s</div>', unsafe_allow_html=True)

        if sinal != 0 and 2 <= segundos_restantes <= 8:
            st.markdown('<div class="entry-alert">⚠️ PREPARE SUA ENTRADA!</div>', unsafe_allow_html=True)
            play_sound()

        # Dashboard
        c1, c2 = st.columns(2)
        c1.metric("Preço", f"{preco:.5f}")
        c2.metric("Força RSI", f"{rsi:.0f}%")

        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=300, margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro no processamento técnico. Tente outro ativo.")
        
    # Auto-refresh
    time.sleep(1)
    st.rerun()
else:
    st.info("📡 Sincronizando dados... No final de semana, use BTC-USD.")
    time.sleep(2)
    st.rerun()
