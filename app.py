import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="VECNA INFERNO TRADER", page_icon="🔥", layout="wide")

# --- FUNÇÃO SOM, CÓPIA E REDIRECIONAMENTO ---
def acao_sinal(nome_copiar):
    sound_vecna = "https://www.myinstants.com/media/sounds/vecna-clock-sound-effect.mp3"
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
        <div onclick="executarAcao()" style="background: linear-gradient(135deg, #4b0000 0%, #ff0000 100%); color: white; padding: 25px; border-radius: 15px; text-align: center; cursor: pointer; font-weight: bold; border: 2px solid #fff; box-shadow: 0 0 40px #ff4500; margin-top: 20px; font-size: 22px; font-family: 'Creepster', cursive;">
            🔥 QUEIMAR O VECNA: COPIAR "{nome_copiar}" & ABRIR QUOTEX
        </div>
    """
    st.components.v1.html(js_code, height=160)

# --- ESTILO VISUAL INFERNAL + ANIMAÇÕES ---
def carregar_estilo(sinal_atual):
    efeito_fogo = ""
    # Se o sinal for de VENDA (-1), ativa a animação de chamas no fundo
    if sinal_atual == -1:
        efeito_fogo = """
        @keyframes flames {
            0% { box-shadow: 0 -10px 20px #ff4500, 0 -20px 40px #ff0000; }
            50% { box-shadow: 0 -15px 30px #ff8c00, 0 -30px 60px #ff4500; }
            100% { box-shadow: 0 -10px 20px #ff4500, 0 -20px 40px #ff0000; }
        }
        .stApp { animation: flames 1.5s infinite alternate; border-top: 10px solid #ff4500; }
        """

    st.markdown(f"""
        <link href="https://fonts.googleapis.com/css2?family=Creepster&family=Press+Start+2P&display=swap" rel="stylesheet">
        <style>
        .stApp {{
            background-color: #000000 !important;
            background-image: radial-gradient(circle at center, #2a0000 0%, #000000 100%);
        }}
        {efeito_fogo}
        
        /* RPG PARTY ANIMATION */
        .rpg-container {{ width: 100%; height: 60px; position: relative; overflow: hidden; background: rgba(0,0,0,0.5); border-bottom: 2px solid #ff0000; }}
        .party-pixel {{ position: absolute; font-size: 35px; white-space: nowrap; animation: moveParty 12s linear infinite; }}
        @keyframes moveParty {{ from {{ left: -300px; }} to {{ left: 100%; }} }}

        h1, h2, h3, .stMetric label {{ font-family: 'Press Start 2P', cursive !important; color: #ff0000 !important; text-shadow: 2px 2px 10px #000; }}
        .signal-card {{ padding: 35px; border-radius: 20px; text-align: center; border: 3px solid #500; }}
        .buy {{ background: linear-gradient(135deg, #003300 0%, #00ff00 100%); color: #000 !important; box-shadow: 0 0 30px #0f0; }}
        .sell {{ background: linear-gradient(135deg, #330000 0%, #ff0000 100%); color: #fff !important; box-shadow: 0 0 50px #ff4500; text-shadow: 0 0 10px #fff; }}
        .wait {{ background-color: #080808; color: #440000 !important; border: 1px dashed #600; }}
        .timer-text {{ font-family: 'Press Start 2P', cursive; font-size: 70px; color: #ff0000; text-align: center; text-shadow: 0 0 25px #f00; }}
        [data-testid="stSidebar"] {{ background-color: #050505 !important; border-right: 2px solid #ff0000; }}
        </style>

        <div class="rpg-container">
            <div class="party-pixel">
                👧🏻 🏃‍♂️ 🧢 🏹 .... 🔥👹🔥
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- BUSCA DE DADOS ---
@st.cache_data(ttl=5)
def buscar_dados(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(col).capitalize() for col in df.columns]
        return df.dropna()
    except: return None

# --- SIDEBAR ---
st.sidebar.title("🔥 INFERNO PORTAL")
cat = st.sidebar.radio("Dimensão:", ["Ações", "Criptos", "Forex", "Commodities"])
ativos = {
    "Ações": {"NVIDIA": "NVDA", "McDonald's": "MCD", "Coca-Cola": "KO", "Amazon": "AMZN", "Apple": "AAPL", "Tesla": "TSLA", "Netflix": "NFLX"},
    "Criptos": {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD"},
    "Forex": {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X"},
    "Commodities": {"Ouro": "GC=F", "Petróleo": "CL=F"}
}
lista = ativos[cat]
nome_exibicao = st.sidebar.selectbox("Ativo:", list(lista.keys()))
par_original = lista[nome_exibicao]
nome_copiar = par_original.replace("-USD", "").replace("=X", "").replace("=F", "")

# --- LÓGICA DE SINAL ---
df = buscar_dados(par_original)
sinal = 0
if df is not None and len(df) > 14:
    rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
    bb = ta.bbands(df['Close'], length=20, std=2.5)
    preco = float(df['Close'].iloc[-1])
    if preco <= bb.iloc[-1, 0] and rsi < 30: sinal = 1 
    elif preco >= bb.iloc[-1, 2] and rsi > 70: sinal = -1

# Carregar CSS (com ou sem fogo)
carregar_estilo(sinal)

if df is not None:
    st.markdown(f'<h2 style="text-align:center;">{nome_exibicao}</h2>', unsafe_allow_html=True)
    
    if sinal != 0:
        classe = "buy" if sinal == 1 else "sell"
        texto = "⬆️ COMPRA" if sinal == 1 else "🔥 VENDA (INFERNO) 🔥"
        st.markdown(f'<div class="signal-card {classe}"><h1>{texto}</h1></div>', unsafe_allow_html=True)
        acao_sinal(nome_copiar)
    else:
        st.markdown('<div class="signal-card wait"><h2>⌛ CAÇANDO O VECNA...</h2></div>', unsafe_allow_html=True)

    segundos = 60 - datetime.now().second
    st.markdown(f'<div class="timer-text">{segundos}s</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    col1.metric("PREÇO", f"{preco:.4f}")
    col2.metric("RSI", f"{rsi:.0f}%")

    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    
    time.sleep(1)
    st.rerun()
else:
    st.info("Sincronizando portal...")
    time.sleep(2)
    st.rerun()
