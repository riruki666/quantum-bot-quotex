import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER AI - PREDADOR M1", page_icon="🎯", layout="wide")

# --- CSS: INTERFACE PROFISSIONAL ---
st.markdown("""
    <style>
    .stApp { background-color: #020202 !important; }
    .main-title {
        color: #ff0000; font-weight: 900; font-size: 50px;
        text-align: center; text-shadow: 0 0 15px #ff0000;
        margin-top: -60px;
    }
    .status-panel {
        padding: 20px; border-radius: 15px; border: 2px solid #333;
        text-align: center; margin-bottom: 10px;
    }
    .timer-m1 {
        font-size: 65px; font-weight: 900; color: #00ff00;
        text-align: center; background: #111; border-radius: 20px;
    }
    .meta-msg { font-size: 22px; font-weight: 800; text-align: center; padding: 10px; border-radius: 10px; }
    </style>
    <h1 class="main-title">STRANGER PREDADOR M1</h1>
    <audio autoplay loop><source src="https://www.myinstants.com/media/sounds/stranger-things-theme-song-hd.mp3"></audio>
    """, unsafe_allow_html=True)

# --- SISTEMA DE GESTÃO DE GANHOS (STOP-GAIN/LOSS) ---
if 'saldo_atual' not in st.session_state: st.session_state.saldo_atual = 0.0

with st.sidebar:
    st.header("💰 GESTÃO DE BANCA")
    banca_inicial = st.number_input("Banca Inicial ($):", value=100.0)
    meta_diaria = st.number_input("Meta de Ganho (Stop Gain $):", value=20.0)
    limite_perda = st.number_input("Limite de Perda (Stop Loss $):", value=10.0)
    
    lucro_sessao = st.session_state.saldo_atual
    progresso = (lucro_sessao / meta_diaria) if lucro_sessao > 0 else 0.0
    
    st.divider()
    st.metric("LUCRO NA SESSÃO", f"$ {lucro_sessao:.2f}", delta=f"{lucro_sessao:.2f}")
    
    if lucro_sessao >= meta_diaria:
        st.markdown("<div class='meta-msg' style='background: #2eb85c; color: white;'>✅ META BATIDA! PARE AGORA!</div>", unsafe_allow_html=True)
        st.balloons()
    elif lucro_sessao <= -limite_perda:
        st.markdown("<div class='meta-msg' style='background: #e55353; color: white;'>❌ STOP LOSS ATINGIDO! VOLTE AMANHÃ!</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='meta-msg' style='background: #333; color: #ccc;'>Operando em Busca da Meta...</div>", unsafe_allow_html=True)

# --- ANALISADOR DE VELAS (PRICE ACTION) ---
def analisar_velas_sniper(df):
    ultima = df.iloc[-1]
    penultima = df.iloc[-2]
    
    # Detecção de Pavio de Exaustão (Rejeição de Preço)
    corpo = abs(ultima['Close'] - ultima['Open'])
    pavio_superior = ultima['High'] - max(ultima['Open'], ultima['Close'])
    pavio_inferior = min(ultima['Open'], ultima['Close']) - ultima['Low']
    
    # Filtros Técnicos Forçados
    rsi = ta.rsi(df['Close'], length=2).iloc[-1]
    bb = ta.bbands(df['Close'], length=20, std=3.0)
    
    # Lógica Sniper 100%
    if rsi < 8 and pavio_inferior > corpo and ultima['Close'] <= bb.iloc[-1, 0]:
        return "COMPRA (CALL) 🔥", "#00ff00"
    elif rsi > 92 and pavio_superior > corpo and ultima['Close'] >= bb.iloc[-1, 2]:
        return "VENDA (PUT) 🔥", "#ff0000"
    return "AGUARDANDO...", "#333"

# --- ÁREA PRINCIPAL ---
col_1, col_2 = st.columns([1, 2.5])

ativos = {"EUR/USD": "EURUSD=X", "USD/BRL": "BRL=X", "BTC/USD": "BTC-USD"}
ativo_sel = st.selectbox("ATIVO:", list(ativos.keys()))

with col_1:
    segundos = 60 - datetime.now().second
    cor_timer = "#00ff00" if segundos > 10 else "#ff0000"
    st.markdown(f'<div class="timer-m1" style="color:{cor_timer};">{segundos}s</div>', unsafe_allow_html=True)
    
    df = yf.download(ativos[ativo_sel], period="1d", interval="1m", progress=False)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        sinal, cor_sinal = analisar_velas_sniper(df)
        st.markdown(f"""
            <div class="status-panel" style="border-color:{cor_sinal};">
                <h3 style="color:{cor_sinal};">{sinal}</h3>
                <p style="color:#888;">Análise de Velas M1 Ativa</p>
            </div>
        """, unsafe_allow_html=True)
        
        if sinal != "AGUARDANDO...":
            st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)

with col_2:
    if not df.empty:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        # Botões de Simulação de Resultado (Para a Gestão)
        c_win, c_loss = st.columns(2)
        if c_win.button("✅ REGISTRAR WIN"):
            st.session_state.saldo_atual += (banca_inicial * 0.05) * 0.87 # Ganho médio
        if c_loss.button("❌ REGISTRAR LOSS"):
            st.session_state.saldo_atual -= (banca_inicial * 0.05)

        st.link_button(f"🚀 ABRIR {ativo_sel} NA QUOTEX", f"https://qxbroker.com/pt/trade/{ativo_sel.replace('/','')}", use_container_width=True)

time.sleep(1)
st.rerun()
