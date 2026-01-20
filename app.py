import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER AI - HYPER DRIVE", page_icon="⚡", layout="wide")

# --- CSS: DESIGN DE ALTA FREQUÊNCIA ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    .main-title {
        color: #ff0000; font-weight: 900; font-size: 55px;
        text-align: center; text-shadow: 0 0 25px #ff0000;
        margin-top: -60px;
    }
    .timer-final {
        font-size: 70px; font-weight: 900; text-align: center;
        color: #00ff00; background: #0a0a0a; border: 3px solid #00ff00;
        border-radius: 20px; padding: 10px; margin-bottom: 20px;
    }
    .card-compra {
        background: linear-gradient(90deg, #004400, #00ff00); color: black; 
        padding: 20px; border-radius: 12px; border: 2px solid #fff;
        text-align: center; font-weight: 900; font-size: 26px; margin-bottom: 10px;
    }
    .card-venda {
        background: linear-gradient(90deg, #440000, #ff0000); color: white; 
        padding: 20px; border-radius: 12px; border: 2px solid #fff;
        text-align: center; font-weight: 900; font-size: 26px; margin-bottom: 10px;
    }
    </style>
    <h1 class="main-title">STRANGER HYPER-DRIVE</h1>
    """, unsafe_allow_html=True)

# --- ATIVOS COM AGRESSIVIDADE TOTAL ---
ativos_config = {
    "USD/BRL": {"tick": "BRL=X", "std": 1.5, "rsi": 3},  # ULTRA AGRESSIVO
    "EUR/USD": {"tick": "EURUSD=X", "std": 1.5, "rsi": 3}, # ULTRA AGRESSIVO
    "OURO": {"tick": "GC=F", "std": 1.7, "rsi": 5},      # AGRESSIVO
    "FACEBOOK": {"tick": "META", "std": 2.0, "rsi": 7},   # PADRÃO
    "BITCOIN": {"tick": "BTC-USD", "std": 2.2, "rsi": 7}  # VOLÁTIL
}

def play_sound(tipo):
    if tipo == "compra":
        st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/super-mario-power-up.mp3"></audio>', unsafe_allow_html=True)
    else:
        st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/bell.mp3"></audio>', unsafe_allow_html=True)

@st.cache_data(ttl=1)
def get_data_fast(t):
    try:
        d = yf.download(t, period="1d", interval="1m", progress=False)
        if d.empty or len(d) < 20: return None
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d.astype(float).dropna()
    except: return None

# --- LAYOUT PRINCIPAL ---
col_L, col_R = st.columns([1.2, 2.8])

with col_L:
    sec = 60 - datetime.now().second
    st.markdown(f'<div class="timer-final">{sec:02d}s</div>', unsafe_allow_html=True)
    
    st.markdown("### 📡 RADAR DE ALTA FREQUÊNCIA")
    for nome, c in ativos_config.items():
        df = get_data_fast(c["tick"])
        if df is not None:
            try:
                cp = df['Close'].squeeze()
                rsi = ta.rsi(cp, length=c["rsi"]).iloc[-1]
                bb = ta.bbands(cp, length=20, std=c["std"])
                last = cp.iloc[-1]
                
                # GATILHOS FORÇADOS (MAIOR FREQUÊNCIA DE SINAIS)
                if rsi < 35 or last <= bb.iloc[-1, 0]:
                    st.markdown(f'<div class="card-compra">{nome}<br>ENTRAR COMPRA ⬆️</div>', unsafe_allow_html=True)
                    if sec > 58: play_sound("compra")
                elif rsi > 65 or last >= bb.iloc[-1, 2]:
                    st.markdown(f'<div class="card-venda">{nome}<br>ENTRAR VENDA ⬇️</div>', unsafe_allow_html=True)
                    if sec > 58: play_sound("venda")
                else:
                    st.write(f"🔎 {nome}: Monitorando brecha...")
            except: continue

with col_R:
    sel = st.selectbox("FOCO NO ATIVO:", list(ativos_config.keys()))
    df_v = get_data_fast(ativos_config[sel]["tick"])
    if df_v is not None:
        fig = go.Figure(data=[go.Candlestick(x=df_v.index, open=df_v['Open'], high=df_v['High'], low=df_v['Low'], close=df_v['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    st.link_button(f"🔥 ABRIR {sel} NA QUOTEX", f"https://qxbroker.com/pt/trade/{sel.replace('/','')}", use_container_width=True)

time.sleep(1)
st.rerun()
