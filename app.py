import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="QUANTUM VECNA COPY", layout="wide")

# --- FUNÇÃO SOM E CÓPIA (JAVASCRIPT) ---
def acao_sinal(nome_ativo):
    sound_url = "https://www.myinstants.com/media/sounds/vecna-clock-sound-effect.mp3"
    corretora_url = "https://qxbroker.com/pt/demo-trade"
    
    # Este script toca o som, copia o texto e abre o link
    js_code = f"""
        <script>
        function executarAcao() {{
            // Copiar para área de transferência
            navigator.clipboard.writeText("{nome_ativo}");
            
            // Tocar som
            var audio = new Audio("{sound_url}");
            audio.play();
            
            // Abrir corretora
            window.open("{corretora_url}", "_blank");
        }}
        </script>
        <div onclick="executarAcao()" style="background: white; color: black; padding: 20px; border-radius: 15px; text-align: center; cursor: pointer; font-weight: bold; border: 4px solid #ff0000; box-shadow: 0 0 20px #ff0000;">
            🚀 CLIQUE AQUI: COPIAR "{nome_ativo}" E ABRIR QUOTEX
        </div>
    """
    st.components.v1.html(js_code, height=100)

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

# --- SIDEBAR ---
st.sidebar.title("🕰️ MUNDO INVERTIDO")
categoria = st.sidebar.radio("Ativos:", ["Ações (Stocks)", "Criptomoedas", "Forex"])

lista = {
    "Ações (Stocks)": {"McDonald's": "MCD", "Coca-Cola": "KO", "Amazon": "AMZN"},
    "Criptomoedas": {"Bitcoin": "BTC-USD", "Ethereum": "ETH-USD"},
    "Forex": {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X"}
}[categoria]

nome_exibicao = st.sidebar.selectbox("Selecione:", list(lista.keys()))
par = lista[nome_exibicao]

# --- LÓGICA ---
df = buscar_dados(par)

if df is not None and len(df) > 14:
    rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
    bb = ta.bbands(df['Close'], length=20, std=2.5)
    preco = float(df['Close'].iloc[-1])
    
    sinal = 0
    if preco <= bb.iloc[-1, 0] and rsi < 30: sinal = 1 
    elif preco >= bb.iloc[-1, 2] and rsi > 70: sinal = -1

    st.subheader(f"Monitorando: {nome_exibicao}")
    
    # Exibição do sinal e botão de ação
    if sinal != 0:
        cor_classe = "buy" if sinal == 1 else "sell"
        texto_sinal = "⬆️ COMPRA" if sinal == 1 else "⬇️ VENDA"
        st.markdown(f'<div class="signal-card {cor_classe}"><h1>{texto_sinal} AGORA</h1></div>', unsafe_allow_html=True)
        
        # O BOTÃO MÁGICO
        acao_sinal(par.replace("=X", "")) # Remove o =X para facilitar a busca na corretora
    else:
        st.markdown('<div class="signal-card" style="background:#111; color:#444;"><h1>⌛ AGUARDANDO...</h1></div>', unsafe_allow_html=True)

    # Timer
    segundos_restantes = 60 - datetime.now().second
    st.markdown(f'<div class="timer-text">{segundos_restantes}s</div>', unsafe_allow_html=True)

    # Gráfico
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=350, margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)
    
    time.sleep(1)
    st.rerun()
