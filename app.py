import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER PROFITS - SNIPER MODE", page_icon="🎯", layout="wide")

# --- CSS: DESIGN MILITAR DE ALTA PRECISÃO ---
st.markdown("""
    <style>
    .stApp { background-color: #050505 !important; }
    .main-title {
        color: #ff0000; font-weight: 900; font-size: 55px;
        text-align: center; text-shadow: 0 0 20px #ff0000;
        margin-top: -60px;
    }
    .sniper-box {
        background: rgba(255, 0, 0, 0.1); border: 2px solid #ff0000;
        padding: 20px; border-radius: 15px; text-align: center;
    }
    .timer-sniper {
        font-size: 60px; font-weight: 900; color: #00ff00;
        text-shadow: 0 0 15px #00ff00; text-align: center;
    }
    .metric-card { background: #111; border-radius: 10px; padding: 15px; border: 1px solid #333; }
    </style>
    <h1 class="main-title">STRANGER SNIPER AI</h1>
    <iframe src="https://www.youtube.com/embed/Av1DFgWLR0E?autoplay=1&loop=1&playlist=Av1DFgWLR0E" 
            width="0" height="0" frameborder="0" allow="autoplay"></iframe>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÃO DE ATIVOS SNIPER ---
ativos_sniper = {"EUR/USD": "EURUSD=X", "USD/BRL": "BRL=X", "BTC/USD": "BTC-USD", "GOLD": "GC=F"}

if 'win_rate' not in st.session_state: st.session_state.win_rate = {"wins": 0, "total": 0}

# --- MOTOR DE CONFLUÊNCIA QUÁDRUPLA ---
def scanner_sniper():
    oportunidades = []
    for nome, ticker in ativos_sniper.items():
        try:
            d = yf.download(ticker, period="1d", interval="1m", progress=False)
            if d.empty: continue
            if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
            
            # INDICADORES FORÇADOS
            rsi_fast = ta.rsi(d['Close'], length=2).iloc[-1] # RSI Ultra-rápido
            stoch = ta.stoch(d['High'], d['Low'], d['Close'], k=5, d=3).iloc[-1]
            bb = ta.bbands(d['Close'], length=20, std=3.0) # Desvio 3.0 (Exaustão Máxima)
            preco = d['Close'].iloc[-1]
            
            # CONDIÇÃO SNIPER (100% CONFLUÊNCIA)
            # Compra: RSI < 10 + Stochastic < 20 + Preço < Banda Inferior 3.0
            if rsi_fast < 10 and stoch[0] < 20 and preco <= bb.iloc[-1, 0]:
                oportunidades.append({"nome": nome, "tipo": "CALL (COMPRA)", "cor": "#00ff00", "p": preco})
            # Venda: RSI > 90 + Stochastic > 80 + Preço > Banda Superior 3.0
            elif rsi_fast > 90 and stoch[0] > 80 and preco >= bb.iloc[-1, 2]:
                oportunidades.append({"nome": nome, "tipo": "PUT (VENDA)", "cor": "#ff0000", "p": preco})
        except: continue
    return oportunidades

# --- COLUNAS ---
col_stats, col_viz = st.columns([1, 2.5])

with col_stats:
    st.markdown("### 🎯 RADAR SNIPER")
    sinais = scanner_sniper()
    
    if not sinais:
        st.write("🔎 Varrendo mercado por exaustão extrema...")
    else:
        for s in sinais:
            st.markdown(f"""
            <div class="sniper-box" style="border-color:{s['cor']};">
                <h2 style="color:{s['cor']};">{s['tipo']}</h2>
                <h1 style="color:white;">{s['nome']}</h1>
                <p>EXECUÇÃO IMEDIATA</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
            st.session_state.win_rate['total'] += 1 # Simulação de registro

    # CALCULADORA SOROS ELITE
    st.markdown("---")
    banca = st.number_input("Banca Atual:", value=100.0)
    entrada = banca * 0.10
    st.info(f"Entrada Recomendada: R$ {entrada:.2f}")

with col_viz:
    sel = st.selectbox("ATIVO EM FOCO:", list(ativos_sniper.keys()))
    seg = 60 - datetime.now().second
    st.markdown(f'<div class="timer-sniper">{seg}s</div>', unsafe_allow_html=True)

    df_viz = yf.download(ativos_sniper[sel], period="1d", interval="1m", progress=False)
    if not df_viz.empty:
        if isinstance(df_viz.columns, pd.MultiIndex): df_viz.columns = df_viz.columns.get_level_values(0)
        
        
        
        fig = go.Figure(data=[go.Candlestick(x=df_viz.index, open=df_viz['Open'], high=df_viz['High'], low=df_viz['Low'], close=df_viz['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450, 
                          margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='#000', plot_bgcolor='#000')
        st.plotly_chart(fig, use_container_width=True)

        link_q = sel.replace("/", "")
        st.link_button(f"🚀 ABRIR {sel} NA QUOTEX", f"https://qxbroker.com/pt/trade/{link_q}", use_container_width=True)

time.sleep(1)
st.rerun()
