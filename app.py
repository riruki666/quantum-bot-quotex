import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER PROFITS - ANALYTICS", page_icon="📈", layout="wide")

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; }
    .main-title {
        color: #ff0000;
        font-family: 'Arial Black', sans-serif;
        font-size: 50px;
        text-align: center;
        text-shadow: 2px 2px #fff;
        margin-top: -50px;
    }
    .stMetric { background-color: #1a1c24; padding: 10px; border-radius: 10px; border: 1px solid #333; }
    .timer-box {
        font-size: 24px;
        color: #ffcc00;
        text-align: center;
        padding: 10px;
        border: 2px solid #ffcc00;
        border-radius: 10px;
        background: #000;
    }
    </style>
    
    <h1 class="main-title">STRANGER THINGS PROFITS</h1>
    
    <iframe src="https://www.youtube.com/embed/Av1DFgWLR0E?autoplay=1&loop=1&playlist=Av1DFgWLR0E" 
            width="0" height="0" frameborder="0" allow="autoplay"></iframe>
    """, unsafe_allow_html=True)

# --- LISTA COMPLETA DE ATIVOS ---
st.sidebar.title("👹 CONFIGURAÇÕES")
cat = st.sidebar.radio("Mercado:", ["Ações BR/EUA", "Criptomoedas", "Forex (Moedas)", "Commodities"])

ativos_db = {
    "Ações BR/EUA": {"NVIDIA": "NVDA", "Tesla": "TSLA", "Apple": "AAPL", "Petrobras": "PBR", "Amazon": "AMZN", "Netflix": "NFLX"},
    "Criptomoedas": {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD", "Cardano": "ADA-USD", "XRP": "XRP-USD"},
    "Forex (Moedas)": {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", "AUD/USD": "AUDUSD=X"},
    "Commodities": {"Ouro": "GC=F", "Petróleo": "CL=F", "Prata": "SI=F"}
}

ticker_nome = st.sidebar.selectbox("Ativo:", list(ativos_db[cat].keys()))
ticker = ativos_db[cat][ticker_nome]

# --- LÓGICA DO CRONÔMETRO (Vela de 1 min) ---
agora = datetime.now()
segundos_restantes = 60 - agora.second
st.sidebar.markdown(f'<div class="timer-box">⏳ Próxima Vela: {segundos_restantes}s</div>', unsafe_allow_html=True)

# --- BUSCA DE DADOS ---
@st.cache_data(ttl=5)
def load_data(s):
    try:
        data = yf.download(s, period="1d", interval="1m", progress=False)
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        return data.dropna()
    except: return None

df = load_data(ticker)

if df is not None and len(df) > 20:
    rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
    bb = ta.bbands(df['Close'], length=20, std=2.5)
    preco_atual = float(df['Close'].iloc[-1])
    
    # --- GRÁFICO ---
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450,
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # --- MÉTRICAS E SINAIS ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Preço", f"${preco_atual:.2f}")
    col2.metric("RSI (Força)", f"{rsi:.1f}")
    
    # Lógica do Sino e Alerta
    sinal = "AGUARDAR"
    cor_sinal = "white"
    
    if rsi < 30:
        sinal = "COMPRA (BUY)"
        cor_sinal = "#2eb85c"
        st.markdown(f'<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
    elif rsi > 70:
        sinal = "VENDA (SELL)"
        cor_sinal = "#e55353"
        st.markdown(f'<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)

    col3.markdown(f"<h3 style='color:{cor_sinal}; text-align:center;'>{sinal}</h3>", unsafe_allow_html=True)

    # --- LINK DIRETO PARA QUOTEX ---
    # Limpa o ticker para o link (ex: remove =X ou -USD)
    clean_ticker = ticker.split('=')[0].split('-')[0]
    quotex_url = f"https://qxbroker.com/pt/demo-trade" # Nota: Quotex não aceita deep link direto de ativo externo sempre
    
    st.write("---")
    st.link_button(f"🚀 ABRIR {ticker_nome} NA QUOTEX", quotex_url, use_container_width=True)

    # Auto-refresh a cada 1 segundo para o cronômetro
    time.sleep(1)
    st.rerun()
