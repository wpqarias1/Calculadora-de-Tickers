import streamlit as st
import yfinance as yf
import pandas as pd

# Configuración de la página con tema moderno
st.set_page_config(page_title="Investment Twin", page_icon="📊", layout="wide")

# Estilo personalizado para las tarjetas
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #007bff;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Mi Twin Digital de Inversiones")
st.caption("Senior Manager Dashboard | Análisis Fundamental")

try:
    ticker = "TSLA"
    tk = yf.Ticker(ticker)
    df_res = tk.quarterly_financials
    df_bal = tk.quarterly_balance_sheet
    
    # Limpieza de datos
    df_res.index = df_res.index.str.strip()
    df_bal.index = df_bal.index.str.strip()
    
    ventas = df_res.loc['Total Revenue']
    utilidad = df_res.loc['Net Income']
    equity = df_bal.loc['Common Stock Equity'] if 'Common Stock Equity' in df_bal.index else df_bal.loc['Stockholders Equity']
    crecimiento = (ventas.pct_change(periods=-1) * 100).round(2)

    st.subheader(f"Resumen Trimestral: {ticker}")

    for i in range(4):
        fecha = ventas.index[i]
        monto_b = round(ventas.iloc[i] / 1e9, 2)
        porc_c = crecimiento.iloc[i]
        u_ttm = utilidad.iloc[i : i+4].sum()
        roe_ttm = round((u_ttm / equity.iloc[i]) * 100, 2)
        
        # Crear una "tarjeta" visual por trimestre
        with st.container():
            st.markdown(f"#### 📅 Periodo: {fecha.date()}")
            
            # Dividimos la pantalla en 3 columnas
            c1, c2, c3 = st.columns(3)
            
            # Columna 1: Ventas
            c1.metric("Ventas Totales", f"${monto_b}B")
            
            # Columna 2: Crecimiento (Semáforo)
            color_c = "normal" if 5 <= porc_c <= 20 else "inverse"
            c2.metric("Crecimiento QoQ", f"{porc_c}%", delta=f"{porc_c}%", delta_color=color_c)
            
            # Columna 3: ROE TTM (Semáforo 12%)
            emoji_roe = "🟢" if roe_ttm >= 12 else "🔴"
            c3.markdown(f"**ROE TTM**")
            c3.subheader(f"{emoji_roe} {roe_ttm}%")
            
            st.divider()

except Exception as e:
    st.error(f"Esperando actualización de datos... {e}")

st.info("💡 Consejo: Los datos se actualizan automáticamente desde Yahoo Finance.")
