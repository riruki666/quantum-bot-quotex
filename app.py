import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER AI - MODO SOROS", page_icon="🔥", layout="wide")

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
        background: #111; border: 1px solid #333;
        border-radius: 10px; padding: 12px; margin-bottom: 8px;
    }
    .timer-display {
        font-size: 50px; font-weight: 900; text-align: center;
        background: #0a0a0a; padding: 10px;
        border: 2px solid #ff0000; border-radius: 15px;
    }
    .soros-box {
        background: linear-gradient(135deg, #1a1c24 0%, #000 100%);
        padding: 20px; border-radius: 15px;
        border: 2px solid #ffcc00; margin-top: 20px;
    }
    .step-text { font-size: 14px; font-weight: bold; color: #ffcc00; }
    .val-text { font-size: 22px; font-weight: 900; color: #ffffff; }
    
    /* Melhoria de Nitidez nas tabelas e botões */
    .stButton>button {
        font-weight: 900 !important;
        border: 2px solid white !important;
    }
    </style>
    <h1 class="main-title">STRANGER PROFITS SOROS</h1>
    <iframe src="https://www.youtube.com/embed/Av1DFgWLR0E?autoplay=1&loop=1&playlist=Av1DFgWLR0E" 
            width="0" height="0" frameborder="0" allow="autoplay"></iframe>
    """, unsafe_allow_html=True)

# --- BANCO DE ATIVOS EXPANDIDO ---
ativos_monitorados = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "EURJPY=X", "GBPJPY=X",
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD",
    "NVDA", "TSLA", "AAPL", "NFLX", "GC=F", "CL=F"
]

# --- MOTOR DE INTELIGÊNCIA (SCANNER) ---
def scanner_ia():
    sinais = []
    # Varre os ativos principais em busca de exaustão
    for t in ativos_monitorados[:12]:
        try:
            d = yf.download(t, period="1d", interval="1m", progress=False)
            if d.empty: continue
            if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
            
            rsi = ta.rsi(d['Close'], length=14).iloc[-1]
            bb = ta.bbands(d['Close'], length=20, std=2.5)
            p = d['Close'].iloc[-1]
            
            if rsi <= 30 and p <= bb.iloc[-1, 0]:
                sinais.append({"ticker": t, "tipo": "COMPRA", "cor": "#00ff00", "rsi": rsi})
            elif rsi >= 70 and p >= bb.iloc[-1, 2]:
                sinais.append({"ticker": t, "tipo": "VENDA", "cor": "#ff0000", "rsi": rsi})
        except: continue
    return sinais

# --- DIVISÃO DE COLUNAS ---
col_side, col_main = st.columns([1, 2.8])

with col_side:
    st.markdown("### 📡 RADAR DE SINAIS")
    lista_sinais = scanner_ia()
    if not lista_sinais:
        st.info("🔎 Varrendo mercado... Nenhuma falha detectada.")
    else:
        for s in lista_sinais:
            st.markdown(f"""
            <div class="radar-card">
                <b style="color:white; font-size:16px;">{s['ticker'].replace('=X','')}</b><br>
                <span style="color:{s['cor']}; font-weight:900;">{s['tipo']} DETECTADA</span><br>
                <small style="color:#888;">Força RSI: {s['rsi']:.1f}</small>
            </div>
            """, unsafe_allow_html=True)
            # Tocar sino de alerta
            st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)

    # --- CALCULADORA DE SOROS NIVEL 3 ---
    st.markdown("<div class='soros-box'>", unsafe_allow_html=True)
    st.markdown("### 🏆 CALCULADORA SOROS")
    banca_v = st.number_input("Banca Total ($):", value=100.0)
    risco_v = st.slider("Risco da 1ª Mão (%):", 1, 20, 5)
    payout_v = st.number_input("Payout Quotex (%):", value=87)
    
    # Cálculos Matemáticos
    e1 = (banca_v * risco_v) / 100
    l1 = e1 * (payout_v / 100)
    e2 = e1 + l1
    l2 = e2 * (payout_v / 100)
    e3 = e2 + l2
    l3 = e3 * (payout_v / 100)
    alvo_final = l1 + l2 + l3

    st.markdown(f"<span class='step-text'>ENTRADA 1:</span> <span class='val-text'>${e1:.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"<span class='step-text'>SOROS NIVEL 2:</span> <span class='val-text'>${e2:.2f}</span>", unsafe_allow_html=True)
    st.markdown(f"<span class='step-text'>SOROS NIVEL 3:</span> <span class='val-text'>${e3:.2f}</span>", unsafe_allow_html=True)
    st.success(f"LUCRO POTENCIAL: ${alvo_final:.2f}")
    st.markdown("</div>", unsafe_allow_html=True)

with col_main:
    # Seleção de Ativo Principal
    ativo_f = st.selectbox("🎯 ATIVO PARA OPERAÇÃO:", ativos_monitorados)
    
    # Cronómetro de Vela
    seg = 60 - datetime.now().second
    cor_timer = "#00ff00" if seg > 10 else "#ff0000"
    st.markdown(f'<div class="timer-display" style="color:{cor_timer}; border-color:{cor_timer};">⏳ FECHO VELA: {seg}s</div>', unsafe_allow_html=True)

    # Gráfico
    df_f = yf.download(ativo_f, period="1d", interval="1m", progress=False)
    if not df_f.empty:
        if isinstance(df_f.columns, pd.MultiIndex): df_f.columns = df_f.columns.get_level_values(0)
        
        fig = go.Figure(data=[go.Candlestick(x=df_f.index, open=df_f['Open'], high=df_f['High'], low=df_f['Low'], close=df_f['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450, 
                          margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='#000', plot_bgcolor='#000')
        st.plotly_chart(fig, use_container_width=True)

        # Botão de Execução Dinâmico
        link_ticker = ativo_f.replace("=X","").replace("-USD","").replace("=F","")
        st.link_button(f"🔥 EXECUTAR NÍVEL 1 (${e1:.2f}) EM {link_ticker}", f"https://qxbroker.com/pt/trade/{link_ticker}", use_container_width=True)

time.sleep(1)
st.rerun()
