import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="UPSIDE DOWN TRADER",
    page_icon="https://i.ibb.co/C5fJvM2/vecna-icon.png",
    layout="wide"
)

# --- FUNÇÃO SOM, CÓPIA E REDIRECIONAMENTO (JS) ---
def acao_sinal(nome_para_copiar):
    sound_url = "https://www.myinstants.com/media/sounds/vecna-clock-sound-effect.mp3"
    corretora_url = "https://qxbroker.com/pt/demo-trade"
    
    js_code = f"""
        <script>
        function executarAcao() {{
            // Copia o nome exato do ativo para o CTRL+V
            const el = document.createElement('textarea');
            el.value = "{nome_para_copiar}";
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            
            // Toca o som do Vecna
            var audio = new Audio("{sound_url}");
            audio.play();
            
            // Abre a Quotex em nova aba
            window.open("{corretora_url}", "_blank");
        }}
        </script>
        <div onclick="executarAcao()" style="background: linear-gradient(135deg, #8b0000 0%, #ff4500 100%); color: white; padding: 20px; border-radius: 15px; text-align: center; cursor: pointer; font-weight: bold; border: 4px solid #fff; box-shadow: 0 0 25px rgba(255,0,0,0.7); margin-top: 20px; font-size: 22px; font-family: 'Creepster', cursive;">
            ⏳ CLIQUE: COPIAR "{nome_para_copiar}" & ABRIR CORRETORA
        </div>
    """
    st.components.v1.html(js_code, height=150)

# --- ESTILO VISUAL STRANGER THINGS ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Creepster&family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
    .main {
        background-color: #050000;
        background-image: url('https://i.ibb.co/D8d3j8K/upside-down-bg.jpg');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }
    h1, h2, h3, p, .stMetric label {
        font-family: 'Press Start 2P', cursive !important;
        color: #ff0000 !important;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.9);
    }
    .signal-card { padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 15px; border: 2px solid #500; }
    .buy { background: linear-gradient(135deg, #004d1a 0%, #00ff55 100%); color: #000; box-shadow: 0 0 20px #0f0; }
    .sell { background: linear-gradient(135deg, #4d0000 0%, #ff0000 100%); color: #fff; box-shadow: 0 0 20px #f00; }
    .wait { background-color: rgba(10, 0, 0, 0.8); color: #880000; border: 1px dashed #500; }
    .timer-text { font-family: 'Press Start 2P', cursive; font-size: 60px; font-weight: bold; color: #ff0000; text-align: center; text-shadow: 0 0 15px #f00; margin-top: 5px; }
    .stMetric { background-color: rgba(10, 0, 0, 0.85); border: 1px solid #ff0000; border-radius: 10px; padding: 10px; }
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

# --- SIDEBAR (MENU DE ATIVOS) ---
st.sidebar.title("🕰️ UPSIDE DOWN")
categoria = st.sidebar.radio("Dimensão:", ["Ações (Stocks)", "Criptomoedas", "Forex (Moedas)", "Commodities"])

if categoria == "Ações (Stocks)":
    lista_ativos = {
        "NVIDIA": "NVDA", "McDonald's": "MCD", "Coca-Cola": "KO", 
        "Amazon": "AMZN", "Apple": "AAPL", "Tesla": "TSLA", 
        "Netflix": "NFLX", "Microsoft": "MSFT"
    }
elif categoria == "Criptomoedas":
    lista_ativos = {
        "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD", "XRP": "XRP-USD"
    }
elif categoria == "Forex (Moedas)":
    lista_ativos = {
        "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", "AUD/USD": "AUDUSD=X"
    }
else:
    lista_ativos = {"Ouro": "GC=F", "Prata": "SI=F", "Petróleo": "CL=F"}

nome_exibicao = st.sidebar.selectbox("Ativo:", list(lista_ativos.keys()))
par_original = lista_ativos[nome_exibicao]

# Limpeza do nome para colar na Quotex
nome_para_copiar = par_original.replace("-USD", "").replace("=X", "").replace("=F", "")

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

        st.markdown(f'<h2 style="text-align:center;">{nome_exibicao}</h2>', unsafe_allow_html=True)
        
        if sinal != 0:
            cor = "buy" if sinal == 1 else "sell"
            txt = "⬆️ COMPRA" if sinal == 1 else "⬇️ VENDA"
            st.markdown(f'<div class="signal-card {cor}"><h1>{txt}</h1></div>', unsafe_allow_html=True)
            acao_sinal(nome_para_copiar)
        else:
            st.markdown('<div class="signal-card wait"><h2>⌛ AGUARDANDO...</h2></div>', unsafe_allow_html=True)

        segundos_restantes = 60 - datetime.now().second
        st.markdown(f'<div class="timer-text">{segundos_restantes}s</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        c1.metric("Preço", f"{preco:.4f}")
        c2.metric("RSI", f"{rsi:.0f}%")

        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=350, 
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
    except: st.error("Erro ao calcular indicadores.")
    
    time.sleep(1)
    st.rerun()
else:
    st.info("Sincronizando portal...")
    time.sleep(3)
    st.rerun()
