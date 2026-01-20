import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="STRANGER AI - SNIPER TIME", page_icon="⏱️", layout="wide")

# --- CSS: DESIGN DE ALTA PRECISÃO ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    .main-title {
        color: #ff0000; font-weight: 900; font-size: 50px;
        text-align: center; text-shadow: 0 0 20px #ff0000;
        margin-top: -60px;
    }
    .timer-vela {
        font-size: 60px; font-weight: 900; text-align: center;
        color: #00ff00; background: #111; border: 3px solid #333;
        border-radius: 15px; margin-bottom: 10px;
    }
    .card-oportunidade {
        background: #111; padding: 20px; border-radius: 15px;
        text-align: center; border: 3px solid #ffcc00; margin-bottom: 15px;
    }
    .expired-text { color: #ff0000; font-weight: bold; font-size: 20px; }
    </style>
    <h1 class="main-title">STRANGER SNIPER TIME</h1>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADO ---
if 'sinal_ativo' not in st.session_state:
    st.session_state.sinal_ativo = None
if 'tempo_expiracao' not in st.session_state:
    st.session_state.tempo_expiracao = 0

# --- ATIVOS ---
ativos_config = {
    "USD/BRL": {"tick": "BRL=X", "std": 1.5, "rsi": 3},
    "EUR/USD": {"tick": "EURUSD=X", "std": 1.5, "rsi": 3},
    "FACEBOOK": {"tick": "META", "std": 2.0, "rsi": 7}
}

@st.cache_data(ttl=1)
def get_data_sniper(t):
    try:
        d = yf.download(t, period="1d", interval="1m", progress=False)
        if d.empty or len(d) < 20: return None
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d.astype(float).dropna()
    except: return None

# --- COLUNAS ---
col_radar, col_view = st.columns([1.2, 2.8])

with col_radar:
    # Cronômetro da Vela Atual
    agora = datetime.now()
    sec_vela = 60 - agora.second
    st.markdown(f'<div class="timer-vela">{sec_vela:02d}s</div>', unsafe_allow_html=True)
    
    # SCANNER DE NOVOS SINAIS
    st.markdown("### 📡 BUSCANDO ENTRADA")
    
    # Se não houver sinal ativo, varre o mercado
    if st.session_state.sinal_ativo is None:
        for nome, c in ativos_config.items():
            df = get_data_sniper(c["tick"])
            if df is not None:
                cp = df['Close'].squeeze()
                rsi = ta.rsi(cp, length=c["rsi"]).iloc[-1]
                bb = ta.bbands(cp, length=20, std=c["std"])
                last = cp.iloc[-1]
                
                # Critério de Entrada
                tipo = None
                if rsi < 35 or last <= bb.iloc[-1, 0]: tipo = "COMPRA (CALL) ⬆️"
                elif rsi > 65 or last >= bb.iloc[-1, 2]: tipo = "VENDA (PUT) ⬇️"
                
                if tipo:
                    st.session_state.sinal_ativo = {"nome": nome, "tipo": tipo, "cor": "#00ff00" if "COMPRA" in tipo else "#ff0000"}
                    st.session_state.tempo_expiracao = time.time() + 15 # 15 segundos de vida
                    st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/ding-sound-effect_2.mp3"></audio>', unsafe_allow_html=True)
                    break # Foca em um sinal por vez
    
    # EXIBIÇÃO DO SINAL COM CRONÔMETRO DE EXPIRAÇÃO
    if st.session_state.sinal_ativo:
        tempo_restante = int(st.session_state.tempo_expiracao - time.time())
        
        if tempo_restante > 0:
            s = st.session_state.sinal_ativo
            st.markdown(f"""
                <div class="card-oportunidade" style="border-color:{s['cor']};">
                    <h2 style="color:{s['cor']};">{s['nome']}</h2>
                    <h3 style="color:white;">{s['tipo']}</h3>
                    <hr>
                    <p style="color:#ffcc00; font-size:18px;">ENTRE AGORA NA QUOTEX!</p>
                    <h1 style="color:#ffcc00;">{tempo_restante}s</h1>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Tempo esgotou, remove o sinal
            st.session_state.sinal_ativo = None
            st.rerun()

with col_view:
    sel = st.selectbox("GRÁFICO DE MONITORAMENTO:", list(ativos_config.keys()))
    df_v = get_data_sniper(ativos_config[sel]["tick"])
    if df_v is not None:
        
        fig = go.Figure(data=[go.Candlestick(x=df_v.index, open=df_v['Open'], high=df_v['High'], low=df_v['Low'], close=df_v['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    if st.session_state.sinal_ativo:
        link_ativo = st.session_state.sinal_ativo['nome'].replace('/','')
        st.link_button(f"🔥 EXECUTAR {st.session_state.sinal_ativo['nome']} AGORA", f"https://qxbroker.com/pt/trade/{link_ativo}", use_container_width=True)

time.sleep(1)
st.rerun()
