import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER AI - OVERDRIVE", page_icon="⚡", layout="wide")

# --- CSS: ESTÉTICA HACKER / ALTA PERFORMANCE ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    .main-title {
        color: #ff0000; font-weight: 900; font-size: 55px;
        text-align: center; text-shadow: 0 0 20px #ff0000;
        margin-top: -60px;
    }
    .timer-display {
        font-size: 75px; font-weight: 900; text-align: center;
        color: #00ff00; background: #0a0a0a; border: 3px solid #ff0000;
        border-radius: 20px; padding: 10px; margin-bottom: 20px;
    }
    .signal-active {
        background: linear-gradient(90deg, #ff0000 0%, #330000 100%);
        padding: 30px; border-radius: 15px; text-align: center;
        font-size: 40px; font-weight: 900; border: 5px solid #fff;
        animation: blinker 1s linear infinite;
    }
    @keyframes blinker { 50% { opacity: 0.5; } }
    </style>
    <h1 class="main-title">STRANGER OVERDRIVE AI</h1>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÃO DE ATIVOS (VELOCIDADE MÁXIMA) ---
ativos_monitor = {
    "EUR/USD": "EURUSD=X",
    "USD/BRL": "BRL=X",
    "BTC/USD": "BTC-USD",
    "GOLD": "GC=F",
    "GBP/USD": "GBPUSD=X"
}

# --- MOTOR DE SCANNER AGRESSIVO ---
@st.cache_data(ttl=1)
def fetch_overdrive(ticker):
    try:
        d = yf.download(ticker, period="1d", interval="1m", progress=False)
        if d.empty: return None
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d.tail(25)
    except: return None

# --- SIDEBAR: GESTÃO E METAS ---
if 'profit' not in st.session_state: st.session_state.profit = 0.0

with st.sidebar:
    st.header("⚡ CONTROLE SNIPER")
    banca_real = st.number_input("Banca Inicial (R$):", value=100.0)
    meta_lucro = st.number_input("Meta do Dia (R$):", value=25.0)
    
    st.metric("LUCRO ACUMULADO", f"R$ {st.session_state.profit:.2f}")
    if st.session_state.profit >= meta_lucro:
        st.success("🎯 META BATIDA! DESLIGUE O SISTEMA!")
    
    if st.button("RESETAR SESSÃO"): st.session_state.profit = 0.0

# --- INTERFACE DE COMANDO ---
col_radar, col_view = st.columns([1.2, 2.5])

with col_radar:
    # Timer Gigante para Entrada de Vela
    sec = 60 - datetime.now().second
    st.markdown(f'<div class="timer-display">{sec:02d}s</div>', unsafe_allow_html=True)
    
    st.markdown("### 📡 SCANNER AGRESSIVO")
    for nome, tick in ativos_monitor.items():
        df = fetch_overdrive(tick)
        if df is not None:
            # INDICADORES OVERDRIVE (MAIS SINAIS)
            rsi = ta.rsi(df['Close'], length=3).iloc[-1]
            bb = ta.bbands(df['Close'], length=20, std=2.7) # Reduzi de 3.0 para 2.7 para mais sinais
            last_p = df['Close'].iloc[-1]
            
            # GATILHOS
            if rsi < 15 and last_p <= bb.iloc[-1, 0]:
                st.markdown(f'<div class="signal-active" style="background:green; border-color:white;">{nome}<br>COMPRA!</div>', unsafe_allow_html=True)
                st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
            elif rsi > 85 and last_p >= bb.iloc[-1, 2]:
                st.markdown(f'<div class="signal-active">{nome}<br>VENDA!</div>', unsafe_allow_html=True)
                st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
            else:
                st.write(f"⚪ {nome}: Buscando brecha...")

with col_view:
    sel_target = st.selectbox("ATIVO NO GRÁFICO:", list(ativos_monitor.keys()))
    df_plot = fetch_overdrive(ativos_monitor[sel_target])
    
    if df_plot is not None:
        
        
        fig = go.Figure(data=[go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        # Gestão de Banca Instantânea
        win_btn, loss_btn = st.columns(2)
        if win_btn.button("✅ WIN (+87%)"): st.session_state.profit += (banca_real * 0.05) * 0.87
        if loss_btn.button("❌ LOSS (-100%)"): st.session_state.profit -= (banca_real * 0.05)
        
        st.link_button(f"🔥 ENTRAR EM {sel_target} NA QUOTEX", f"https://qxbroker.com/pt/trade/{sel_target.replace('/','')}", use_container_width=True)

time.sleep(1)
st.rerun()
