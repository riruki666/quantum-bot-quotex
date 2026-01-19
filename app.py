import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER PROFITS ARCADE", page_icon="🕹️", layout="wide")

# --- CSS: ANIMAÇÃO, ATIVOS E CORES ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    .stApp { background-color: #1a1c24 !important; }

    /* Cabeçalho FIXO com Personagens */
    .header-banner {
        background-color: #000;
        padding: 20px;
        text-align: center;
        border-bottom: 4px solid #ff0000;
        margin: -60px -50px 20px -50px;
    }
    .header-banner h1 {
        color: #ff0000 !important;
        font-family: 'Arial Black', sans-serif;
        font-size: 40px !important;
        margin: 0;
        text-shadow: 2px 2px 0px #fff;
    }

    /* ANIMAÇÃO DOS PERSONAGENS CORRENDO */
    .rpg-track {
        width: 100%; height: 60px; position: relative; overflow: hidden;
        background: rgba(255,0,0,0.1); margin-top: 10px;
    }
    .party-walk {
        position: absolute; display: flex; gap: 20px;
        animation: moveParty 12s linear infinite;
    }
    .char-sprite { width: 45px; height: 45px; }
    @keyframes moveParty {
        from { left: -300px; }
        to { left: 100%; }
    }

    /* Cards e Sinais */
    .chart-card {
        background-color: #242731; border: 1px solid #363a45;
        border-radius: 12px; padding: 15px;
    }
    .sig-btn {
        padding: 25px; border-radius: 15px; text-align: center; font-weight: bold;
    }
    .buy-btn { background: #2eb85c; border: 3px solid #1f7a3d; color: white; }
    .sell-btn { background: #e55353; border: 3px solid #a33b3b; color: white; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #14161b !important; }
    </style>
    
    <div class="header-banner">
        <h1>STRANGER PROFITS</h1>
        <div class="rpg-track">
            <div class="party-walk">
                <img class="char-sprite" src="https://img.icons8.com/color/96/stranger-things-eleven.png">
                <img class="char-sprite" src="https://img.icons8.com/color/96/stranger-things-mike-wheeler.png">
                <img class="char-sprite" src="https://img.icons8.com/color/96/stranger-things-dustin.png">
                <img class="char-sprite" src="https://img.icons8.com/color/96/stranger-things-lucas-sinclair.png">
                <span style="font-size:40px;">👹</span>
            </div>
        </div>
    </div>
    
    <iframe src="https://www.youtube.com/embed/Av1DFgWLR0E?autoplay=1&loop=1&playlist=Av1DFgWLR0E" 
            width="0" height="0" frameborder="0" allow="autoplay"></iframe>
    """, unsafe_allow_html=True)

# --- LISTA COMPLETA DE ATIVOS ---
st.sidebar.title("🕹️ MENU DE ATIVOS")
categoria = st.sidebar.radio("Escolha a Categoria:", ["Ações", "Criptos", "Forex", "Commodities"])

ativos_db = {
    "Ações": {"McDonald's": "MCD", "Coke": "KO", "NVIDIA": "NVDA", "Tesla": "TSLA", "Apple": "AAPL", "Amazon": "AMZN"},
    "Criptos": {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD", "XRP": "XRP-USD"},
    "Forex": {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", "GBP/JPY": "GBPJPY=X"},
    "Commodities": {"Petróleo (WTI)": "CL=F", "Ouro (Gold)": "GC=F", "Prata": "SI=F"}
}

lista_ativos = ativos_db[categoria]
escolha = st.sidebar.selectbox("Selecione o Ativo:", list(lista_ativos.keys()))
ticker = lista_ativos[escolha]

# --- BUSCA DE DADOS ---
@st.cache_data(ttl=5)
def get_data(symbol):
    data = yf.download(symbol, period="1d", interval="1m", progress=False)
    if not data.empty:
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        return data.dropna()
    return None

df = get_data(ticker)

if df is not None and len(df) > 20:
    rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
    bb = ta.bbands(df['Close'], length=20, std=2.5)
    preco = float(df['Close'].iloc[-1])
    
    # Lógica de Sinal
    sinal = 0
    if preco <= bb.iloc[-1, 0] and rsi < 35: sinal = 1
    elif preco >= bb.iloc[-1, 2] and rsi > 65: sinal = -1

    st.markdown(f"### 📊 {escolha} (Minuto a Minuto)")

    # Gráfico
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=350,
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Cards de Sinal
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="sig-btn buy-btn">
            <small>SIGNAL</small><br>BUY<br><span style='font-size:10px;'>COPIPE FINAL - {preco:.2f}</span>
            </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="sig-btn sell-btn">
            <small>SIGNAL</small><br>SELL<br><span style='font-size:10px;'>"FROCK" "HOO" - {preco:.2f}</span>
            </div>""", unsafe_allow_html=True)

    # Se houver sinal, toca o relógio do Vecna
    if sinal != 0:
        st.markdown(f'<audio autoplay><source src="https://www.myinstants.com/media/sounds/vecna-clock-sound-effect.mp3"></audio>', unsafe_allow_html=True)

    time.sleep(1)
    st.rerun()
