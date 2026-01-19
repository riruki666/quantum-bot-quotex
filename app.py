import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER PROFITS ARCADE", page_icon="🕹️", layout="wide")

# --- ESTILO CSS PARA RÉPLICA DA IMAGEM ---
st.markdown("""
    <style>
    /* Fundo Dark Blue/Grey da imagem */
    .stApp {
        background-color: #1a1c24 !important;
    }
    
    /* Cabeçalho "STRANGER PROFITS ARCADE" */
    .header-banner {
        background-color: #000;
        padding: 15px;
        text-align: center;
        border-bottom: 4px solid #ff0000;
        margin: -60px -50px 20px -50px;
        position: relative;
    }
    .header-banner h1 {
        color: #ff0000 !important;
        font-family: 'Arial Black', sans-serif;
        font-size: 42px !important;
        letter-spacing: 2px;
        margin: 0;
        text-shadow: 2px 2px 0px #fff;
    }
    
    /* Personagens no Topo (Réplica da Imagem) */
    .char-line {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        margin-top: 5px;
    }
    .char-img { width: 45px; height: 45px; }
    .vecna-fire { width: 60px; filter: drop-shadow(0 0 10px #f00); }

    /* Estilo do Gráfico (Card) */
    .chart-container {
        background-color: #242731;
        border: 1px solid #363a45;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
    }

    /* Botões de Sinal (Buy/Sell) Idênticos à Imagem */
    .signal-wrapper {
        display: flex;
        justify-content: space-between;
        gap: 20px;
        margin-top: 15px;
    }
    .signal-card {
        flex: 1;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 3px solid;
    }
    .buy-card {
        background-color: #2eb85c;
        border-color: #1f7a3d;
        color: white;
        box-shadow: 0 0 15px rgba(46, 184, 92, 0.4);
    }
    .sell-card {
        background-color: #e55353;
        border-color: #a33b3b;
        color: white;
        box-shadow: 0 0 15px rgba(229, 83, 83, 0.4);
    }
    .signal-label { font-size: 14px; text-transform: uppercase; opacity: 0.9; }
    .signal-main { font-size: 28px; font-weight: bold; margin: 5px 0; }
    .signal-sub { font-size: 12px; font-family: monospace; }

    /* Sidebar Customizada */
    [data-testid="stSidebar"] {
        background-color: #14161b !important;
        border-right: 1px solid #363a45;
    }
    .st-emotion-cache-16ids93 { color: #8a919e !important; }
    </style>
    
    <div class="header-banner">
        <h1>STRANGER PROFITS</h1>
        <div class="char-line">
            <img class="char-img" src="https://img.icons8.com/color/96/stranger-things-eleven.png" style="transform: rotate(-20deg);">
            <img class="char-img" src="https://img.icons8.com/color/48/stranger-things-mike-wheeler.png">
            <img class="char-img" src="https://img.icons8.com/color/48/stranger-things-dustin.png">
            <img class="char-img" src="https://img.icons8.com/color/48/stranger-things-lucas-sinclair.png">
            <img class="char-img" src="https://img.icons8.com/color/48/stranger-things-will-byers.png">
            <img class="vecna-fire" src="https://img.icons8.com/color/96/horror.png">
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE BUSCA DE DADOS ---
@st.cache_data(ttl=5)
def buscar_dados(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(col).capitalize() for col in df.columns]
        return df.dropna()
    except: return None

# --- SIDEBAR (CONFORME A IMAGEM) ---
st.sidebar.markdown("<h2 style='color:white; font-size:20px;'>app.py</h2>", unsafe_allow_html=True)
st.sidebar.button("STRANGER PORTAL", use_container_width=True)

st.sidebar.markdown("<p style='color:#8a919e; margin-top:10px;'>Atives:</p>", unsafe_allow_html=True)
cat = st.sidebar.radio("", ["Ações", "Forex", "Commodities"])

ativos_dict = {
    "Ações": {"McDonald's, MCD": "MCD", "Coke": "KO", "NVIDIA": "NVDA"},
    "Forex": {"EUR/USD": "EURUSD=X", "GBP/JPY": "GBPJPY=X"},
    "Commodities": {"CL=F (Petróleo)": "CL=F"}
}

lista = ativos_dict[cat]
nome_exibicao = st.sidebar.selectbox("Selecione:", list(lista.keys()))
par_original = lista[nome_exibicao]

# --- PROCESSAMENTO PRINCIPAL ---
df = buscar_dados(par_original)

if df is not None and len(df) > 14:
    rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
    bb = ta.bbands(df['Close'], length=20, std=2.5)
    preco = float(df['Close'].iloc[-1])
    
    sinal = 0 # 0=Wait, 1=Buy, -1=Sell
    if preco <= bb.iloc[-1, 0] and rsi < 30: sinal = 1 
    elif preco >= bb.iloc[-1, 2] and rsi > 70: sinal = -1

    # Título do gráfico conforme a imagem
    st.markdown(f"<p style='color:white; font-size:16px;'>{nome_exibicao} (period 1d, interval 1m)</p>", unsafe_allow_html=True)
    
    # Gráfico dentro do Card
    with st.container():
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(
            template="plotly_dark", 
            xaxis_rangeslider_visible=False, 
            height=300,
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Painel de Sinais (BUY / SELL)
    c_buy, c_sell = st.columns(2)
    
    with c_buy:
        # Se sinal for 1, brilha mais; se não, fica padrão
        st.markdown(f"""
            <div class="signal-card buy-card">
                <div class="signal-label">— Signal —</div>
                <div class="signal-main">BUY</div>
                <div class="signal-sub">COPIPE FINAL</div>
                <div style="font-size:10px; margin-top:5px;">nome - {preco:.1f} - USD</div>
            </div>
            """, unsafe_allow_html=True)
            
    with c_sell:
        st.markdown(f"""
            <div class="signal-card sell-card">
                <div class="signal-label">— Signal —</div>
                <div class="signal-main">SELL</div>
                <div class="signal-sub">"FROCK" "HOO"</div>
                <div style="font-size:10px; margin-top:5px;">nome - {preco:.1f} - 700</div>
            </div>
            """, unsafe_allow_html=True)

    # Lógica de som e cópia automática no sinal
    if sinal != 0:
        # Copia o ativo para a Quotex
        ativo_limpo = par_original.replace("=X", "").replace("-USD", "").replace("=F", "")
        js_copy = f"""
        <script>
        navigator.clipboard.writeText("{ativo_limpo}");
        var audio = new Audio("https://www.myinstants.com/media/sounds/vecna-clock-sound-effect.mp3");
        audio.play();
        </script>
        """
        st.components.v1.html(js_copy, height=0)

    time.sleep(1)
    st.rerun()
