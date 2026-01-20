import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="STRANGER AI - SINAL DIRETO", page_icon="⚡", layout="wide")

# --- CSS: DESIGN DE ALTO IMPACTO VISUAL ---
st.markdown("""
    <style>
    .stApp { background-color: #050505 !important; }
    .main-title { color: #ffffff; font-weight: 900; font-size: 35px; text-align: center; margin-top: -60px; }
    
    /* ESTILO DOS CARDS DE SINAL */
    .card-compra {
        background: linear-gradient(135deg, #00c853, #b2ff59);
        color: black !important; padding: 40px; border-radius: 20px;
        text-align: center; border: 5px solid #fff;
        box-shadow: 0 0 50px rgba(0, 200, 83, 0.6);
        animation: pulse 1s infinite;
    }
    .card-venda {
        background: linear-gradient(135deg, #d50000, #ff5252);
        color: white !important; padding: 40px; border-radius: 20px;
        text-align: center; border: 5px solid #fff;
        box-shadow: 0 0 50px rgba(213, 0, 0, 0.6);
        animation: pulse 1s infinite;
    }
    .card-aguarde {
        background: #111; color: #555; padding: 40px; border-radius: 20px;
        text-align: center; border: 2px dashed #333;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .texto-grande { font-size: 50px; font-weight: 900; margin-bottom: 0px; }
    .texto-sub { font-size: 20px; font-weight: 600; }
    </style>
    <h1 class="main-title">STRANGER AI: SINALIZADOR DE ENTRADA</h1>
    """, unsafe_allow_html=True)

# --- MOTOR DE DADOS ---
@st.cache_data(ttl=1)
def get_data_direct(t):
    try:
        d = yf.download(t, period="1d", interval="1m", progress=False)
        if d.empty or len(d) < 30: return None
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        return d[['Open', 'High', 'Low', 'Close']].astype(float).dropna()
    except: return None

# --- ATIVOS ---
ativos = {"EUR/USD": "EURUSD=X", "USD/BRL": "BRL=X", "GBP/USD": "GBPUSD=X", "BTC/USD": "BTC-USD", "GOLD": "GC=F"}

# --- COLUNAS ---
col_menu, col_signal = st.columns([1, 2.5])

with col_menu:
    st.markdown("### ⚙️ CONFIGURAR")
    sel = st.selectbox("ATIVO PARA MONITORAR:", list(ativos.keys()))
    tempo_exp = st.selectbox("TEMPO DE EXPIRAÇÃO:", ["1 MINUTO", "2 MINUTOS", "5 MINUTOS"])
    st.divider()
    st.info("O robô analisa RSI + Bandas de Bollinger em tempo real para dar a direção exata.")

with col_signal:
    df = get_data_direct(ativos[sel])
    
    if df is not None:
        # Indicadores
        c = df['Close'].squeeze()
        rsi = ta.rsi(c, length=5).iloc[-1]
        bb = ta.bbands(c, length=20, std=2.0)
        last_p = c.iloc[-1]
        
        # --- LÓGICA DE DECISÃO VISUAL ---
        # COMPRA: Preço abaixo da Banda Inferior e RSI sobrevendido
        if last_p <= bb.iloc[-1, 0] and rsi < 30:
            st.markdown(f"""
                <div class="card-compra">
                    <p class="texto-sub">{sel} DETECTADO</p>
                    <p class="texto-grande">ABRIR COMPRA ⬆️</p>
                    <p class="texto-sub">CLIQUE NO BOTÃO VERDE NA QUOTEX</p>
                    <hr>
                    <p>Expiração: {tempo_exp}</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/super-mario-power-up.mp3"></audio>', unsafe_allow_html=True)
            
        # VENDA: Preço acima da Banda Superior e RSI sobrecomprado
        elif last_p >= bb.iloc[-1, 2] and rsi > 70:
            st.markdown(f"""
                <div class="card-venda">
                    <p class="texto-sub">{sel} DETECTADO</p>
                    <p class="texto-grande">ABRIR VENDA ⬇️</p>
                    <p class="texto-sub">CLIQUE NO BOTÃO VERMELHO NA QUOTEX</p>
                    <hr>
                    <p>Expiração: {tempo_exp}</p>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('<audio autoplay><source src="https://www.myinstants.com/media/sounds/bell.mp3"></audio>', unsafe_allow_html=True)
            
        else:
            st.markdown(f"""
                <div class="card-aguarde">
                    <p class="texto-grande">AGUARDANDO...</p>
                    <p class="texto-sub">O {sel} ainda não atingiu a zona de entrada.</p>
                    <p style="color:#555;">RSI Atual: {rsi:.2f} | Alvo: <30 ou >70</p>
                </div>
            """, unsafe_allow_html=True)

        # Gráfico de Apoio em baixo
        st.divider()
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=350, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        st.link_button(f"🔗 IR PARA A QUOTEX AGORA", f"https://qxbroker.com/pt/trade/{sel.replace('/','')}", use_container_width=True)

time.sleep(1)
st.rerun()
