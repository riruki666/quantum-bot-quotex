import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="VECNA INFERNO ELITE", page_icon="👹", layout="wide")

# --- FUNÇÃO ATMOSFERA (MÚSICA, SOM E CÓPIA) ---
def injetar_atmosfera(nome_copiar, sinal_atual):
    sound_vecna = "https://www.myinstants.com/media/sounds/vecna-clock-sound-effect.mp3"
    # Trilha oficial de suspense
    musica_fundo = "https://www.youtube.com/embed/Av1DFgWLR0E?autoplay=1&loop=1&playlist=Av1DFgWLR0E"
    corretora_url = "https://qxbroker.com/pt/demo-trade"
    
    js_code = f"""
        <script>
        function executarAcao() {{
            const el = document.createElement('textarea');
            el.value = "{nome_copiar}";
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            var audio = new Audio("{sound_vecna}");
            audio.play();
            window.open("{corretora_url}", "_blank");
        }}
        </script>
        <iframe src="{musica_fundo}" width="0" height="0" frameborder="0" allow="autoplay"></iframe>
        <div onclick="executarAcao()" style="background: linear-gradient(135deg, #8b0000 0%, #ff4500 100%); color: white; padding: 25px; border-radius: 15px; text-align: center; cursor: pointer; font-weight: bold; border: 3px solid #fff; box-shadow: 0 0 30px #f00; margin-top: 20px; font-size: 20px; font-family: sans-serif;">
            ⚔️ DESFERIR GOLPE: COPIAR "{nome_copiar}" & ABRIR CORRETORA
        </div>
    """
    st.components.v1.html(js_code, height=180)

