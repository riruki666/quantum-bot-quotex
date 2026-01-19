import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER PROFITS PRO", page_icon="📈", layout="wide")

# --- CSS PARA NITIDEZ E UI ---
st.markdown("""
    <style>
    /* Fundo preto puro para contraste máximo */
    .stApp { background-color: #000000 !important; }
    
    /* Fontes Ultra Nítidas */
    h1, h2, h3, p, div, span {
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    .main-title {
        color: #ff0000;
        font-weight: 900;
        font-size: 55px;
        text-align: center;
        text-shadow: 3px 3px 0px #ffffff;
        margin-top: -40px;
        letter-spacing: -2px;
    }

    /* Timer Centralizado e Brilhante */
    .timer-display {
        font-size: 50px;
        font-weight: 900;
        color: #00ff00;
        text-align: center;
        text-shadow: 0 0 15px #00ff00;
        margin: 10px 0;
        background: #111;
        border-radius: 15px;
        border: 2px solid #333;
    }

    /* Cards de Métricas com bordas claras */
    [data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 16px !important;
        color: #aaaaaa !important;
        font-weight: 600 !important;
    }

    .signal-alert {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        font-size: 40px;
        font-weight: 900;
        border: 4px solid #fff;
    }

    /* Botão Quotex de Alta Visibilidade */
    .stButton>button {
        background: linear-gradient(90deg, #ff0000 0%, #8b0000 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 22px !important;
        border-radius: 50px !important;
        border: 2px solid #fff !important;
        height: 60px !important;
    }
    </style>
    
    <h1 class="main-title">STRANGER PROFITS</h1>
    
    <iframe src="https://www.youtube.com/embed/Av1DFgWLR0E?autoplay=1&loop=1&playlist=Av1DFgWLR0E" 
            width="0" height="0" frameborder="0" allow="autoplay"></iframe>
    """, unsafe_allow_html=True)

# --- MENU LATERAL ---
st.sidebar.title("💎 TERMINAL DE ATIVOS")
mercado = st.sidebar.radio("Mercado:", ["Ações", "Criptomoedas", "Forex", "Commodities"])

ativos_db = {
    "Ações": {"NVIDIA": "NVDA", "Tesla": "TSLA", "Apple": "AAPL", "Amazon": "AMZN", "McDonalds": "MCD"},
    "Criptomoedas": {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD"},
    "Forex": {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X"},
    "Commodities": {"Ouro": "GC=F", "Petróleo": "CL=F"}
}

nome_ativo = st.sidebar.selectbox("Ativo:", list(ativos_db[mercado].keys()))
ticker = ativos_db[mercado][nome_ativo]

# --- LÓGICA DO CRONÔMETRO DE VELA ---
agora = datetime.now()
segundos_restantes = 60 - agora.second
cor_timer = "#00ff00" if segundos_restantes > 10 else "#ff0000"
st.markdown(f'<div class="timer-display" style="color:{cor_timer}; text-shadow: 0 0 15px {cor_timer};">⏳ {segundos_restantes}s</div>', unsafe_allow_html=True)

# --- DADOS ---
@st.cache_data(ttl=1)
def get_live_data(s):
    try:
        data = yf.download(s, period="1d", interval="1m", progress=False)
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        return data.dropna()
    except: return None

df = get_live_data(ticker)

if df is not None and len(df) > 15:
    rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
    bb = ta.bbands(df['Close'], length=20, std=2.5)
    preco = float(df['Close'].iloc[-1])
    
    # Gráfico
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400,
                      paper_bgcolor='#000', plot_bgcolor='#000', margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

    # Painel Inferior
    c1, c2 = st.columns(2)
    c1.metric("VALOR ATUAL", f"{preco:.4f}")
    c2.metric("ÍNDICE RSI", f"{rsi:.1f}%")

    # SINAIS E SINO
    if rsi < 32:
        st.markdown('<div class="signal-alert" style="background:#2eb85c;">🔥 COMPRA (CALL) 🔥</div>', unsafe_allow_html=True)
        st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
    elif rsi > 68:
        st.markdown('<div class="signal-alert" style="background:#e55353;">🔥 VENDA (PUT) 🔥</div>', unsafe_allow_html=True)
        st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="signal-alert" style="background:#111; border-color:#333; color:#555;">AGUARDANDO SINAL...</div>', unsafe_allow_html=True)

    # --- LINK DIRETO PARA QUOTEX ---
    # Traduz o ticker para o padrão da corretora (Ex: EURUSD)
    ativo_clean = ticker.replace("=X", "").replace("-USD", "").replace("=F", "")
    url_final = f"https://qxbroker.com/pt/trade/{ativo_clean}"
    
    st.write("")
    st.link_button(f"🚀 OPERAR {nome_ativo} AGORA NA QUOTEX", url_final, use_container_width=True)

    time.sleep(1)
    st.rerun()
