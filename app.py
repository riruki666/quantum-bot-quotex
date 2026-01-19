import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER PROFITS - ABSOLUTO", page_icon="👹", layout="wide")

# --- ESTILO CSS PARA NITIDEZ E TEMA DARK ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    
    .main-title {
        color: #ff0000;
        font-weight: 900;
        font-size: 55px;
        text-align: center;
        text-shadow: 2px 2px 0px #ffffff;
        margin-top: -50px;
        letter-spacing: -2px;
    }

    .timer-display {
        font-size: 45px;
        font-weight: 900;
        text-align: center;
        padding: 15px;
        background: #111;
        border-radius: 15px;
        border: 2px solid #ff0000;
        margin-bottom: 20px;
        color: #00ff00;
    }

    .signal-card {
        padding: 40px;
        border-radius: 25px;
        text-align: center;
        font-size: 50px;
        font-weight: 900;
        border: 6px solid #fff;
        text-transform: uppercase;
    }

    /* Nitidez das Métricas */
    [data-testid="stMetricValue"] { 
        font-size: 40px !important; 
        font-weight: 900 !important; 
        color: #ffffff !important; 
    }
    
    /* Botão Quotex */
    .stButton>button {
        background: linear-gradient(90deg, #ff0000 0%, #8b0000 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 24px !important;
        border-radius: 10px !important;
        height: 70px !important;
        border: 2px solid #fff !important;
    }
    </style>
    
    <h1 class="main-title">STRANGER PROFITS</h1>
    
    <iframe src="https://www.youtube.com/embed/Av1DFgWLR0E?autoplay=1&loop=1&playlist=Av1DFgWLR0E" 
            width="0" height="0" frameborder="0" allow="autoplay"></iframe>
    """, unsafe_allow_html=True)

# --- MENU LATERAL: TODOS OS ATIVOS ---
st.sidebar.title("💎 TERMINAL DE ATIVOS")
categoria = st.sidebar.radio("Escolha o Mercado:", ["Ações", "Criptomoedas", "Forex", "Commodities"])

ativos_db = {
    "Ações": {
        "NVIDIA": "NVDA", "Tesla": "TSLA", "Apple": "AAPL", "Amazon": "AMZN", 
        "Netflix": "NFLX", "Microsoft": "MSFT", "Disney": "DIS", "McDonalds": "MCD"
    },
    "Criptomoedas": {
        "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD", 
        "XRP": "XRP-USD", "Cardano": "ADA-USD", "Dogecoin": "DOGE-USD"
    },
    "Forex": {
        "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", 
        "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "EUR/GBP": "EURGBP=X"
    },
    "Commodities": {
        "Ouro": "GC=F", "Petróleo": "CL=F", "Prata": "SI=F", "Gás Natural": "NG=F"
    }
}

nome_ativo = st.sidebar.selectbox("Selecione o Alvo:", list(ativos_db[categoria].keys()))
ticker = ativos_db[categoria][nome_ativo]

# --- CRONÔMETRO DE VELA (M1) ---
segundos = 60 - datetime.now().second
cor_timer = "#00ff00" if segundos > 10 else "#ff0000"
st.markdown(f'<div class="timer-display" style="color:{cor_timer}; border-color:{cor_timer};">⏳ FECHAMENTO: {segundos}s</div>', unsafe_allow_html=True)

# --- FUNÇÃO DE DADOS ROBUSTA ---
@st.cache_data(ttl=1)
def get_market_data(t):
    try:
        data = yf.download(t, period="1d", interval="1m", progress=False)
        if data.empty: return None
        # Correção para o novo formato do Yahoo Finance (MultiIndex)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data.dropna()
    except Exception as e:
        return None

df = get_market_data(ticker)

if df is not None and len(df) > 25:
    # --- CÁLCULOS TÉCNICOS ---
    rsi = ta.rsi(df['Close'], length=14).iloc[-1]
    bb = ta.bbands(df['Close'], length=20, std=2.5) # Desvio 2.5 para maior assertividade
    preco_atual = df['Close'].iloc[-1]
    banda_inf = bb.iloc[-1, 0]
    banda_sup = bb.iloc[-1, 2]
    
    # Gráfico Estilo Profissional
    
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400, 
                      paper_bgcolor='#000', plot_bgcolor='#000', margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

    # Painel de Dados nítidos
    c1, c2 = st.columns(2)
    c1.metric("VALOR ATUAL", f"{preco_atual:.4f}")
    c2.metric("FORÇA RSI", f"{rsi:.1f}%")

    # --- LÓGICA DE ASSERTIVIDADE ABSOLUTA ---
    # SINAL DE COMPRA: Preço tocou/furou banda inferior + RSI abaixo de 30
    if rsi <= 30 and preco_atual <= banda_inf:
        st.markdown('<div class="signal-card" style="background:#2eb85c;">🚀 COMPRA (CALL)</div>', unsafe_allow_html=True)
        # SINO DE ALERTA
        st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
    
    # SINAL DE VENDA: Preço tocou/furou banda superior + RSI acima de 70
    elif rsi >= 70 and preco_atual >= banda_sup:
        st.markdown('<div class="signal-card" style="background:#e55353;">🔥 VENDA (PUT)</div>', unsafe_allow_html=True)
        # SINO DE ALERTA
        st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
    
    else:
        st.markdown('<div class="signal-card" style="background:#111; color:#333; border-color:#222;">AGUARDANDO OPORTUNIDADE...</div>', unsafe_allow_html=True)

    # --- LINK DIRETO QUOTEX ---
    # Limpa o ticker para a URL (ex: EURUSD=X vira EURUSD)
    ativo_limpo = ticker.replace("=X", "").replace("-USD", "").replace("=F", "").upper()
    st.write("---")
    st.link_button(f"👉 ABRIR {nome_ativo} NA QUOTEX", f"https://qxbroker.com/pt/trade/{ativo_limpo}", use_container_width=True)

    # Refresh para o cronômetro
    time.sleep(1)
    st.rerun()
else:
    st.warning("Portal instável ou mercado fechado. Reconectando...")
    time.sleep(5)
    st.rerun()
