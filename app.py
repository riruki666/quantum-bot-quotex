import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import numpy as np

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER AI - MASTER SR", page_icon="🎯", layout="wide")

# --- CSS: ESTILO PROFISSIONAL ---
st.markdown("""
    <style>
    .stApp { background-color: #050505 !important; }
    .main-title {
        color: #ffffff; font-weight: 900; font-size: 40px;
        text-align: center; text-shadow: 0 0 15px #00ff00;
        margin-top: -60px;
    }
    .signal-active {
        background: linear-gradient(135deg, #004400, #00ff00);
        color: black; padding: 20px; border-radius: 15px;
        text-align: center; font-weight: 800; font-size: 24px;
        border: 2px solid white; animation: pulse 1.5s infinite;
    }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
    </style>
    <h1 class="main-title">STRANGER MASTER: SUPORTE & RESISTÊNCIA</h1>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE DADOS ---
@st.cache_data(ttl=1)
def get_data_master(t):
    try:
        d = yf.download(t, period="1d", interval="1m", progress=False)
        if d.empty or len(d) < 60: return None
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d.astype(float).dropna()
    except: return None

# --- MOTOR DE SUPORTE E RESISTÊNCIA ---
def detectar_sr(df):
    # Encontra picos e vales locais
    highs = df['High'].rolling(window=15, center=True).max()
    lows = df['Low'].rolling(window=15, center=True).min()
    
    # Pega os 3 níveis mais fortes de suporte e resistência recentes
    resistencias = df[df['High'] == highs]['High'].unique()[-3:]
    suportes = df[df['Low'] == lows]['Low'].unique()[-3:]
    
    return suportes, resistencias

# --- LAYOUT ---
col_stats, col_chart = st.columns([1, 2.5])

with col_stats:
    st.markdown("### 📊 SCANNER DE ZONAS")
    ativos = {"USD/BRL": "BRL=X", "EUR/USD": "EURUSD=X", "OURO": "GC=F"}
    sel = st.selectbox("ATIVO:", list(ativos.keys()))
    
    df = get_data_master(ativos[sel])
    
    if df is not None:
        sup, res = detectar_sr(df)
        last_price = df['Close'].iloc[-1]
        
        # Exibe Níveis no Painel
        st.write(f"**Resistência Principal:** {max(res):.4f}" if len(res)>0 else "")
        st.write(f"**Suporte Principal:** {min(sup):.4f}" if len(sup)>0 else "")
        
        # Indicadores para confluência
        rsi = ta.rsi(df['Close'], length=5).iloc[-1]
        
        st.divider()
        
        # LOGICA DE SINAL POR TOQUE EM S/R
        # Compra: Preço perto do suporte + RSI baixo
        dist_sup = min([abs(last_price - s) for s in sup]) if len(sup)>0 else 999
        dist_res = min([abs(last_price - r) for r in res]) if len(res)>0 else 999
        
        if (dist_sup < (last_price * 0.0002) or rsi < 30):
            st.markdown(f'<div class="signal-active" style="background:green; color:white;">🔥 TOQUE NO SUPORTE<br>COMPRA (CALL)</div>', unsafe_allow_html=True)
            st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/super-mario-power-up.mp3"></audio>', unsafe_allow_html=True)
        
        elif (dist_res < (last_price * 0.0002) or rsi > 70):
            st.markdown(f'<div class="signal-active" style="background:red; color:white;">🔥 TOQUE NA RESISTÊNCIA<br>VENDA (PUT)</div>', unsafe_allow_html=True)
            st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/bell.mp3"></audio>', unsafe_allow_html=True)
        else:
            st.warning("Aguardando o preço tocar em uma zona de Suporte ou Resistência forte...")

with col_chart:
    if df is not None:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Preço")])
        
        # Desenha Linhas de Suporte (Verde) e Resistência (Vermelho) automaticamente
        for s in sup:
            fig.add_hline(y=s, line_dash="dash", line_color="#00ff00", annotation_text="SUPORTE")
        for r in res:
            fig.add_hline(y=r, line_dash="dash", line_color="#ff0000", annotation_text="RESISTÊNCIA")
            
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=550, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        st.link_button("🚀 ABRIR QUOTEX AGORA", f"https://qxbroker.com/pt/trade/{sel.replace('/','')}", use_container_width=True)

time.sleep(1)
st.rerun()
