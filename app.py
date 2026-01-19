import streamlit as st
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURAÇÃO DA PÁGINA (Com Favicon Temático) ---
st.set_page_config(
    page_title="UPSIDE DOWN TRADER",
    page_icon="https://i.ibb.co/C5fJvM2/vecna-icon.png", # Ícone do relógio do Vecna
    layout="wide"
)

# --- FUNÇÃO SOM, CÓPIA E REDIRECIONAMENTO (JS) ---
def acao_sinal(nome_para_copiar):
    sound_url = "https://www.myinstants.com/media/sounds/vecna-clock-sound-effect.mp3"
    corretora_url = "https://qxbroker.com/pt/demo-trade"
    
    js_code = f"""
        <script>
        function executarAcao() {{
            navigator.clipboard.writeText("{nome_para_copiar}");
            var audio = new Audio("{sound_url}");
            audio.play();
            window.open("{corretora_url}", "_blank");
        }}
        </script>
        <div onclick="executarAcao()" style="background: linear-gradient(135deg, #8b0000 0%, #ff4500 100%); color: white; padding: 20px; border-radius: 15px; text-align: center; cursor: pointer; font-weight: bold; border: 4px solid #fff; box-shadow: 0 0 25px rgba(255,0,0,0.7); margin-top: 20px; font-size: 22px;">
            <span style="font-family: 'Creepster', cursive;">⏳ CLIQUE PARA ESCAPAR: COPIAR "{nome_para_copiar}" & ABRIR CORRETORA</span>
        </div>
    """
    st.components.v1.html(js_code, height=120)

