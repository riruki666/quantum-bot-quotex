import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER PROFITS", page_icon="👹", layout="wide")

# --- CSS: ESTILO BRASIL + PERSONAGENS REAIS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    .stApp { background-color: #111217 !important; }

    .header-banner {
        background: linear-gradient(180deg, #4b0000 0%, #000000 100%);
        padding: 20px;
        text-align: center;
        border-bottom: 4px solid #ff0000;
        margin: -60px -50px 20px -50px;
    }
    
    .header-banner h1 {
        color: #ff0000 !important;
        font-family: 'Arial Black', sans-serif;
        font-size: 42px !important;
        text-shadow: 2px 2px 0px #fff;
        margin-bottom: 10px;
    }

    /* Animação com links de imagens ultra-estáveis */
    .track {
        width: 100%; height: 110px; position: relative; overflow: hidden;
        background: rgba(255,0,0,0.05); border-radius: 10px;
    }
    .party {
        position: absolute; display: flex; gap: 35px; align-items: center;
        animation: walk 18s linear infinite; bottom: 5px;
    }
    .char { width: 75px; height: 100px; object-fit: contain; filter: drop-shadow(0 0 5px #fff); }

    @keyframes walk {
        from { left: -600px; }
        to { left: 100%; }
    }

    .chart-container {
        background-color: #1a1c24; border: 1px solid #363a45;
        border-radius: 12px; padding: 15px; margin: 10px 0;
    }

    .sig-row { display: flex; gap: 20px; margin-top: 15px; }
    .sig-card {
        flex: 1; padding: 25px; border-radius: 15px; text-align: center;
        border: 2px solid #fff; font-family: 'Arial Black', sans-serif;
    }
    .buy { background-color: #2eb85c; color: white; box-shadow: 0 0 20px #2eb85c; }
    .sell { background-color: #e55353; color: white; box-shadow: 0 0 20px #e55353; }
    
    [data-testid="stSidebar"] { background-color: #0d0e12 !important; border-right: 1px solid #333; }
    </style>
    
    <div class="header-banner">
        <h1>STRANGER PROFITS</h1>
        <div class="track">
            <div class="party">
                <img class="char" src="https://www.nicepng.com/png/full/258-2581699_stranger-things-eleven-png.png">
                <img class="char" src="https://www.nicepng.com/png/full/966-9665672_mike-wheeler-stranger-things.png">
                <img class="char" src="https://www.nicepng.com/png/full/966-9665768_dustin-henderson-stranger-things.png">
                <img class="char" src="https://www.nicepng.com/png/full/966-9666014_lucas-sinclair-stranger-things.png">
                <span style="font-size:70px;">👹</span>
            </div>
        </div>
    </div>
    
    <iframe src="https://www.youtube.com/embed/Av1DFgWLR0E?autoplay=1&loop=1&playlist=Av1DFgWLR0E" 
            width="0" height="0" frameborder="0" allow="autoplay"></iframe>
    """, unsafe_allow_html=True)

# --- LISTA DE ATIVOS ---
st.sidebar.markdown("<h2 style='color:white;'>PORTAL VECNA</h2>", unsafe_allow_html=True)
categoria = st.sidebar.radio("Ativos:", ["Ações", "Cripto", "Forex", "Commodities"])

ativos = {
    "Ações": {"NVIDIA": "NVDA", "McDonald's": "MCD", "Tesla": "TSLA", "Apple": "AAPL"},
    "Cripto": {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD"},
    "Forex": {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X"},
    "Commodities": {"Ouro": "GC=F", "Petróleo": "CL=F"}
}

ticker_nome = st.sidebar.selectbox("Selecione:", list(ativos[categoria].keys()))
ticker = ativos[categoria][ticker_nome]

# --- DADOS ---
@st.cache_data(ttl=5)
def load_data(s):
    try:
        data = yf.download(s, period="1d", interval="1m", progress=False)
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        return data.dropna()
    except: return None

df = load_data(ticker)

if df is not None:
    rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
    bb = ta.bbands(df['Close'], length=20, std=2.5)
    preco = float(df['Close'].iloc[-1])
    
    st.markdown(f"### 📈 Monitorando: {ticker_nome}")

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=350,
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Botões de Sinal
    st.markdown('<div class="sig-row">', unsafe_allow_html=True)
    col_buy, col_sell = st.columns(2)
    with col_buy:
        st.markdown(f"""<div class="sig-card buy">
            <div style="font-size:12px;">SINAL</div>
            <div style="font-size:30px;">COMPRA</div>
            <div style="font-size:14px;">GOLPE FINAL</div>
            </div>""", unsafe_allow_html=True)
    with col_sell:
        st.markdown(f"""<div class="sig-card sell">
            <div style="font-size:12px;">SINAL</div>
            <div style="font-size:30px;">VENDA</div>
            <div style="font-size:14px;">QUEIMAR VECNA</div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Som de Alerta
    if rsi < 35 or rsi > 65:
        st.markdown(f'<audio autoplay><source src="https://www.myinstants.com/media/sounds/vecna-clock-sound-effect.mp3"></audio>', unsafe_allow_html=True)

    time.sleep(1)
    st.rerun()
