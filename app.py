import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER AI - FINAL ELITE", page_icon="👹", layout="wide")

# --- CSS: ESTÉTICA DARK SNIPER ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    .main-title {
        color: #ff0000; font-weight: 900; font-size: 50px;
        text-align: center; text-shadow: 0 0 20px #ff0000;
        margin-top: -60px;
    }
    .timer-final {
        font-size: 65px; font-weight: 900; text-align: center;
        color: #00ff00; background: #0a0a0a; border: 3px solid #ff0000;
        border-radius: 20px; padding: 10px; margin-bottom: 20px;
    }
    .card-compra {
        background: #006400; color: white; padding: 15px;
        border-radius: 10px; border: 2px solid #00ff00;
        text-align: center; font-weight: 900; font-size: 22px;
    }
    .card-venda {
        background: #8b0000; color: white; padding: 15px;
        border-radius: 10px; border: 2px solid #ff0000;
        text-align: center; font-weight: 900; font-size: 22px;
    }
    </style>
    <h1 class="main-title">STRANGER SNIPER ELITE</h1>
    """, unsafe_allow_html=True)

# --- LISTA DE ATIVOS ---
ativos = {
    "EUR/USD": "EURUSD=X", "USD/BRL": "BRL=X", "FACEBOOK": "META",
    "APPLE": "AAPL", "BITCOIN": "BTC-USD", "OURO": "GC=F"
}

# --- FUNÇÃO DE ÁUDIO ---
def play_sound(tipo):
    if tipo == "compra":
        # Som de "Level Up" para Compra
        st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/super-mario-power-up.mp3"></audio>', unsafe_allow_html=True)
    else:
        # Som de "Sino de Alerta" para Venda
        st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/bell.mp3"></audio>', unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
@st.cache_data(ttl=1)
def get_data(t):
    try:
        d = yf.download(t, period="1d", interval="1m", progress=False)
        if d.empty: return None
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d.tail(40)
    except: return None

# --- LAYOUT ---
col_L, col_R = st.columns([1, 2.5])

with col_L:
    sec = 60 - datetime.now().second
    st.markdown(f'<div class="timer-final">{sec:02d}s</div>', unsafe_allow_html=True)
    
    st.markdown("### 📡 RADAR SNIPER")
    for nome, ticker in ativos.items():
        df = get_data(ticker)
        if df is not None:
            rsi = ta.rsi(df['Close'], length=7).iloc[-1]
            bb = ta.bbands(df['Close'], length=20, std=2.0)
            p = df['Close'].iloc[-1]
            
            # GATILHO COMPRA
            if rsi < 30 or p <= bb.iloc[-1, 0]:
                st.markdown(f'<div class="card-compra">{nome}<br>CALL (COMPRA)</div>', unsafe_allow_html=True)
                play_sound("compra")
            # GATILHO VENDA
            elif rsi > 70 or p >= bb.iloc[-1, 2]:
                st.markdown(f'<div class="card-venda">{nome}<br>PUT (VENDA)</div>', unsafe_allow_html=True)
                play_sound("venda")

with col_R:
    sel = st.selectbox("ATIVO EM FOCO:", list(ativos.keys()))
    df_f = get_data(ativos[sel])
    if df_f is not None:
        
        fig = go.Figure(data=[go.Candlestick(x=df_f.index, open=df_f['Open'], high=df_f['High'], low=df_f['Low'], close=df_f['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    st.link_button(f"🚀 EXECUTAR EM {sel}", f"https://qxbroker.com/pt/trade/{sel.replace('/','')}", use_container_width=True)

time.sleep(1)
st.rerun()
