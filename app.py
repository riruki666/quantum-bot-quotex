import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER PROFITS - AI SCANNER", page_icon="🤖", layout="wide")

# --- ESTILO CSS PROFISSIONAL ---
st.markdown("""
    <style>
    .stApp { background-color: #050505 !important; }
    .main-title {
        color: #ff0000; font-weight: 900; font-size: 50px;
        text-align: center; text-shadow: 2px 2px 0px #ffffff;
        margin-top: -50px;
    }
    .scanner-card {
        background: #111; border: 1px solid #333;
        border-radius: 10px; padding: 15px; margin-bottom: 10px;
    }
    .status-buy { color: #00ff00; font-weight: bold; }
    .status-sell { color: #ff0000; font-weight: bold; }
    .timer-display {
        font-size: 35px; font-weight: 900; text-align: center;
        color: #ffcc00; background: #1a1a1a; padding: 10px;
        border-radius: 10px; border: 2px solid #333;
    }
    </style>
    <h1 class="main-title">STRANGER AI SCANNER</h1>
    <iframe src="https://www.youtube.com/embed/Av1DFgWLR0E?autoplay=1&loop=1&playlist=Av1DFgWLR0E" 
            width="0" height="0" frameborder="0" allow="autoplay"></iframe>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS DE VARREDURA ---
watchlist = {
    "EURUSD=X": "EUR/USD", "GBPUSD=X": "GBP/USD", "JPY=X": "USD/JPY",
    "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum", "SOL-USD": "Solana",
    "NVDA": "NVIDIA", "TSLA": "Tesla", "AAPL": "Apple", "GC=F": "Ouro"
}

# --- FUNÇÃO INTELIGENTE DE SCANNER ---
def scanner_mercado():
    oportunidades = []
    for ticker, nome in watchlist.items():
        try:
            df = yf.download(ticker, period="1d", interval="1m", progress=False)
            if df.empty: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            
            rsi = ta.rsi(df['Close'], length=14).iloc[-1]
            bb = ta.bbands(df['Close'], length=20, std=2.5)
            preco = df['Close'].iloc[-1]
            
            # Lógica de IA: Detectar Extremos
            if rsi <= 32 and preco <= bb.iloc[-1, 0]:
                oportunidades.append({"ativo": nome, "ticker": ticker, "tipo": "COMPRA (BAIXA)", "forca": rsi})
            elif rsi >= 68 and preco >= bb.iloc[-1, 2]:
                oportunidades.append({"ativo": nome, "ticker": ticker, "tipo": "VENDA (ALTA)", "forca": rsi})
        except: continue
    return oportunidades

# --- INTERFACE ---
col_L, col_R = st.columns([1, 3])

with col_L:
    st.markdown("### 🔍 Radar de Sinais")
    if st.button("🔄 FORÇAR SCANNER"):
        st.cache_data.clear()
    
    lista_ops = scanner_mercado()
    
    if not lista_ops:
        st.info("Varrendo mercado... Nenhuma exaustão detectada no momento.")
    else:
        for op in lista_ops:
            cor = "status-buy" if "COMPRA" in op['tipo'] else "status-sell"
            st.markdown(f"""
            <div class="scanner-card">
                <b>{op['ativo']}</b><br>
                Status: <span class="{cor}">{op['tipo']}</span><br>
                RSI: {op['forca']:.1f}
            </div>
            """, unsafe_allow_html=True)

with col_R:
    # Seleção do Ativo Principal para Análise Gráfica
    ativo_selecionado = st.selectbox("Analise um ativo do Scanner ou Watchlist:", list(watchlist.values()))
    ticker_final = [k for k, v in watchlist.items() if v == ativo_selecionado][0]
    
    # Cronômetro
    segundos = 60 - datetime.now().second
    st.markdown(f'<div class="timer-display">⏳ VELA M1: {segundos}s</div>', unsafe_allow_html=True)
    
    # Carregamento do Gráfico
    df_main = yf.download(ticker_final, period="1d", interval="1m", progress=False)
    if not df_main.empty:
        if isinstance(df_main.columns, pd.MultiIndex): df_main.columns = df_main.columns.get_level_values(0)
        
        fig = go.Figure(data=[go.Candlestick(x=df_main.index, open=df_main['Open'], high=df_main['High'], low=df_main['Low'], close=df_main['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        # Link Dinâmico Quotex
        ativo_limpo = ticker_final.replace("=X", "").replace("-USD", "").replace("=F", "").upper()
        st.link_button(f"🔥 ENTRAR AGORA EM {ativo_selecionado} NA QUOTEX", f"https://qxbroker.com/pt/trade/{ativo_limpo}", use_container_width=True)

time.sleep(1)
st.rerun()
