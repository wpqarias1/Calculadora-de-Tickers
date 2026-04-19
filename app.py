import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Executive Investor Twin", page_icon="📈", layout="wide")

# 2. ESTILOS CSS (Mejorados para evitar el error anterior)
st.markdown("""
<style>
    .stApp { background-color: #f4f7f6; }
    h1 { color: #1a202c; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #4a5568;
    }
    .metric-box { text-align: center; padding: 10px; }
    .value { font-size: 28px; font-weight: bold; color: #2d3748; margin: 0; }
    .label { font-size: 14px; color: #718096; text-transform: uppercase; margin-bottom: 5px; }
    .badge {
        padding: 4px 12px;
        border-radius: 20px;
        color: white;
        font-size: 12px;
        font-weight: bold;
    }
    .bg-red { background-color: #f56565; }
    .bg-green { background-color: #48bb78; }
    .bg-yellow { background-color: #ecc94b; color: #744210; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Executive Investor Twin")
st.caption("Senior Manager Dashboard | Análisis Fundamental")

try:
    ticker = "TSLA"
    tk = yf.Ticker(ticker)
    df_res = tk.quarterly_financials
    df_bal = tk.quarterly_balance_sheet
    
    df_res.index = df_res.index.str.strip()
    df_bal.index = df_bal.index.str.strip()
    
    ventas = df_res.loc['Total Revenue']
    utilidad = df_res.loc['Net Income']
    equity = df_bal.loc['Common Stock Equity'] if 'Common Stock Equity' in df_bal.index else df_bal.loc['Stockholders Equity']
    crecimiento = (ventas.pct_change(periods=-1) * 100).round(2)

    st.subheader(f"Análisis de Rentabilidad: {ticker}")

    for i in range(4):
        fecha = ventas.index[i]
        monto_b = round(ventas.iloc[i] / 1e9, 2)
        porc_c = crecimiento.iloc[i]
        u_ttm = utilidad.iloc[i : i+4].sum()
        roe_ttm = round((u_ttm / equity.iloc[i]) * 100, 2)
        
        # Lógica de Semáforos
        if pd.isna(porc_c): b_c, t_c = "bg-yellow", "PENDIENTE"
        elif porc_c < 5: b_c, t_c = "bg-red", "ALERTA BAJA"
        elif porc_c > 20: b_c, t_c = "bg-yellow", "CREC. ALTO"
        else: b_c, t_c = "bg-green", "SALUDABLE"

        b_r, t_r = ("bg-green", "EFICIENTE") if roe_ttm >= 12 else ("bg-red", "BAJO REND.")

        # RENDERIZADO USANDO MARKDOWN (Más estable para Streamlit)
        st.markdown(f"""
        <div class="card">
            <h4 style="margin-top:0;">📅 Trimestre: {fecha.date()}</h4>
            <div style="display: flex; justify-content: space-around;">
                <div class="metric-box">
                    <p class="label">Ventas</p>
                    <p class="value">${monto_b}B</p>
                </div>
                <div class="metric-box">
                    <p class="label">Crecimiento</p>
                    <p class="value">{porc_c}%</p>
                    <span class="badge {b_c}">{t_c}</span>
                </div>
                <div class="metric-box">
                    <p class="label">ROE TTM</p>
                    <p class="value">{roe_ttm}%</p>
                    <span class="badge {b_r}">{t_r}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error cargando datos: {e}")
