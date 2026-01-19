import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="VECNA QUANTUM ELITE",
    page_icon="https://i.ibb.co/C5fJvM2/vecna-icon.png",
    layout="wide"
)

# --- MÚSICA E AÇÕES JS ---
def injetar_audio_e_acao(nome_copiar):
    sound_vecna = "https://www.myinstants.com/media/sounds/vecna-clock-sound-effect.mp3"
    # Trilha de suspense de 10 horas em loop
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

        <div onclick="executarAcao()" style="background: linear-gradient(135deg, #4b0000 0%, #ff0000 100%); color: white; padding: 25px; border-radius: 15px; text-align: center; cursor: pointer; font-weight: bold; border: 2px solid #fff; box-shadow: 0 0 30px rgba(255,0,0,0.8); margin-top: 20px; font-size: 22px; font-family: 'Creepster', cursive;">
            🩸 COLHER LUCRO: COPIAR "{nome_copiar}" & IR PARA QUOTEX
        </div>
    """
    st.components.v1.html(js_code, height=160)

# --- ESTILO TOTAL DARK ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Creepster&family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
    .stApp {
        background-color: #000000 !important;
        background-image: radial-gradient(circle at center, #2a0000 0%, #000000 100%);
    }
    h1, h2, h3, p, span, .stMetric label {
        font-family: 'Press Start 2P', cursive !important;
        color: #ff0000 !important;
        text-shadow: 2px 2px 10px #000;
    }
    .signal-card { padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 15px; border: 2px solid #500; background-color: rgba(0,0,0,0.9); }
    .buy { background: linear-gradient(135deg, #003300 0%, #00ff00 100%); color: #000 !important; box-shadow: 0 0 30px #0f0; }
    .sell { background: linear-gradient(135deg, #330000 0%, #ff0000 100%); color: #fff !important; box-shadow: 0 0 30px #f00; }
    .wait { background-color: #080808; color: #440000 !important; border: 1px dashed #600; }
    .timer-text { font-family: 'Press Start 2P', cursive; font-size: 75px; color: #ff0000; text-align: center; text-shadow: 0 0 25px #f00; margin: 15px 0; }
    [data-testid="stMetric"] { background-color: #050505 !important; border: 1px solid #600 !important; border-radius: 10px; padding: 15px !important; }
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 2px solid #600; }
    </style>
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

# --- MENU DE ATIVOS ---
st.sidebar.title("🕰️ UPSIDE DOWN")
cat = st.sidebar.radio("Escolha a Dimensão:", ["Ações", "Criptos", "Forex", "Commodities"])

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

# --- LÓGICA ---
df = buscar_dados(par_original)

if df is not None and len(df) > 14:
    try:
        rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
        bb = ta.bbands(df['Close'], length=20, std=2.5)
        preco = float(df['Close'].iloc[-1])
        
        sinal = 0
        if preco <= bb.iloc[-1, 0] and rsi < 30: sinal = 1 
        elif preco >= bb.iloc[-1, 2] and rsi > 70: sinal = -1

        st.markdown(f'<h2 style="text-align:center;">{nome_exibicao}</h2>', unsafe_allow_html=True)
        
        if sinal != 0:
            classe = "buy" if sinal == 1 else "sell"
            st.markdown(f'<div class="signal-card {classe}"><h1>{"⬆️ COMPRA" if sinal == 1 else "⬇️ VENDA"}</h1></div>', unsafe_allow_html=True)
            injetar_audio_e_acao(nome_copiar)
        else:
            st.markdown('<div class="signal-card wait"><h2>⌛ AGUARDANDO O RELÓGIO...</h2></div>', unsafe_allow_html=True)

        segundos = 60 - datetime.now().second
        st.markdown(f'<div class="timer-text">{segundos}s</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        c1.metric("PREÇO", f"{preco:.4f}")
        c2.metric("FORÇA RSI", f"{rsi:.0f}%")

        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
    except: st.error("Erro na conexão com o Mundo Invertido.")
    
    time.sleep(1)
    st.rerun()
else:
    st.markdown('<h1 style="text-align:center;">ABRINDO PORTAL...</h1>', unsafe_allow_html=True)
    time.sleep(2)
    st.rerun()
