import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER PROFITS - PORTAL", page_icon="👹", layout="wide")

# --- ESTILO VISUAL: TEMAS EM PORTUGUÊS E PERSONAGENS REAIS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    .stApp { background-color: #1a1c24 !important; }

    /* Banner Principal */
    .header-banner {
        background-color: #000;
        padding: 30px;
        text-align: center;
        border-bottom: 5px solid #ff0000;
        margin: -60px -50px 30px -50px;
        box-shadow: 0 10px 40px rgba(255,0,0,0.4);
    }
    
    .header-banner h1 {
        color: #ff0000 !important;
        font-family: 'Arial Black', sans-serif;
        font-size: 45px !important;
        margin: 0;
        text-shadow: 3px 3px 0px #fff;
    }

    /* TRILHA DOS PERSONAGENS REAIS */
    .rpg-track {
        width: 100%; height: 130px; position: relative; overflow: hidden;
        background: linear-gradient(to right, #000, #300, #000);
        margin-top: 15px; border-radius: 15px; border: 2px solid #500;
    }
    
    .party-walk {
        position: absolute; display: flex; gap: 45px; align-items: center;
        animation: moveParty 15s linear infinite;
        bottom: 5px;
    }

    /* Fotos dos Atores Reais (PNG) */
    .char-real {
        width: 90px; height: 110px; 
        object-fit: contain;
        filter: drop-shadow(0 0 10px rgba(255,255,255,0.3));
    }

    @keyframes moveParty {
        from { left: -600px; }
        to { left: 115%; }
    }

    /* Textos em Português */
    .section-title { color: #ffffff; font-size: 20px; font-weight: bold; margin-bottom: 15px; }
    
    .chart-card {
        background-color: #242731; border: 1px solid #363a45;
        border-radius: 15px; padding: 20px;
    }
    
    /* Botões de Sinal Estilizados */
    .sig-container { display: flex; gap: 20px; margin-top: 20px; }
    .sig-box {
        flex: 1; padding: 30px; border-radius: 20px; text-align: center;
        border: 4px solid #fff; font-family: 'Press Start 2P', cursive;
    }
    .buy-box { background: #2eb85c; color: white; box-shadow: 0 0 20px #2eb85c; }
    .sell-box { background: #e55353; color: white; box-shadow: 0 0 20px #e55353; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #14161b !important; border-right: 2px solid #ff0000; }
    </style>
    
    <div class="header-banner">
        <h1>STRANGER PROFITS</h1>
        <div class="rpg-track">
            <div class="party-walk">
                <img class="char-real" src="https://static.wikia.nocookie.net/strangerthings/images/c/cf/Eleven_-_ST4.png">
                <img class="char-real" src="https://static.wikia.nocookie.net/strangerthings/images/1/10/Mike_Wheeler_-_ST4.png">
                <img class="char-real" src="https://static.wikia.nocookie.net/strangerthings/images/2/2b/Dustin_Henderson_-_ST4.png">
                <img class="char-real" src="https://static.wikia.nocookie.net/strangerthings/images/4/4e/Lucas_Sinclair_-_ST4.png">
                <img class="char-real" src="https://static.wikia.nocookie.net/strangerthings/images/b/bd/Will_Byers_-_ST4.png">
                <img class="char-real" src="https://static.wikia.nocookie.net/strangerthings/images/e/ee/Vecna_-_Profile.png" style="width:110px; height:130px;">
            </div>
        </div>
    </div>
    
    <iframe src="https://www.youtube.com/embed/Av1DFgWLR0E?autoplay=1&loop=1&playlist=Av1DFgWLR0E" 
            width="0" height="0" frameborder="0" allow="autoplay"></iframe>
    """, unsafe_allow_html=True)

# --- MENU LATERAL EM PORTUGUÊS ---
st.sidebar.title("👹 PORTAL DO VECNA")
cat_pt = st.sidebar.radio("Selecione a Categoria:", ["Ações", "Criptomoedas", "Moedas (Forex)", "Commodities"])

ativos_dict = {
    "Ações": {"NVIDIA": "NVDA", "McDonald's": "MCD", "Tesla": "TSLA", "Apple": "AAPL"},
    "Criptomoedas": {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD"},
    "Moedas (Forex)": {"Euro / Dólar": "EURUSD=X", "Libra / Dólar": "GBPUSD=X", "Dólar / Iene": "JPY=X"},
    "Commodities": {"Petróleo": "CL=F", "Ouro": "GC=F", "Prata": "SI=F"}
}

escolha = st.sidebar.selectbox("Escolha o Ativo:", list(ativos_dict[cat_pt].keys()))
ticker = ativos_dict[cat_pt][escolha]

# --- BUSCA DE DADOS ---
@st.cache_data(ttl=5)
def carregar_dados(s):
    d = yf.download(s, period="1d", interval="1m", progress=False)
    if not d.empty:
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d.dropna()
    return None

df = carregar_dados(ticker)

if df is not None:
    rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
    bb = ta.bbands(df['Close'], length=20, std=2.5)
    preco_atual = float(df['Close'].iloc[-1])
    
    st.markdown(f"<div class='section-title'>Análise em Tempo Real: {escolha}</div>", unsafe_allow_html=True)

    # Gráfico no Card
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=350,
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Botões de Compra e Venda
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class="sig-box buy-box">
            <span style="font-size:12px;">SINAL</span><br>COMPRA<br>
            <span style="font-size:10px;">GOLPE FINAL: {preco_atual:.2f}</span>
            </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="sig-box sell-box">
            <span style="font-size:12px;">SINAL</span><br>VENDA<br>
            <span style="font-size:10px;">QUEIMAR VECNA: {preco_atual:.2f}</span>
            </div>""", unsafe_allow_html=True)

    # Lógica de Som (Relógio do Vecna)
    # Ativa se o preço tocar nas bandas ou RSI estiver extremo
    if (preco_atual <= bb.iloc[-1, 0] or rsi < 30) or (preco_atual >= bb.iloc[-1, 2] or rsi > 70):
        st.markdown(f'<audio autoplay><source src="https://www.myinstants.com/media/sounds/vecna-clock-sound-effect.mp3"></audio>', unsafe_allow_html=True)

    time.sleep(1)
    st.rerun()