# --- ESTILO VISUAL RPG + FOGO + TEXTO CLARO ---
def carregar_estilo(sinal_atual):
    efeito_fogo = "border-top: 5px solid #300;"
    if sinal_atual == -1: # Venda
        efeito_fogo = "border-top: 15px solid #ff4500; box-shadow: inset 0 0 100px #ff0000;"
    elif sinal_atual == 1: # Compra
        efeito_fogo = "border-top: 15px solid #00ff00; box-shadow: inset 0 0 100px #003300;"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

        .stApp {{
            background-color: #000000 !important;
            {efeito_fogo}
        }}

        /* ANIMAÇÃO RPG STRANGER THINGS */
        .rpg-path {{ 
            width: 100%; height: 90px; position: relative; overflow: hidden; 
            background: rgba(15,0,0,0.9); border-bottom: 3px solid #ff0000; margin-bottom: 20px;
        }}
        .party-animation {{ 
            position: absolute; white-space: nowrap; 
            animation: walk 18s linear infinite; 
            display: flex; align-items: center; gap: 20px;
            bottom: 10px;
        }}
        .char {{ width: 50px; height: 50px; background-size: contain; background-repeat: no-repeat; }}
        .eleven {{ background-image: url('https://img.icons8.com/color/96/stranger-things-eleven.png'); }}
        .dustin {{ background-image: url('https://img.icons8.com/color/96/stranger-things-dustin.png'); }}
        .mike {{ background-image: url('https://img.icons8.com/color/96/stranger-things-mike-wheeler.png'); }}
        .vecna {{ background-image: url('https://img.icons8.com/color/96/horror.png'); margin-left: 60px; }}

        @keyframes walk {{ from {{ left: -600px; }} to {{ left: 100%; }} }}

        /* TEXTOS E INTERFACE */
        h1, h2, h3 {{ font-family: 'Press Start 2P', cursive; color: #ffffff !important; text-shadow: 3px 3px #ff0000; text-align: center; }}
        .stMetric div {{ color: #ffffff !important; font-family: 'Press Start 2P', cursive !important; font-size: 16px !important; }}
        label {{ color: #ffaaaa !important; font-weight: bold !important; text-transform: uppercase; }}
        
        .timer-text {{ 
            font-family: 'Press Start 2P', cursive; font-size: 60px; color: #ff0000; 
            text-align: center; text-shadow: 0 0 25px #f00; margin: 15px 0;
        }}

        .signal-card {{ padding: 30px; border-radius: 20px; text-align: center; border: 4px solid #500; background: #0a0a0a; }}
        .buy {{ background: #008800 !important; border-color: #00ff00 !important; box-shadow: 0 0 30px #0f0; }}
        .sell {{ background: #880000 !important; border-color: #ff4500 !important; box-shadow: 0 0 50px #ff4500; }}
        
        [data-testid="stSidebar"] {{ background-color: #050505 !important; border-right: 2px solid #ff0000; }}
        </style>

        <div class="rpg-path">
            <div class="party-animation">
                <div class="char eleven"></div>
                <div class="char dustin"></div>
                <div class="char mike"></div>
                <div style="color:white; font-family:'Press Start 2P'; font-size:10px;">ESTAMOS CHEGANDO...</div>
                <div class="char vecna"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- BUSCA DE DADOS ---
@st.cache_data(ttl=5)
def buscar_dados(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(col).capitalize() for col in df.columns]
        return df.dropna()
    except: return None

# --- MENU LATERAL (TODOS OS ATIVOS) ---
st.sidebar.title("👹 PORTAL VECNA")
cat = st.sidebar.radio("Dimensão:", ["Ações (STOCKS)", "Criptomoedas", "Forex (MOEDAS)", "Commodities"])

ativos_full = {
    "Ações (STOCKS)": {
        "NVIDIA": "NVDA", "McDonald's": "MCD", "Tesla": "TSLA", "Apple": "AAPL", 
        "Amazon": "AMZN", "Netflix": "NFLX", "Microsoft": "MSFT", "Disney": "DIS"
    },
    "Criptomoedas": {
        "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD", "XRP": "XRP-USD", "Cardano": "ADA-USD"
    },
    "Forex (MOEDAS)": {
        "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", "AUD/USD": "AUDUSD=X", "EUR/GBP": "EURGBP=X"
    },
    "Commodities": {
        "Ouro (Gold)": "GC=F", "Prata (Silver)": "SI=F", "Petróleo": "CL=F"
    }
}

lista = ativos_full[cat]
nome_exibicao = st.sidebar.selectbox("Escolha o Alvo:", list(lista.keys()))
par_original = lista[nome_exibicao]
nome_copiar = par_original.replace("-USD", "").replace("=X", "").replace("=F", "")

# --- PROCESSAMENTO DE SINAL ---
df = buscar_dados(par_original)
sinal, rsi, preco = 0, 0, 0

if df is not None and len(df) > 14:
    rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
    bb = ta.bbands(df['Close'], length=20, std=2.5)
    preco = float(df['Close'].iloc[-1])
    if preco <= bb.iloc[-1, 0] and rsi < 30: sinal = 1 
    elif preco >= bb.iloc[-1, 2] and rsi > 70: sinal = -1

carregar_estilo(sinal)

if df is not None:
    st.markdown(f"### MONITORANDO DIMENSÃO: {nome_exibicao}")
    
    if sinal != 0:
        classe = "buy" if sinal == 1 else "sell"
        texto = "⬆️ COMPRA (CALL)" if sinal == 1 else "🔥 VENDA (INFERNO) 🔥"
        st.markdown(f'<div class="signal-card {classe}"><h1>{texto}</h1></div>', unsafe_allow_html=True)
        injetar_atmosfera(nome_copiar, sinal)
    else:
        st.markdown('<div class="signal-card" style="border-color:#333;"><h3>⌛ BUSCANDO ENERGIA...</h3></div>', unsafe_allow_html=True)

    segundos = 60 - datetime.now().second
    st.markdown(f'<div class="timer-text">{segundos}s</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    c1.metric("PREÇO", f"{preco:.4f}")
    c2.metric("FORÇA RSI", f"{rsi:.0f}%")

    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400, 
                      paper_bgcolor='#000', plot_bgcolor='#000', margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)
    
    time.sleep(1)
    st.rerun()
else:
    st.info("Portal instável... Reconectando em 2 segundos.")
    time.sleep(2)
    st.rerun()