# --- ESTILO VISUAL STRANGER THINGS ---
st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Creepster&family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
    .main {{
        background-color: #050000;
        background-image: url('https://i.ibb.co/D8d3j8K/upside-down-bg.jpg'); /* Fundo do Mundo Invertido */
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    h1, h2, h3, .st-b5, .stMetric, .stSelectbox label, .stRadio label {{
        font-family: 'Press Start 2P', cursive;
        color: #ff0000 !important; /* Vermelho sangue */
        text-shadow: 2px 2px 5px rgba(0,0,0,0.8);
    }}
    .signal-card {{ padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 15px; border: 2px solid #500; }}
    .buy {{ background: linear-gradient(135deg, #004d1a 0%, #00ff55 100%); color: #fff; box-shadow: 0 0 20px #0f0; }}
    .sell {{ background: linear-gradient(135deg, #4d0000 0%, #ff0000 100%); color: #fff; box-shadow: 0 0 20px #f00; }}
    .wait {{ background-color: rgba(10, 0, 0, 0.7); color: #880000; border: 1px dashed #500; }}
    .timer-text {{ font-family: 'Press Start 2P', cursive; font-size: 65px; font-weight: bold; color: #ff0000; text-align: center; text-shadow: 0 0 15px #f00; margin-top: 10px; }}
    .stMetric {{ background-color: rgba(10, 0, 0, 0.8); border: 1px solid #ff0000; color: #ff0000; }}
    .stMetric label {{ color: #ff8888 !important; }}
    .stSelectbox div[data-baseweb="select"] {{ background-color: rgba(10,0,0,0.9); border: 1px solid #ff0000; color: #ff0000; }}
    .stSelectbox div[data-baseweb="select"] div {{ color: #ff0000; }}
    .stRadio div[role="radiogroup"] {{ background-color: rgba(10,0,0,0.9); border-radius: 10px; padding: 10px; border: 1px solid #ff0000; }}
    .stRadio div[role="radiogroup"] label {{ color: #ff8888; }}
    </style>
    """, unsafe_allow_html=True)

# --- BUSCA DE DADOS ---
@st.cache_data(ttl=5)
def buscar_dados(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(col).capitalize() for col in df.columns]
        return df.dropna()
    except: return None

# --- SIDEBAR (MUNDO INVERTIDO) ---
st.sidebar.title("🕰️ UPSIDE DOWN PORTAL")
categoria = st.sidebar.radio("Ativos da Dimensão:", ["Ações (Stocks)", "Criptomoedas", "Forex (Moedas)", "Commodities"])

if categoria == "Ações (Stocks)":
    lista_ativos = {
        "McDonald's": "MCD", "Coca-Cola": "KO", "Amazon": "AMZN",
        "Apple": "AAPL", "Tesla": "TSLA", "NVIDIA": "NVDA",
        "Netflix": "NFLX", "Disney": "DIS", "Microsoft": "MSFT"
    }
elif categoria == "Criptomoedas":
    lista_ativos = {
        "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Solana": "SOL-USD",
        "Ripple (XRP)": "XRP-USD", "Cardano": "ADA-USD"
    }
elif categoria == "Forex (Moedas)":
    lista_ativos = {
        "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
        "AUD/USD": "AUDUSD=X", "EUR/GBP": "EURGBP=X", "USD/CAD": "CAD=X"
    }
else: # Commodities
    lista_ativos = {
        "Ouro (Gold)": "GC=F", "Prata (Silver)": "SI=F", "Petróleo": "CL=F"
    }

nome_exibicao = st.sidebar.selectbox("Selecione o Ativo:", list(lista_ativos.keys()))
par_original = lista_ativos[nome_exibicao]
nome_limpo = par_original.replace("-USD", "").replace("=X", "").replace("=F", "")

# --- LÓGICA PRINCIPAL ---
df = buscar_dados(par_original)

if df is not None and len(df) > 14:
    try:
        rsi = float(ta.rsi(df['Close'], length=14).iloc[-1])
        bb = ta.bbands(df['Close'], length=20, std=2.5)
        preco = float(df['Close'].iloc[-1])
        
        sinal = 0
        if preco <= bb.iloc[-1, 0] and rsi < 30: sinal = 1 
        elif preco >= bb.iloc[-1, 2] and rsi > 70: sinal = -1

        st.markdown(f'<h1 style="text-align:center;">{nome_exibicao}</h1>', unsafe_allow_html=True)
        
        # SINAL E BOTÃO
        if sinal != 0:
            cor_classe = "buy" if sinal == 1 else "sell"
            texto_sinal = "⬆️ COMPRE (CALL)" if sinal == 1 else "⬇️ VENDA (PUT)"
            st.markdown(f'<div class="signal-card {cor_classe}"><h2>{texto_sinal}</h2></div>', unsafe_allow_html=True)
            acao_sinal(nome_limpo) # Botão com ação JS
        else:
            st.markdown('<div class="signal-card wait"><h2>⌛ AGUARDANDO SINAL...</h2></div>', unsafe_allow_html=True)

        # TIMER E MÉTRICAS
        segundos_restantes = 60 - datetime.now().second
        st.markdown(f'<div class="timer-text">{segundos_restantes}s</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        col1.metric("Preço Atual", f"{preco:.4f}")
        col2.metric("Força RSI", f"{rsi:.0f}%")

        # GRÁFICO
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(
            template="plotly_dark", 
            xaxis_rangeslider_visible=False, 
            height=350, 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Press Start 2P", color="#ff0000"),
            xaxis=dict(gridcolor='rgba(255,0,0,0.2)'),
            yaxis=dict(gridcolor='rgba(255,0,0,0.2)')
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao carregar os dados. Tente outro ativo. Detalhes: {e}")
    
    time.sleep(1)
    st.rerun()
else:
    st.markdown('<h1 style="text-align:center; color:#ff0000; font-family: \'Press Start 2P\', cursive;">PORTAL PARA O UPSIDE DOWN ABRINDO...</h1>', unsafe_allow_html=True)
    st.info(f"Sincronizando {nome_exibicao}. Verifique se o mercado está aberto.")
    time.sleep(3)
    st.rerun()

st.sidebar.markdown("""
    <div style="text-align:center; color:#ff8888; font-family: 'Press Start 2P', cursive; font-size: 10px; margin-top: 30px;">
        BY QUANTUM TRADER 🕰️
    </div>
""", unsafe_allow_html=True)
