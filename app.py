import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO MOBILE ---
st.set_page_config(page_title="LS SNIPER MOBILE", page_icon="📱", layout="centered")

# --- CSS: OTIMIZAÇÃO PARA TELAS PEQUENAS ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    
    /* Título e Assinatura */
    .header-mobile {
        text-align: center; color: #00ff00; font-weight: 900;
        font-size: 28px; margin-top: -50px; text-shadow: 0 0 10px #00ff00;
    }
    .ls-tag {
        text-align: center; color: #ffcc00; font-size: 14px;
        margin-bottom: 20px; letter-spacing: 2px;
    }

    /* Cards de Sinal Mobile */
    .card-signal {
        padding: 30px 15px; border-radius: 20px; text-align: center;
        margin-bottom: 20px; border: 3px solid #fff;
    }
    .compra-bg { background: linear-gradient(180deg, #00c853, #004d40); }
    .venda-bg { background: linear-gradient(180deg, #d50000, #4a148c); }
    .neutro-bg { background: #111; border: 1px dashed #444; color: #888; }

    .btn-quotex-mobile {
        display: block; width: 100%; padding: 20px;
        background-color: #ffcc00; color: #000 !important;
        text-align: center; font-weight: 900; font-size: 20px;
        border-radius: 15px; text-decoration: none; margin-top: 15px;
    }
    
    .timer-text { font-size: 50px; font-weight: 900; display: block; }
    
    /* Esconder elementos desnecessários no mobile */
    [data-testid="stHeader"] {display: none;}
    </style>
    
    <div class="header-mobile">LS SNIPER AI</div>
    <div class="ls-tag">DEVELOPED BY LUCAS SILVA</div>
    """, unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
@st.cache_data(ttl=1)
def get_mobile_data(t):
    try:
        d = yf.download(t, period="1d", interval="1m", progress=False)
        if d.empty or len(d) < 30: return None
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d[['Open', 'High', 'Low', 'Close']].astype(float).dropna()
    except: return None

# --- SELEÇÃO DE ATIVO (FORMATO MOBILE) ---
ativos_ls = {
    "EUR/USD": "EURUSD=X", "USD/BRL": "BRL=X", "GBP/USD": "GBPUSD=X",
    "BTC/USD": "BTC-USD", "GOLD": "GC=F", "TESLA": "TSLA", "NVIDIA": "NVDA"
}

sel = st.selectbox("🎯 SELECIONE O ATIVO:", list(ativos_ls.keys()))

# --- ESTADOS ---
if 'sinal_ativo' not in st.session_state: st.session_state.sinal_ativo = None
if 'timer_ls' not in st.session_state: st.session_state.timer_ls = 0

# --- LÓGICA ---
df = get_mobile_data(ativos_ls[sel])
agora = time.time()

if df is not None:
    c = df['Close'].squeeze()
    rsi = ta.rsi(c, length=5).iloc[-1]
    bb = ta.bbands(c, length=20, std=2.0)
    last_p = c.iloc[-1]
    
    # Captura de Sinal
    if st.session_state.sinal_ativo is None:
        if last_p <= bb.iloc[-1, 0] and rsi < 30:
            st.session_state.sinal_ativo = {"tipo": "COMPRA ⬆️", "cor": "compra-bg"}
            st.session_state.timer_ls = agora + 15
        elif last_p >= bb.iloc[-1, 2] and rsi > 70:
            st.session_state.sinal_ativo = {"tipo": "VENDA ⬇️", "cor": "venda-bg"}
            st.session_state.timer_ls = agora + 15

    # Exibição do Sinal (Card Gigante para Mobile)
    if st.session_state.sinal_ativo:
        restante = int(st.session_state.timer_ls - agora)
        if restante > 0:
            s = st.session_state.sinal_ativo
            st.markdown(f"""
                <div class="card-signal {s['cor']}">
                    <span style="font-size:20px;">SINAL CONFIRMADO</span>
                    <h1 style="font-size:60px; margin:10px 0;">{s['tipo']}</h1>
                    <span class="timer-text">{restante}s</span>
                    <p>ENTRE AGORA NA QUOTEX</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
        else:
            st.session_state.sinal_ativo = None
            st.rerun()
    else:
        st.markdown(f"""
            <div class="card-signal neutro-bg">
                <h3>ANALISANDO MERCADO...</h3>
                <p>Aguardando oportunidade em {sel}</p>
                <small>RSI: {rsi:.1f}</small>
            </div>
        """, unsafe_allow_html=True)

    # Gráfico Simplificado para Mobile
    
    fig = go.Figure(data=[go.Candlestick(x=df.index[-20:], open=df['Open'][-20:], high=df['High'][-20:], low=df['Low'][-20:], close=df['Close'][-20:])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=300, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Botão de Ação Gigante
    st.markdown(f'<a href="https://qxbroker.com/pt/trade/{sel.replace("/","")}" class="btn-quotex-mobile">ABRIR QUOTEX</a>', unsafe_allow_html=True)

# Rodapé Fixo
st.markdown(f'<div style="text-align:center; color:#333; font-size:10px; margin-top:20px;">LS SYSTEM v5.0 MOBILE © 2026</div>', unsafe_allow_html=True)

time.sleep(1)
st.rerun()
