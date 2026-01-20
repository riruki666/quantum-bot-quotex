import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER AI - QUOTEX FULL", page_icon="💰", layout="wide")

# --- CSS: ESTILO PROFISSIONAL E SCANNÁVEL ---
st.markdown("""
    <style>
    .stApp { background-color: #050505 !important; }
    .main-title {
        color: #00ff00; font-weight: 900; font-size: 40px;
        text-align: center; text-shadow: 0 0 15px #00ff00; margin-top: -60px;
    }
    .card-ativo {
        background: #111; padding: 10px; border-radius: 8px;
        border: 1px solid #333; margin-bottom: 5px;
    }
    .signal-buy { background: #004400; border: 2px solid #00ff00; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; }
    .signal-sell { background: #440000; border: 2px solid #ff0000; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; }
    </style>
    <h1 class="main-title">STRANGER QUOTEX EXPLORER</h1>
    """, unsafe_allow_html=True)

# --- LISTA COMPLETA DE ATIVOS QUOTEX (FOREX, STOCKS, CRYPTO, COMMODITIES) ---
ativos_quotex = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", 
    "USD/BRL": "BRL=X", "AUD/USD": "AUDUSD=X", "EUR/GBP": "EURGBP=X",
    "FACEBOOK (META)": "META", "APPLE": "AAPL", "GOOGLE": "GOOGL", 
    "AMAZON": "AMZN", "NETFLIX": "NFLX", "MICROSOFT": "MSFT", 
    "TESLA": "TSLA", "BITCOIN": "BTC-USD", "ETHEREUM": "ETH-USD",
    "OURO (GOLD)": "GC=F", "PRATA (SILVER)": "SI=F", "PETRÓLEO (CRUDE)": "CL=F"
}

# --- MOTOR DE DADOS OTIMIZADO ---
@st.cache_data(ttl=1)
def fetch_full_data(t):
    try:
        d = yf.download(t, period="1d", interval="1m", progress=False)
        if d.empty or len(d) < 30: return None
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d.astype(float).dropna().tail(60)
    except: return None

# --- SIDEBAR: GESTÃO DE GANHOS ---
if 'profit_total' not in st.session_state: st.session_state.profit_total = 0.0
with st.sidebar:
    st.header("💰 GESTÃO DE BANCA")
    meta = st.number_input("Meta de Ganho ($):", value=50.0)
    loss_limit = st.number_input("Stop Loss ($):", value=20.0)
    st.divider()
    st.metric("LUCRO NA SESSÃO", f"$ {st.session_state.profit_total:.2f}")
    
    if st.session_state.profit_total >= meta:
        st.success("✅ META ATINGIDA! PARE!")
    elif st.session_state.profit_total <= -loss_limit:
        st.error("❌ LIMITE DE PERDA! PARE!")

# --- LAYOUT PRINCIPAL ---
col_radar, col_chart = st.columns([1.3, 2.7])

with col_radar:
    st.markdown("### 📡 RADAR DE ATIVOS")
    
    # Botão para forçar atualização
    if st.button("🔄 ATUALIZAR SCANNER"): st.rerun()
    
    # Loop rápido de Scanner
    for nome, ticker in ativos_quotex.items():
        df = fetch_full_data(ticker)
        if df is not None:
            # Indicadores Rápidos (Agresividade Média)
            rsi = ta.rsi(df['Close'], length=7).iloc[-1]
            bb = ta.bbands(df['Close'], length=20, std=2.0)
            last = df['Close'].iloc[-1]
            
            # Condições de Suporte/Resistência Automáticos
            res_diaria = df['High'].max()
            sup_diaria = df['Low'].min()
            
            if rsi < 32 or last <= bb.iloc[-1, 0] or last <= sup_diaria:
                st.markdown(f'<div class="signal-buy">{nome}<br>CALL (COMPRA) 🚀</div>', unsafe_allow_html=True)
            elif rsi > 68 or last >= bb.iloc[-1, 2] or last >= res_diaria:
                st.markdown(f'<div class="signal-sell">{nome}<br>PUT (VENDA) 🔥</div>', unsafe_allow_html=True)
            else:
                # Exibe o ativo em modo neutro para saber que está funcionando
                st.markdown(f'<div class="card-ativo">{nome}: Neutro</div>', unsafe_allow_html=True)

with col_chart:
    sel_ativo = st.selectbox("FOCO NO GRÁFICO:", list(ativos_quotex.keys()))
    df_v = fetch_full_data(ativos_quotex[sel_ativo])
    
    if df_v is not None:
        fig = go.Figure(data=[go.Candlestick(x=df_v.index, open=df_v['Open'], high=df_v['High'], low=df_v['Low'], close=df_v['Close'])])
        
        # Desenha Linhas de S/R Automáticas do Ativo Selecionado
        fig.add_hline(y=df_v['High'].max(), line_dash="dot", line_color="red", annotation_text="RESISTÊNCIA")
        fig.add_hline(y=df_v['Low'].min(), line_dash="dot", line_color="green", annotation_text="SUPORTE")
        
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        # Botões de Resultado para o Indicador de Ganhos
        c_win, c_loss = st.columns(2)
        if c_win.button("✅ REGISTRAR WIN"): st.session_state.profit_total += 10.0 # Exemplo de valor fixo
        if c_loss.button("❌ REGISTRAR LOSS"): st.session_state.profit_total -= 10.0

        st.link_button(f"🔗 OPERAR {sel_ativo} NA QUOTEX", f"https://qxbroker.com/pt/trade/{sel_ativo.replace('/','')}")

time.sleep(2) # Pausa leve para não sobrecarregar o Yahoo
st.rerun()
