import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="VECNA INFERNO TRADER", page_icon="🔥", layout="wide")

# --- FUNÇÃO SOM, CÓPIA E MÚSICA ---
def injetar_atmosfera(nome_copiar, sinal_atual):
    sound_vecna = "https://www.myinstants.com/media/sounds/vecna-clock-sound-effect.mp3"
    # Link da trilha de suspense (YouTube invisível)
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
        <div onclick="executarAcao()" style="background: linear-gradient(135deg, #8b0000 0%, #ff0000 100%); color: white; padding: 25px; border-radius: 15px; text-align: center; cursor: pointer; font-weight: bold; border: 3px solid #fff; box-shadow: 0 0 30px #f00; margin-top: 20px; font-size: 22px; font-family: 'Arial Black', sans-serif;">
            🔥 GOLPE FINAL: COPIAR "{nome_copiar}" & ABRIR QUOTEX
        </div>
    """
    st.components.v1.html(js_code, height=180)

# --- ESTILO VISUAL CORRIGIDO ---
def carregar_estilo(sinal_atual):
    # Efeito de chamas apenas no sinal de venda
    efeito_fogo = ""
    if sinal_atual == -1:
        efeito_fogo = "border-top: 15px solid #ff4500; box-shadow: inset 0 0 100px #ff0000;"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

        .stApp {{
            background-color: #000000 !important;
            {efeito_fogo}
        }}

        /* RPG PARTY ANIMATION (Ícones Fixos) */
        .rpg-container {{ 
            width: 100%; height: 80px; position: relative; overflow: hidden; 
            background: #0a0a0a; border-bottom: 3px solid #ff0000; margin-bottom: 20px;
        }}
        .party-pixel {{ 
            position: absolute; font-size: 40px; white-space: nowrap; 
            animation: moveParty 12s linear infinite; 
            color: white;
        }}
        @keyframes moveParty {{ 
            from {{ left: -400px; }} 
            to {{ left: 100%; }} 
        }}

        /* TEXTOS CLAROS E VISÍVEIS */
        h1, h2, h3 {{ font-family: 'Press Start 2P', cursive; color: #ffffff !important; text-shadow: 2px 2px #ff0000; text-align: center; }}
        p, .stMetric label {{ font-family: 'Arial', sans-serif; color: #ff8888 !important; font-weight: bold; font-size: 16px !important; }}
        
        .timer-text {{ 
            font-family: 'Press Start 2P', cursive; font-size: 60px; color: #ff0000; 
            text-align: center; text-shadow: 0 0 20px #f00; margin: 20px 0;
        }}

        /* CARDS */
        .signal-card {{ padding: 30px; border-radius: 20px; text-align: center; border: 4px solid #500; background: #111; }}
        .buy {{ background: #00ff00 !important; color: #000 !important; box-shadow: 0 0 30px #0f0; }}
        .sell {{ background: #ff0000 !important; color: #fff !important; box-shadow: 0 0 40px #f00; }}
        
        /* SIDEBAR VISÍVEL */
        [data-testid="stSidebar"] {{ background-color: #050505 !important; border-right: 2px solid #ff0000; }}
        .stRadio label, .stSelectbox label {{ color: #ffffff !important; font-weight: bold; }}
        </style>

        <div class="rpg-container">
            <div class="party-pixel">
                🧙‍♂️ 🗡️ 🛡️ 🏹 ........ 👹🔥
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
st.sidebar.title("🔥 VECNA PORTAL")
cat = st.sidebar.radio("Ativos:", ["Ações", "Criptos", "Forex", "Commodities"])
ativos = {
    "Ações": {"NVIDIA": "NVDA", "McDonald's": "MCD", "Coca-Cola": "KO", "Amazon": "AMZN", "Apple": "AAPL", "Tesla": "TSLA"},
    "Criptos": {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD"},
    "Forex": {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X"},
    "Commodities": {"Ouro": "GC=F", "Petróleo": "CL=F"}
}
lista = ativos[cat]
nome_exibicao = st.sidebar.selectbox("Ativo:", list(lista.keys()))
par_original = lista[nome_exibicao]
nome_copiar = par_original.replace("-USD", "").replace("=X", "").replace("=F", "")

# --- LÓGICA ---
df = buscar_dados(par_original)
sinal = 0
rsi, preco = 0, 0
if df is not None and len(df) > 14:
    rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
    bb = ta.bbands(df['Close'], length=20, std=2.5)
    preco = float(df['Close'].iloc[-1])
    if preco <= bb.iloc[-1, 0] and rsi < 30: sinal = 1 
    elif preco >= bb.iloc[-1, 2] and rsi > 70: sinal = -1

carregar_estilo(sinal)

if df is not None:
    st.markdown(f"## {nome_exibicao}")
    
    if sinal != 0:
        classe = "buy" if sinal == 1 else "sell"
        texto = "⬆️ COMPRA (CALL)" if sinal == 1 else "🔥 VENDA (PUT) 🔥"
        st.markdown(f'<div class="signal-card {classe}"><h1>{texto}</h1></div>', unsafe_allow_html=True)
        injetar_atmosfera(nome_copiar, sinal)
    else:
        st.markdown('<div class="signal-card"><h3>⌛ AGUARDANDO EXAUSTÃO...</h3></div>', unsafe_allow_html=True)

    segundos = 60 - datetime.now().second
    st.markdown(f'<div class="timer-text">{segundos}s</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    col1.metric("PREÇO ATUAL", f"{preco:.4f}")
    col2.metric("FORÇA RSI", f"{rsi:.0f}%")

    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400, paper_bgcolor='#000', plot_bgcolor='#000')
    st.plotly_chart(fig, use_container_width=True)
    
    time.sleep(1)
    st.rerun()
