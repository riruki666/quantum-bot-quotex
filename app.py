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

    /* Fundo Escuro da Imagem */
    .stApp { background-color: #111217 !important; }

    /* Banner Superior */
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

    /* Animação dos Personagens Reais */
    .track {
        width: 100%; height: 100px; position: relative; overflow: hidden;
        background: rgba(0,0,0,0.5); border-radius: 10px;
    }
    .party {
        position: absolute; display: flex; gap: 30px; align-items: center;
        animation: walk 15s linear infinite; bottom: 5px;
    }
    .char { width: 70px; height: 90px; object-fit: contain; }

    @keyframes walk {
        from { left: -500px; }
        to { left: 100%; }
    }

    /* Cards de Gráfico */
    .chart-container {
        background-color: #1a1c24; border: 1px solid #363a45;
        border-radius: 12px; padding: 15px; margin: 10px 0;
    }

    /* Botões de Sinal Iguais à Foto */
    .sig-row { display: flex; gap: 20px; margin-top: 15px; }
    .sig-card {
        flex: 1; padding: 25px; border-radius: 15px; text-align: center;
        border: 2px solid #fff; font-family: 'Arial Black', sans-serif;
    }
    .buy { background-color: #2eb85c; color: white; box-shadow: 0 0 20px #2eb85c; }
    .sell { background-color: #e55353; color: white; box-shadow: 0 0 20px #e55353; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #0d0e12 !important; border-right: 1px solid #333; }
    </style>
    
    <div class="header-banner">
        <h1>STRANGER PROFITS</h1>
        <div class="track">
            <div class="party">
                <img class="char" src="https://www.pngplay.com/wp-content/uploads/12/Stranger-Things-Eleven-PNG-Clipart-Background.png">
                <img class="char" src="https://images.ctfassets.net/lp986m4p6pvl/5Yv1PzPZ9YQW8E8W8Y6W4W/d9f9c8f9f9f9f9f9f9f9f9f9f9f9f9f9/ST4_Mike_Poster.png" style="width:60px;">
                <img class="char" src="https://images.ctfassets.net/lp986m4p6pvl/2Yv1PzPZ9YQW8E8W8Y6W4W/d9f9c8f9f9f9f9f9f9f9f9f9f9f9f9f9/ST4_Dustin_Poster.png" style="width:60px;">
                <img class="char" src="https://images.ctfassets.net/lp986m4p6pvl/3Yv1PzPZ9YQW8E8W8Y6W4W/d9f9c8f9f9f9f9f9f9f9f9f9f9f9f9f9/ST4_Lucas_Poster.png" style="width:60px;">
                <span style="font-size:60px;">👹</span>
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

    # Métricas
    c1, c2, c3 = st.columns(3)
    c1.metric("Preço Atual", f"{preco:.2f}")
    c2.metric("Força RSI", f"{rsi:.1f}")
    c3.metric("Atualização", f"{datetime.now().second}s")

    # Sinais (Conforme a imagem)
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

    # Som de Alerta (Relógio do Vecna)
    if rsi < 30 or rsi > 70:
        st.markdown(f'<audio autoplay><source src="https://www.myinstants.com/media/sounds/vecna-clock-sound-effect.mp3"></audio>', unsafe_allow_html=True)

    time.sleep(1)
    st.rerun()
