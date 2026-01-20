import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER AI - PRECISION", page_icon="🎯", layout="wide")

# --- CSS: DESIGN DE ALTA PRECISÃO ---
st.markdown("""
    <style>
    .stApp { background-color: #050505 !important; }
    .main-title {
        color: #ffffff; font-weight: 900; font-size: 40px;
        text-align: center; text-shadow: 0 0 15px #ff0000; margin-top: -60px;
    }
    .timer-box {
        font-size: 50px; font-weight: 900; text-align: center;
        color: #00ff00; background: #111; border: 2px solid #333;
        border-radius: 10px; padding: 5px; margin-bottom: 20px;
    }
    .signal-card {
        padding: 20px; border-radius: 15px; text-align: center;
        font-size: 24px; font-weight: 800; border: 4px solid #fff;
        margin-bottom: 10px;
    }
    .countdown-text { font-size: 35px; color: #ffcc00; font-weight: 900; }
    </style>
    <h1 class="main-title">STRANGER PRECISION AI</h1>
    """, unsafe_allow_html=True)

# --- ESTADOS DA SESSÃO ---
if 'sinal_atual' not in st.session_state: st.session_state.sinal_atual = None
if 'expira_em' not in st.session_state: st.session_state.expira_em = 0

# --- ATIVOS ---
ativos = {
    "EUR/USD": "EURUSD=X", "USD/BRL": "BRL=X", "BTC/USD": "BTC-USD",
    "OURO": "GC=F", "FACEBOOK": "META", "APPLE": "AAPL"
}

@st.cache_data(ttl=1)
def get_live_data(t):
    try:
        d = yf.download(t, period="1d", interval="1m", progress=False)
        if d.empty or len(d) < 30: return None
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d.astype(float).dropna().tail(50)
    except: return None

# --- LAYOUT ---
col_radar, col_chart = st.columns([1.2, 2.8])

with col_radar:
    # Relógio da Vela
    segundos_vela = 60 - datetime.now().second
    st.markdown(f'<div class="timer-box">{segundos_vela:02d}s</div>', unsafe_allow_html=True)
    
    st.markdown("### 📡 SCANNER DE FLUXO")
    
    # Busca novo sinal apenas se não houver um ativo no cronômetro
    if st.session_state.sinal_atual is None:
        for nome, tick in ativos.items():
            df = get_live_data(tick)
            if df is not None:
                rsi = ta.rsi(df['Close'], length=5).iloc[-1]
                bb = ta.bbands(df['Close'], length=20, std=2.0)
                last = df['Close'].iloc[-1]
                
                # Lógica de Reversão Confirmada (Evita comprar em queda livre)
                # Compra: Toca a banda inferior + RSI < 30
                if last <= bb.iloc[-1, 0] and rsi < 30:
                    st.session_state.sinal_atual = {"nome": nome, "tipo": "COMPRA (CALL) ⬆️", "cor": "#00ff00"}
                    st.session_state.expira_em = time.time() + 15 # 15 Segundos para entrar
                    break
                # Venda: Toca a banda superior + RSI > 70
                elif last >= bb.iloc[-1, 2] and rsi > 70:
                    st.session_state.sinal_atual = {"nome": nome, "tipo": "VENDA (PUT) ⬇️", "cor": "#ff0000"}
                    st.session_state.expira_em = time.time() + 15
                    break

    # Exibição do Sinal com Cronômetro de Validade
    if st.session_state.sinal_atual:
        tempo_restante = int(st.session_state.expira_em - time.time())
        
        if tempo_restante > 0:
            s = st.session_state.sinal_atual
            st.markdown(f"""
                <div class="signal-card" style="background:{s['cor']}; color:white;">
                    {s['nome']}<br>{s['tipo']}<br>
                    <span class="countdown-text">{tempo_restante}s</span>
                </div>
                <p style="text-align:center; color:gray;">Após 0s o sinal será descartado.</p>
            """, unsafe_allow_html=True)
            st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
        else:
            st.session_state.sinal_atual = None
            st.rerun()
    else:
        st.write("🔍 Analisando tendências...")

with col_chart:
    sel = st.selectbox("GRÁFICO EM TEMPO REAL:", list(ativos.keys()))
    df_v = get_live_data(ativos[sel])
    
    if df_v is not None:
        fig = go.Figure(data=[go.Candlestick(x=df_v.index, open=df_v['Open'], high=df_v['High'], low=df_v['Low'], close=df_v['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        if st.session_state.sinal_atual:
            st.link_button(f"🚀 ABRIR {st.session_state.sinal_atual['nome']} NA QUOTEX", f"https://qxbroker.com/pt/trade/{st.session_state.sinal_atual['nome'].replace('/','')}", use_container_width=True)

time.sleep(1)
st.rerun()
