import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA FERRAMENTA ---
st.set_page_config(page_title="STRANGER AI - LS", page_icon="⚡", layout="wide")

# --- CSS: ESTILO PREMIUM COM ASSINATURA ---
st.markdown("""
    <style>
    .stApp { background-color: #050505 !important; }
    .footer-ls {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #000; color: #444; text-align: center;
        padding: 10px; font-weight: bold; font-size: 14px;
        border-top: 1px solid #222; z-index: 100;
    }
    .main-title { color: #00ff00; font-weight: 900; font-size: 30px; text-align: center; margin-top: -60px; }
    .dev-tag { color: #ffcc00; font-size: 16px; text-align: center; margin-bottom: 20px; }
    
    .card-compra {
        background: linear-gradient(135deg, #00c853, #004d40);
        color: white !important; padding: 30px; border-radius: 15px;
        text-align: center; border: 3px solid #fff; box-shadow: 0 0 30px #00c853;
    }
    .card-venda {
        background: linear-gradient(135deg, #d50000, #4a148c);
        color: white !important; padding: 30px; border-radius: 15px;
        text-align: center; border: 3px solid #fff; box-shadow: 0 0 30px #d50000;
    }
    .card-neutro {
        background: #111; color: #555; padding: 30px; border-radius: 15px;
        text-align: center; border: 1px dashed #333;
    }
    .countdown-timer { font-size: 40px; font-weight: 900; color: #ffcc00; }
    </style>
    <h1 class="main-title">STRANGER AI SIGNAL</h1>
    <p class="dev-tag">DESENVOLVIDO POR: <b>LUCAS SILVA - LS</b></p>
    """, unsafe_allow_html=True)

# --- LISTA MASSIVA DE ATIVOS (QUOTEX COMPLETA) ---
ativos_ls = {
    # FOREX
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", 
    "USD/BRL": "BRL=X", "AUD/USD": "AUDUSD=X", "EUR/GBP": "EURGBP=X",
    "USD/CAD": "USDCAD=X", "EUR/JPY": "EURJPY=X",
    # AÇÕES
    "FACEBOOK (META)": "META", "APPLE": "AAPL", "TESLA": "TSLA", 
    "GOOGLE": "GOOGL", "AMAZON": "AMZN", "NETFLIX": "NFLX", 
    "MICROSOFT": "MSFT", "NVIDIA": "NVDA", "INTEL": "INTC",
    # CRIPTO & COMMODITIES
    "BITCOIN": "BTC-USD", "ETHEREUM": "ETH-USD", "GOLD": "GC=F", 
    "SILVER": "SI=F", "PETRÓLEO": "CL=F"
}

# --- MOTOR DE DADOS ---
@st.cache_data(ttl=1)
def get_data_ls(t):
    try:
        d = yf.download(t, period="1d", interval="1m", progress=False)
        if d.empty or len(d) < 30: return None
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d[['Open', 'High', 'Low', 'Close']].astype(float).dropna()
    except: return None

if 'sinal_ativo' not in st.session_state: st.session_state.sinal_ativo = None
if 'timer_ls' not in st.session_state: st.session_state.timer_ls = 0

# --- LAYOUT ---
col_menu, col_signal = st.columns([1, 2.5])

with col_menu:
    st.markdown("### 📡 RADAR LS")
    sel = st.selectbox("ATIVO:", list(ativos_ls.keys()))
    st.divider()
    st.write("Configurado para M1 (Retração)")
    
with col_signal:
    agora = time.time()
    df = get_data_ls(ativos_ls[sel])
    
    if df is not None:
        c = df['Close'].squeeze()
        rsi = ta.rsi(c, length=5).iloc[-1]
        bb = ta.bbands(c, length=20, std=2.0)
        last_p = c.iloc[-1]
        
        # Lógica de Captura de Sinal
        if st.session_state.sinal_ativo is None:
            if last_p <= bb.iloc[-1, 0] and rsi < 30:
                st.session_state.sinal_ativo = {"tipo": "COMPRA", "cor": "card-compra", "icon": "⬆️"}
                st.session_state.timer_ls = agora + 15
            elif last_p >= bb.iloc[-1, 2] and rsi > 70:
                st.session_state.sinal_ativo = {"tipo": "VENDA", "cor": "card-venda", "icon": "⬇️"}
                st.session_state.timer_ls = agora + 15

        # Exibição do Sinal
        if st.session_state.sinal_ativo:
            restante = int(st.session_state.timer_ls - agora)
            if restante > 0:
                s = st.session_state.sinal_ativo
                st.markdown(f"""
                    <div class="{s['cor']}">
                        <h2>{sel} - SINAL CONFIRMADO</h2>
                        <h1 style="font-size:60px; margin:0;">{s['tipo']} {s['icon']}</h1>
                        <p class="countdown-timer">{restante}s</p>
                        <p>ENTRE AGORA PARA 1 MINUTO NA QUOTEX</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.session_state.sinal_ativo = None
                st.rerun()
        else:
            st.markdown(f"""
                <div class="card-neutro">
                    <h2>ANALISANDO {sel}...</h2>
                    <p>Aguardando toque na região de suporte ou resistência.</p>
                </div>
            """, unsafe_allow_html=True)

        # Gráfico
        st.divider()
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=350, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        st.link_button(f"🚀 ABRIR {sel} NA QUOTEX", f"https://qxbroker.com/pt/trade/{sel.replace('/','')}", use_container_width=True)

# Rodapé de Assinatura
st.markdown('<div class="footer-ls">STRANGER AI SYSTEM - MADE BY LUCAS SILVA (LS) © 2026</div>', unsafe_allow_html=True)

time.sleep(1)
st.rerun()
