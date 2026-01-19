import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="QUANTUM VECNA FULL", layout="wide")

# --- FUNÇÃO SOM, CÓPIA E REDIRECIONAMENTO (JS) ---
def acao_sinal(nome_para_copiar):
    sound_url = "https://www.myinstants.com/media/sounds/vecna-clock-sound-effect.mp3"
    corretora_url = "https://qxbroker.com/pt/demo-trade"
    
    js_code = f"""
        <script>
        function executarAcao() {{
            navigator.clipboard.writeText("{nome_para_copiar}");
            var audio = new Audio("{sound_url}");
            audio.play();
            window.open("{corretora_url}", "_blank");
        }}
        </script>
        <div onclick="executarAcao()" style="background: white; color: black; padding: 20px; border-radius: 15px; text-align: center; cursor: pointer; font-weight: bold; border: 4px solid #ff0000; box-shadow: 0 0 20px #ff0000; margin-top: 10px;">
            🚀 CLIQUE: COPIAR "{nome_para_copiar}" E ABRIR CORRETORA
        </div>
    """
    st.components.v1.html(js_code, height=120)

# --- ESTILO ---
st.markdown("""
    <style>
    .main { background-color: #050000; }
    .signal-card { padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 10px; }
    .buy { background: linear-gradient(135deg, #004d1a 0%, #00ff55 100%); color: #000; }
    .sell { background: linear-gradient(135deg, #4d0000 0%, #ff0000 100%); color: #fff; }
    .timer-text { font-size: 60px; font-weight: bold; color: #ff0000; text-align: center; text-shadow: 0 0 10px #f00; }
    </style>
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

# --- SIDEBAR COM TODOS OS ATIVOS ---
st.sidebar.title("💎 MENU DE ATIVOS")
categoria = st.sidebar.radio("Filtrar por:", ["Ações (Stocks)", "Criptomoedas", "Forex (Moedas)", "Commodities"])

if categoria == "Ações (Stocks)":
    lista_ativos = {
        "McDonald's": "MCD", "Coca-Cola": "KO", "Amazon": "AMZN", 
        "Apple": "AAPL", "Tesla": "TSLA", "NVIDIA": "NVDA", 
        "Netflix": "NFLX", "Disney": "DIS", "Microsoft": "MSFT"
    }
elif categoria == "Criptomoedas":
    lista_ativos = {
        "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD",
        "Ripple (XRP)": "XRP-USD", "Cardano": "ADA-USD"
    }
elif categoria == "Forex (Moedas)":
    lista_ativos = {
        "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
        "AUD/USD": "AUDUSD=X", "EUR/GBP": "EURGBP=X", "USD/CAD": "CAD=X"
    }
else: # Commodities
    lista_ativos = {
        "Ouro (Gold)": "GC=F", "Prata (Silver)": "SI=F", "Petróleo": "CL=F"
    }

nome_exibicao = st.sidebar.selectbox("Selecione o Ativo:", list(lista_ativos.keys()))
par_original = lista_ativos[nome_exibicao]

# Limpeza para a cópia (Ex: BTC-USD vira BTC / EURUSD=X vira EURUSD)
nome_limpo = par_original.replace("-USD", "").replace("=X", "").replace("=F", "")

# --- LÓGICA PRINCIPAL ---
df = buscar_dados(par_original)

if df is not None and len(df) > 14:
    try:
        rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
        bb = ta.bbands(df['Close'], length=20, std=2.5)
        preco = float(df['Close'].iloc[-1])
        
        sinal = 0
        if preco <= bb.iloc[-1, 0] and rsi < 30: sinal = 1 
        elif preco >= bb.iloc[-1, 2] and rsi > 70: sinal = -1

        st.subheader(f"Monitorando: {nome_exibicao}")
        
        # SINAL E BOTÃO
        if sinal != 0:
            cor_classe = "buy" if sinal == 1 else "sell"
            texto_sinal = "⬆️ COMPRA (CALL)" if sinal == 1 else "⬇️ VENDA (PUT)"
            st.markdown(f'<div class="signal-card {cor_classe}"><h1>{texto_sinal}</h1></div>', unsafe_allow_html=True)
            acao_sinal(nome_limpo)
        else:
            st.markdown('<div class="signal-card" style="background:#111; color:#444;"><h1>⌛ AGUARDANDO...</h1></div>', unsafe_allow_html=True)

        # TIMER
        segundos_restantes = 60 - datetime.now().second
        st.markdown(f'<div class="timer-text">{segundos_restantes}s</div>', unsafe_allow_html=True)

        # MÉTRICAS E GRÁFICO
        c1, c2 = st.columns(2)
        c1.metric("Preço", f"{preco:.4f}")
        c2.metric("RSI", f"{rsi:.0f}%")

        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=350, margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True)
        
    except: st.error("Erro nos indicadores deste ativo.")
    
    time.sleep(1)
    st.rerun()
else:
    st.info(f"Sincronizando {nome_exibicao}... Verifique o horário do mercado.")
    time.sleep(2)
    st.rerun()
