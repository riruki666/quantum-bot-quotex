import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="QUANTUM VECNA EDITION", layout="wide")

# --- FUNÇÃO DO SOM DO VECNA ---
def play_vecna_sound():
    # Som das badaladas do relógio do Vecna
    sound_url = "https://www.myinstants.com/media/sounds/vecna-clock-sound-effect.mp3"
    html_string = f"""
        <audio autoplay>
            <source src="{sound_url}" type="audio/mp3">
        </audio>
    """
    st.components.v1.html(html_string, height=0)

# --- ESTILO VISUAL SOMBRIO ---
st.markdown("""
    <style>
    .main { background-color: #050000; }
    .signal-card { padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 10px; border: 2px solid #300; }
    .buy { background: linear-gradient(135deg, #004d1a 0%, #00ff55 100%); color: #000; font-weight: bold; }
    .sell { background: linear-gradient(135deg, #4d0000 0%, #ff0000 100%); color: #fff; box-shadow: 0 0 20px #f00; }
    .wait { background-color: #0a0a0a; color: #4e0000; border: 1px solid #200; }
    .timer-text { font-size: 60px; font-weight: bold; color: #ff0000; text-align: center; text-shadow: 0 0 10px #f00; margin-top: -10px; }
    .vecna-alert { color: #ff0000; font-size: 18px; font-weight: bold; text-align: center; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# --- BUSCA DE DADOS BLINDADA ---
@st.cache_data(ttl=5)
def buscar_dados(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, threads=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[['Open', 'High', 'Low', 'Close']].copy()
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna()
    except:
        return None

# --- SIDEBAR (MENU DE ATIVOS) ---
st.sidebar.title("🕰️ MUNDO INVERTIDO")
categoria = st.sidebar.radio("Filtrar por:", ["Ações (Stocks)", "Criptomoedas", "Forex (Moedas)", "Commodities"])

if categoria == "Ações (Stocks)":
    lista_ativos = {"McDonald's": "MCD", "Coca-Cola": "KO", "Amazon": "AMZN", "Apple": "AAPL", "Tesla": "TSLA"}
elif categoria == "Criptomoedas":
    lista_ativos = {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD"}
elif categoria == "Forex (Moedas)":
    lista_ativos = {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X"}
else:
    lista_ativos = {"Ouro (Gold)": "GC=F", "Prata (Silver)": "SI=F"}

nome_exibicao = st.sidebar.selectbox("Selecione o Ativo:", list(lista_ativos.keys()))
par = lista_ativos[nome_exibicao]

# --- LÓGICA PRINCIPAL ---
df = buscar_dados(par)

if df is not None and len(df) > 14:
    try:
        # Indicadores
        rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
        bb = ta.bbands(df['Close'], length=20, std=2.5)
        banda_inf, banda_sup = float(bb.iloc[-1, 0]), float(bb.iloc[-1, 2])
        preco = float(df['Close'].iloc[-1])
        
        # Sinal
        sinal = 0
        if preco <= banda_inf and rsi < 30: sinal = 1 
        elif preco >= banda_sup and rsi > 70: sinal = -1

        # Exibição do Cartão
        st.subheader(f"Monitorando: {nome_exibicao}")
        
        if sinal == 1:
            st.markdown('<div class="signal-card buy"><h1>⬆️ COMPRE AGORA (CALL)</h1></div>', unsafe_allow_html=True)
        elif sinal == -1:
            st.markdown('<div class="signal-card sell"><h1>⬇️ VENDA AGORA (PUT)</h1></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="signal-card wait"><h1>⌛ AGUARDANDO O RELÓGIO...</h1></div>', unsafe_allow_html=True)

        # Cronômetro
        segundos_restantes = 60 - datetime.now().second
        st.markdown(f'<div class="timer-text">{segundos_restantes}s</div>', unsafe_allow_html=True)

        # Alerta Sonoro Vecna
        if sinal != 0 and 2 <= segundos_restantes <= 12:
            st.markdown('<div class="vecna-alert">🕰️ O RELÓGIO ESTÁ BATENDO... PREPARE SUA ENTRADA!</div>', unsafe_allow_html=True)
            if 'last_vecna' not in st.session_state or st.session_state.last_vecna != datetime.now().minute:
                play_vecna_sound()
                st.session_state.last_vecna = datetime.now().minute

        # Gráfico
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=350, margin=dict(l=0,r=0,b=0,t=0))
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro no processamento: Selecione outro ativo.")
    
    time.sleep(1)
    st.rerun()
else:
    st.info(f"Sincronizando {nome_exibicao}... Verifique se o mercado está aberto.")
    time.sleep(3)
    st.rerun()
