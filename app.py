import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz
import requests
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="QUANTUM BOT - Pro", layout="wide")

# --- ESTILO VISUAL PREMIUM ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #31333f; }
    .status-box { padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px; border: 2px solid #31333f; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE DADOS (CORRIGIDA PARA EVITAR TYPEERROR) ---
@st.cache_data(ttl=10)
def buscar_dados_seguro(ticker, intervalo):
    try:
        dados = yf.download(ticker, period="2d", interval=intervalo, progress=False, threads=False)
        
        # Correção crucial para o erro de 'MultiIndex' do yfinance
        if isinstance(dados.columns, pd.MultiIndex):
            dados.columns = dados.columns.get_level_values(0)
            
        if dados.empty or len(dados) < 30:
            return None
        return dados
    except:
        return None

def analisar_estatisticas(df):
    if df is None: return 0, 50, 0, 0
    
    # Cálculos de Indicadores
    df['RSI'] = ta.rsi(df['Close'], length=14)
    bb = ta.bbands(df['Close'], length=20, std=2)
    
    # Extração de valores (Garantindo que sejam números simples)
    preco = float(df['Close'].iloc[-1])
    rsi = float(df['RSI'].iloc[-1])
    sup = float(df['Low'].rolling(window=20).min().iloc[-1])
    res = float(df['High'].rolling(window=20).max().iloc[-1])
    banda_inf = float(bb['BBL_20_2.0'].iloc[-1])
    banda_sup = float(bb['BBU_20_2.0'].iloc[-1])
    
    # Lógica de Sinal
    pontos = 0
    if (preco <= banda_inf or preco <= sup) and rsi < 35:
        pontos = 1 # Compra
    elif (preco >= banda_sup or preco >= res) and rsi > 65:
        pontos = -1 # Venda
    
    return pontos, rsi, sup, res

# --- SIDEBAR ---
if 'wins' not in st.session_state: st.session_state.wins = 0
if 'losses' not in st.session_state: st.session_state.losses = 0

st.sidebar.title("🎮 Quantum Control")
par = st.sidebar.selectbox("Ativo:", ["BTC-USD", "ETH-USD", "EURUSD=X", "GBPUSD=X", "AUDUSD=X"])
st.sidebar.subheader(f"🏆 Placar: {st.session_state.wins}W - {st.session_state.losses}L")

c1, c2 = st.sidebar.columns(2)
if c1.button("✅ WIN"): st.session_state.wins += 1
if c2.button("❌ LOSS"): st.session_state.losses += 1

# Timer
segundos = datetime.now().second
restante = 60 - segundos
st.sidebar.metric("Próxima Vela", f"{restante}s")

# --- CORPO PRINCIPAL ---
st.title("📊 QUANTUM BOT - Operacional")

df_m1 = buscar_dados_seguro(par, "1m")
df_m5 = buscar_dados_seguro(par, "5m")

# Verificação de segurança antes de exibir
if df_m1 is not None and not df_m1.empty and 'Close' in df_m1.columns:
    p_m1, rsi_val, sup_val, res_val = analisar_estatisticas(df_m1)
    p_m5, _, _, _ = analisar_estatisticas(df_m5)

    # Confluência de Sinal
    sinal = "AGUARDANDO OPORTUNIDADE"
    cor_box = "#1e2130"
    
    if p_m1 == 1 and p_m5 == 1:
        sinal, cor_box = "🔥 COMPRA FORTE (CALL)", "#004d26"
    elif p_m1 == -1 and p_m5 == -1:
        sinal, cor_box = "❄️ VENDA FORTE (PUT)", "#4d0000"

    st.markdown(f"""<div class="status-box" style="background-color: {cor_box};">
                <h1 style="color: white; margin:0;">{sinal}</h1></div>""", unsafe_allow_html=True)

    # Métricas
    m1, m2, m3 = st.columns(3)
    m1.metric("Preço", f"{df_m1['Close'].iloc[-1]:.5f}")
    m2.metric("RSI (14)", f"{rsi_val:.2f}")
    m3.metric("Zonas", f"S:{sup_val:.4f} | R:{res_val:.4f}")

    # Gráfico
    fig = go.Figure(data=[go.Candlestick(
        x=df_m1.index, open=df_m1['Open'], high=df_m1['High'],
        low=df_m1['Low'], close=df_m1['Close']
    )])
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=10, r=10, t=10, b=10), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("📡 Conectando ao mercado... Se for final de semana, use BTC-USD.")
    if st.button("Recarregar"):
        st.rerun()

st.caption("Quantum Bot v1.2 - Otimizado")
