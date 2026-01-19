import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER AI - QUOTEX BRASIL", page_icon="🇧🇷", layout="wide")

# --- CSS: DESIGN DE ALTA PERFORMANCE ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    .main-title {
        color: #ff0000; font-weight: 900; font-size: 50px;
        text-align: center; text-shadow: 2px 2px 0px #ffffff;
        margin-top: -60px;
    }
    .radar-card {
        background: #111; border-left: 5px solid #00ff00;
        border-radius: 5px; padding: 12px; margin-bottom: 8px;
    }
    .timer-display {
        font-size: 50px; font-weight: 900; text-align: center;
        background: #0a0a0a; padding: 10px;
        border: 2px solid #ff0000; border-radius: 15px;
    }
    .soros-box {
        background: linear-gradient(135deg, #1a1c24 0%, #000 100%);
        padding: 20px; border-radius: 15px;
        border: 2px solid #00ff00; margin-top: 20px;
    }
    .val-text { font-size: 24px; font-weight: 900; color: #00ff00; }
    </style>
    <h1 class="main-title">STRANGER PROFITS BR</h1>
    <iframe src="https://www.youtube.com/embed/Av1DFgWLR0E?autoplay=1&loop=1&playlist=Av1DFgWLR0E" 
            width="0" height="0" frameborder="0" allow="autoplay"></iframe>
    """, unsafe_allow_html=True)

# --- ATIVOS FOCO QUOTEX ---
ativos_foco = {
    "EUR/USD": "EURUSD=X",
    "USD/BRL": "BRL=X",
    "BITCOIN": "BTC-USD",
    "OURO": "GC=F"
}

# --- MOTOR DE SCANNER ---
def scanner_br():
    sinais = []
    for nome, ticker in ativos_foco.items():
        try:
            d = yf.download(ticker, period="1d", interval="1m", progress=False)
            if d.empty: continue
            if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
            
            rsi = ta.rsi(d['Close'], length=14).iloc[-1]
            bb = ta.bbands(d['Close'], length=20, std=2.5)
            p = d['Close'].iloc[-1]
            
            if rsi <= 31 and p <= bb.iloc[-1, 0]:
                sinais.append({"nome": nome, "ticker": ticker, "tipo": "COMPRA", "cor": "#00ff00", "rsi": rsi})
            elif rsi >= 69 and p >= bb.iloc[-1, 2]:
                sinais.append({"nome": nome, "ticker": ticker, "tipo": "VENDA", "cor": "#ff0000", "rsi": rsi})
        except: continue
    return sinais

# --- COLUNAS ---
col_gestao, col_trade = st.columns([1, 2.5])

with col_gestao:
    st.markdown("### 📡 RADAR QUOTEX")
    lista_sinais = scanner_br()
    if not lista_sinais:
        st.info("🔎 Monitorando EUR/USD e USD/BRL...")
    else:
        for s in lista_sinais:
            st.markdown(f"""
            <div class="radar-card" style="border-left-color:{s['cor']};">
                <b style="color:white; font-size:18px;">{s['nome']}</b><br>
                <span style="color:{s['cor']}; font-weight:900;">SINAL DE {s['tipo']}</span><br>
                <small style="color:#888;">RSI: {s['rsi']:.1f}</small>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)

    # --- CALCULADORA SOROS BR ---
    st.markdown("<div class='soros-box'>", unsafe_allow_html=True)
    st.markdown("### 🇧🇷 GESTÃO DE SOROS")
    banca_br = st.number_input("Banca em R$:", value=500.0)
    risco_br = st.slider("Risco Inicial (%):", 1, 10, 2)
    payout_br = st.number_input("Payout Quotex (%):", value=87)
    
    # Soros Níveis
    m1 = (banca_br * risco_br) / 100
    m2 = m1 + (m1 * (payout_br / 100))
    m3 = m2 + (m2 * (payout_br / 100))

    st.markdown(f"**Entrada 1:** <span class='val-text'>R$ {m1:.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"**Entrada 2:** <span class='val-text'>R$ {m2:.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"**Entrada 3:** <span class='val-text'>R$ {m3:.2f}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_trade:
    selecao = st.selectbox("🎯 ATIVO PRINCIPAL:", list(ativos_foco.keys()))
    ticker_final = ativos_foco[selecao]
    
    # Timer
    seg = 60 - datetime.now().second
    cor_t = "#00ff00" if seg > 10 else "#ff0000"
    st.markdown(f'<div class="timer-display" style="color:{cor_t};">⏳ {seg}s</div>', unsafe_allow_html=True)

    # Gráfico
    df_f = yf.download(ticker_final, period="1d", interval="1m", progress=False)
    if not df_f.empty:
        if isinstance(df_f.columns, pd.MultiIndex): df_f.columns = df_f.columns.get_level_values(0)
        
        
        
        fig = go.Figure(data=[go.Candlestick(x=df_f.index, open=df_f['Open'], high=df_f['High'], low=df_f['Low'], close=df_f['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450, 
                          margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='#000', plot_bgcolor='#000')
        st.plotly_chart(fig, use_container_width=True)

        # Botão Quotex
        ativo_link = selecao.replace("/", "")
        st.link_button(f"🚀 OPERAR {selecao} NA QUOTEX", f"https://qxbroker.com/pt/trade/{ativo_link}", use_container_width=True)

time.sleep(1)
st.rerun()
