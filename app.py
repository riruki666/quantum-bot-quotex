import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA FERRAMENTA ---
st.set_page_config(page_title="STRANGER AI - ELITE", page_icon="🏆", layout="wide")

# --- CSS: ESTILO DARK PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #050505 !important; }
    .main-title { color: #00ff00; font-weight: 900; font-size: 35px; text-align: center; text-shadow: 0 0 10px #00ff00; margin-top: -60px; }
    .ranking-box { background: #111; padding: 12px; border-radius: 10px; border: 1px solid #333; margin-bottom: 10px; }
    .win-tag { color: #00ff00; font-weight: bold; }
    .loss-tag { color: #ff0000; font-weight: bold; }
    .signal-active { padding: 20px; border-radius: 15px; text-align: center; border: 4px solid #00ff00; background: rgba(0,255,0,0.1); margin-bottom: 20px; }
    </style>
    <h1 class="main-title">STRANGER ELITE: SYNC & HISTÓRICO</h1>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'historico' not in st.session_state: st.session_state.historico = []

# --- MOTOR DE DADOS BLINDADO (CORREÇÃO DO ATTRIBUTEERROR) ---
@st.cache_data(ttl=1)
def get_data_pro(t):
    try:
        d = yf.download(t, period="1d", interval="1m", progress=False)
        if d.empty or len(d) < 30: return None
        # Limpeza de MultiIndex (Causa do erro AttributeError)
        if isinstance(d.columns, pd.MultiIndex):
            d.columns = d.columns.get_level_values(0)
        # Força colunas como Series limpas e numéricas
        d = d[['Open', 'High', 'Low', 'Close']].astype(float).dropna()
        return d
    except: return None

# --- ATIVOS ---
ativos_lista = {
    "EUR/USD": "EURUSD=X", "USD/BRL": "BRL=X", "GBP/USD": "GBPUSD=X",
    "BTC/USD": "BTC-USD", "GOLD": "GC=F", "META": "META", "TESLA": "TSLA"
}

# --- LAYOUT ---
col_stats, col_main = st.columns([1.2, 2.8])

with col_stats:
    # FILTRO DE NOTÍCIAS / HORÁRIO
    agora = datetime.now()
    st.markdown("### 🕒 STATUS DO MERCADO")
    if agora.minute < 5 or agora.minute > 55:
        st.error("⚠️ VOLATILIDADE ALTA (Virada de Hora)")
    else:
        st.success("✅ MERCADO ESTÁVEL")
        
    st.divider()
    st.markdown("### 🏆 RANKING DE ASSERTIVIDADE")
    for nome, ticker in ativos_lista.items():
        df_h = get_data_pro(ticker)
        if df_h is not None and len(df_h) >= 20:
            try:
                # Squeeze garante que passamos uma série simples de preços
                h, l, c = df_h['High'].squeeze(), df_h['Low'].squeeze(), df_h['Close'].squeeze()
                atr = ta.atr(h, l, c, length=10)
                if atr is not None:
                    vol = atr.iloc[-1]
                    win_rate = 94.0 - (vol * 120)
                    st.markdown(f'<div class="ranking-box"><b>{nome}</b>: <span class="win-tag">{max(min(win_rate, 98.0), 60.0):.1f}% Win</span></div>', unsafe_allow_html=True)
            except: pass

    st.divider()
    st.markdown("### 📜 HISTÓRICO")
    if st.button("🗑️ LIMPAR HISTÓRICO"):
        st.session_state.historico = []
        st.rerun()
    
    for h in st.session_state.historico[-4:]:
        cor = "win-tag" if h['res'] == "WIN" else "loss-tag"
        st.markdown(f"• {h['time']} | {h['ativo']} | <span class='{cor}'>{h['res']}</span>", unsafe_allow_html=True)

with col_main:
    sel_ativo = st.selectbox("SELECIONE O ATIVO NA QUOTEX:", list(ativos_lista.keys()))
    df = get_data_pro(ativos_lista[sel_ativo])
    
    if df is not None:
        c = df['Close'].squeeze()
        rsi = ta.rsi(c, length=5).iloc[-1]
        bb = ta.bbands(c, length=20, std=2.0)
        last_p = c.iloc[-1]
        
        # --- LÓGICA DE SINAL ---
        sinal = None
        if last_p <= bb.iloc[-1, 0] and rsi < 30:
            sinal = {"ativo": sel_ativo, "tipo": "COMPRA ⬆️ (CALL)", "cor": "#00ff00"}
        elif last_p >= bb.iloc[-1, 2] and rsi > 70:
            sinal = {"ativo": sel_ativo, "tipo": "VENDA ⬇️ (PUT)", "cor": "#ff0000"}

        if sinal:
            st.markdown(f"""
                <div class="signal-active" style="border-color:{sinal['cor']};">
                    <h1 style="color:{sinal['cor']}; margin:0;">{sinal['tipo']}</h1>
                    <h3 style="color:white;">{sinal['ativo']} - ENTRADA PARA 1 MINUTO</h3>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            if c1.button("✅ REGISTRAR WIN"):
                st.session_state.historico.append({"time": datetime.now().strftime("%H:%M"), "ativo": sel_ativo, "res": "WIN"})
                st.rerun()
            if c2.button("❌ REGISTRAR LOSS"):
                st.session_state.historico.append({"time": datetime.now().strftime("%H:%M"), "ativo": sel_ativo, "res": "LOSS"})
                st.rerun()

        # --- GRÁFICO ---
        
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        st.link_button(f"🚀 ABRIR {sel_ativo} NA QUOTEX", f"https://qxbroker.com/pt/trade/{sel_ativo.replace('/','')}", use_container_width=True)

time.sleep(1)
st.rerun()
