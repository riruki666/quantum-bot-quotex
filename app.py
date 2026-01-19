import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER PROFITS - ASSERTIVO", page_icon="👹", layout="wide")

# --- CSS ALTA NITIDEZ ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    
    .main-title {
        color: #ff0000;
        font-weight: 900;
        font-size: 60px;
        text-align: center;
        text-shadow: 3px 3px 0px #ffffff;
        margin-top: -50px;
        letter-spacing: -2px;
    }

    .timer-display {
        font-size: 55px;
        font-weight: 900;
        text-align: center;
        padding: 10px;
        background: #111;
        border-radius: 15px;
        border: 2px solid #444;
        margin-bottom: 20px;
    }

    .signal-box {
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        font-size: 45px;
        font-weight: 900;
        border: 5px solid #fff;
        text-transform: uppercase;
    }

    /* Nitidez de Métricas */
    [data-testid="stMetricValue"] { font-size: 35px !important; font-weight: 900 !important; color: #fff !important; }
    [data-testid="stMetricLabel"] { font-size: 18px !important; color: #ccc !important; font-weight: bold !important; }

    /* Botão Quotex */
    .stButton>button {
        background: linear-gradient(90deg, #ff0000 0%, #8b0000 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 24px !important;
        border-radius: 10px !important;
        height: 70px !important;
        border: 2px solid #fff !important;
    }
    </style>
    <h1 class="main-title">STRANGER PROFITS</h1>
    <iframe src="https://www.youtube.com/embed/Av1DFgWLR0E?autoplay=1&loop=1&playlist=Av1DFgWLR0E" 
            width="0" height="0" frameborder="0" allow="autoplay"></iframe>
    """, unsafe_allow_html=True)

# --- MENU LATERAL: TODOS OS ATIVOS RESTAURADOS ---
st.sidebar.title("💎 SELECIONE O ATIVO")
cat = st.sidebar.radio("Mercado:", ["Ações", "Cripto", "Forex", "Commodities"])

ativos_full = {
    "Ações": {
        "NVIDIA": "NVDA", "Tesla": "TSLA", "Apple": "AAPL", "Amazon": "AMZN", 
        "Netflix": "NFLX", "Microsoft": "MSFT", "Disney": "DIS", "McDonalds": "MCD"
    },
    "Cripto": {
        "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD", 
        "XRP": "XRP-USD", "Cardano": "ADA-USD", "BNB": "BNB-USD"
    },
    "Forex": {
        "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", 
        "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "EUR/GBP": "EURGBP=X"
    },
    "Commodities": {
        "Ouro (Gold)": "GC=F", "Petróleo": "CL=F", "Prata": "SI=F", "Gás Natural": "NG=F"
    }
}

nome_ativo = st.sidebar.selectbox("Ativo:", list(ativos_full[cat].keys()))
ticker = ativos_full[cat][nome_ativo]

# --- CRONÔMETRO DE VELA ---
segundos_restantes = 60 - datetime.now().second
cor_t = "#00ff00" if segundos_restantes > 10 else "#ff0000"
st.markdown(f'<div class="timer-display" style="color:{cor_t};">⏳ FECHAMENTO: {segundos_restantes}s</div>', unsafe_allow_html=True)

# --- ANALISADOR ASSERTIVO ---
@st.cache_data(ttl=1)
def fetch_data(s):
    try:
        data = yf.download(s, period="1d", interval="1m", progress=False)
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        return data.dropna()
    except: return None

df = fetch_data(ticker)

if df is not None and len(df) > 30:
    # Indicadores
    rsi = ta.rsi(df['Close'], length=14).iloc[-1]
    bb = ta.bbands(df['Close'], length=20, std=2.5)
    ema9 = ta.ema(df['Close'], length=9).iloc[-1]
    ema21 = ta.ema(df['Close'], length=21).iloc[-1]
    preco = df['Close'].iloc[-1]
    
    # Gráfico Profissional
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400, paper_bgcolor='#000', plot_bgcolor='#000')
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("PREÇO", f"{preco:.4f}")
    c2.metric("RSI", f"{rsi:.1f}")
    c3.metric("TENDÊNCIA", "ALTA" if ema9 > ema21 else "BAIXA")

    # --- ESTRATÉGIA ASSERTIVA (CONFLUÊNCIA) ---
    # COMPRA: RSI < 30 + Preço abaixo da Banda Inferior + EMA9 virando para cima
    # VENDA: RSI > 70 + Preço acima da Banda Superior + EMA9 virando para baixo
    
    if rsi < 30 and preco <= bb.iloc[-1, 0]:
        st.markdown('<div class="signal-box" style="background:#2eb85c;">🚀 COMPRA (CALL) AGORA</div>', unsafe_allow_html=True)
        st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
    elif rsi > 70 and preco >= bb.iloc[-1, 2]:
        st.markdown('<div class="signal-box" style="background:#e55353;">🔥 VENDA (PUT) AGORA</div>', unsafe_allow_html=True)
        st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="signal-box" style="background:#111; color:#444; border-color:#222;">AGUARDANDO CONFLUÊNCIA...</div>', unsafe_allow_html=True)

    # LINK DIRETO QUOTEX
    ativo_link = ticker.replace("=X", "").replace("-USD", "").replace("=F", "")
    st.write("---")
    st.link_button(f"👉 OPERAR {nome_ativo} NA QUOTEX", f"https://qxbroker.com/pt/trade/{ativo_link}", use_container_width=True)

    time.sleep(1)
    st.rerun()
