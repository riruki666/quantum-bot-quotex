import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER AI - SAFE MODE", page_icon="🛡️", layout="wide")

# --- CSS: ESTÉTICA DE SEGURANÇA ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    .main-title {
        color: #ff0000; font-weight: 900; font-size: 50px;
        text-align: center; text-shadow: 0 0 20px #ff0000;
        margin-top: -60px;
    }
    .safe-zone {
        padding: 15px; border-radius: 10px; text-align: center;
        background: #002200; border: 1px solid #00ff00; color: #00ff00;
        margin-bottom: 20px; font-weight: bold;
    }
    .risk-zone {
        padding: 15px; border-radius: 10px; text-align: center;
        background: #220000; border: 1px solid #ff0000; color: #ff0000;
        margin-bottom: 20px; font-weight: bold;
    }
    .card-oportunidade {
        background: #111; padding: 20px; border-radius: 15px;
        text-align: center; border: 3px solid #00ff00; margin-bottom: 15px;
    }
    </style>
    <h1 class="main-title">STRANGER SAFE-SNIPER</h1>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÃO ---
ativos_config = {
    "USD/BRL": {"tick": "BRL=X", "std": 1.5, "rsi": 3},
    "EUR/USD": {"tick": "EURUSD=X", "std": 1.5, "rsi": 3},
    "FACEBOOK": {"tick": "META", "std": 2.0, "rsi": 7}
}

@st.cache_data(ttl=1)
def get_data_safe(t):
    try:
        d = yf.download(t, period="1d", interval="1m", progress=False)
        if d.empty or len(d) < 30: return None
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d.astype(float).dropna()
    except: return None

# --- MOTOR DE ANÁLISE DE RISCO ---
def detectar_risco(df):
    # Calcula a Média Móvel de 50 períodos para ver a tendência macro
    sma50 = ta.sma(df['Close'], length=30)
    preco_atual = df['Close'].iloc[-1]
    distancia = abs(preco_atual - sma50.iloc[-1])
    
    # Se o preço está se afastando demais da média em linha reta, é zona de risco (Rompimento)
    # Calculamos a inclinação das últimas 5 velas
    diff = df['Close'].diff(5).iloc[-1]
    volatilidade = ta.atr(df['High'], df['Low'], df['Close'], length=14).iloc[-1]
    
    if abs(diff) > (volatilidade * 2.5): # Movimento muito brusco
        return True # RISCO ALTO
    return False # MERCADO TÉCNICO

# --- INTERFACE ---
col_L, col_R = st.columns([1.2, 2.8])

with col_L:
    st.markdown("### 📊 STATUS DO MERCADO")
    
    sel_ativo = st.selectbox("VERIFICAR ATIVO:", list(ativos_config.keys()))
    df = get_data_safe(ativos_config[sel_ativo]["tick"])
    
    if df is not None:
        esta_em_risco = detectar_risco(df)
        
        if esta_em_risco:
            st.markdown('<div class="risk-zone">⚠️ MERCADO EM TENDÊNCIA FORTE<br>ALERTA BLOQUEADO PARA SEGURANÇA</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="safe-zone">✅ MERCADO LATERALIZADO<br>ZONA SEGURA PARA RETRAÇÃO</div>', unsafe_allow_html=True)
            
            # --- LÓGICA DE SINAL (SÓ RODA SE NÃO TIVER EM RISCO) ---
            cp = df['Close'].squeeze()
            rsi = ta.rsi(cp, length=ativos_config[sel_ativo]["rsi"]).iloc[-1]
            bb = ta.bbands(cp, length=20, std=ativos_config[sel_ativo]["std"])
            last = cp.iloc[-1]
            
            if rsi < 35 or last <= bb.iloc[-1, 0]:
                st.markdown(f'<div class="card-oportunidade">🎯 SINAL DETECTADO<br>{sel_ativo}: COMPRA</div>', unsafe_allow_html=True)
                st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
            elif rsi > 65 or last >= bb.iloc[-1, 2]:
                st.markdown(f'<div class="card-oportunidade" style="border-color:red;">🎯 SINAL DETECTADO<br>{sel_ativo}: VENDA</div>', unsafe_allow_html=True)
                st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)

with col_R:
    if df is not None:
        
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        st.link_button(f"🔥 OPERAR {sel_ativo} NA QUOTEX", f"https://qxbroker.com/pt/trade/{sel_ativo.replace('/','')}", use_container_width=True)

time.sleep(1)
st.rerun()
