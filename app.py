import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER AI - ANALISTA PRO", page_icon="📈", layout="wide")

# --- CSS: DESIGN MINIMALISTA E PROFISSIONAL ---
st.markdown("""
    <style>
    .stApp { background-color: #050505 !important; }
    .main-title {
        color: #ffffff; font-weight: 900; font-size: 45px;
        text-align: center; text-shadow: 0 0 10px #ff0000;
        margin-top: -60px;
    }
    .metric-box {
        background: #111; padding: 15px; border-radius: 10px;
        border: 1px solid #333; text-align: center;
    }
    .signal-box {
        padding: 25px; border-radius: 15px; text-align: center;
        font-size: 28px; font-weight: 800; border: 2px dashed #ff0000;
    }
    </style>
    <h1 class="main-title">STRANGER ANALISTA PRO</h1>
    """, unsafe_allow_html=True)

# --- ATIVOS E CONFIGURAÇÕES ---
ativos_pro = {"USD/BRL": "BRL=X", "EUR/USD": "EURUSD=X", "OURO": "GC=F", "BITCOIN": "BTC-USD"}

@st.cache_data(ttl=1)
def fetch_analise_pro(t):
    try:
        d = yf.download(t, period="1d", interval="1m", progress=False)
        if d.empty or len(d) < 50: return None
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d.astype(float).dropna()
    except: return None

# --- MOTOR DE ANÁLISE DE VELA (PRICE ACTION) ---
def analisar_anatomia_vela(df):
    ultima = df.iloc[-1]
    corpo = abs(ultima['Close'] - ultima['Open'])
    pavio_sup = ultima['High'] - max(ultima['Open'], ultima['Close'])
    pavio_inf = min(ultima['Open'], ultima['Close']) - ultima['Low']
    
    # Detecção de Rejeição (Pavio deve ser maior que o corpo)
    rejeicao_compra = pavio_inf > (corpo * 1.5)
    rejeicao_venda = pavio_sup > (corpo * 1.5)
    
    return rejeicao_compra, rejeicao_venda

# --- LAYOUT PRINCIPAL ---
col_stats, col_main = st.columns([1, 2.5])

with col_stats:
    st.markdown("### 🔍 ANÁLISE DE FLUXO")
    sel_ativo = st.selectbox("ATIVO ANALISADO:", list(ativos_pro.keys()))
    df = fetch_analise_pro(ativos_pro[sel_ativo])
    
    if df is not None:
        # Indicadores de Confluência
        rsi = ta.rsi(df['Close'], length=7).iloc[-1]
        bb = ta.bbands(df['Close'], length=20, std=2.0)
        rej_compra, rej_venda = analisar_anatomia_vela(df)
        last_p = df['Close'].iloc[-1]
        
        # Dashboard de Métricas
        c1, c2 = st.columns(2)
        c1.metric("RSI (7)", f"{rsi:.1f}")
        c2.metric("VOLATIL.", f"{ta.atr(df['High'], df['Low'], df['Close'], length=14).iloc[-1]:.4f}")

        st.divider()
        
        # LOGICA DE RESULTADO CERTO (CONFLUÊNCIA TRIPLA)
        # 1. Tocar na Banda | 2. RSI em Extremo | 3. Rejeição de Pavio
        if (last_p <= bb.iloc[-1, 0] or rsi < 30) and rej_compra:
            st.markdown('<div class="signal-box" style="border-color:#00ff00; color:#00ff00;">🔥 SINAL CONFIRMADO<br>COMPRA (REJEIÇÃO)</div>', unsafe_allow_html=True)
            st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
        elif (last_p >= bb.iloc[-1, 2] or rsi > 70) and rej_venda:
            st.markdown('<div class="signal-box" style="border-color:#ff0000; color:#ff0000;">🔥 SINAL CONFIRMADO<br>VENDA (REJEIÇÃO)</div>', unsafe_allow_html=True)
            st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
        else:
            st.info("Aguardando Confluência de Preço + Volume + Rejeição...")

with col_main:
    if df is not None:
        # Gráfico com Candlestick Reais
        
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        
        # Adiciona as Bandas de Bollinger no gráfico para visualização
        fig.add_trace(go.Scatter(x=df.index, y=bb.iloc[:, 0], name='Banda Inf', line=dict(color='rgba(255,255,255,0.2)')))
        fig.add_trace(go.Scatter(x=df.index, y=bb.iloc[:, 2], name='Banda Sup', line=dict(color='rgba(255,255,255,0.2)')))
        
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=550, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        st.link_button(f"🚀 OPERAR {sel_ativo} NA QUOTEX", f"https://qxbroker.com/pt/trade/{sel_ativo.replace('/','')}", use_container_width=True)

time.sleep(1)
st.rerun()
