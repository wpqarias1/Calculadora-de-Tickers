import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Total Rewards Investor", page_icon="📈")

st.title("🚀 Mi Twin Digital de Inversiones")
st.subheader("Análisis Fundamental de Tesla (TSLA)")

try:
    tk = yf.Ticker("TSLA")
    df_res = tk.quarterly_financials
    df_bal = tk.quarterly_balance_sheet
    
    df_res.index = df_res.index.str.strip()
    df_bal.index = df_bal.index.str.strip()
    
    ventas = df_res.loc['Total Revenue']
    utilidad = df_res.loc['Net Income']
    equity = df_bal.loc['Common Stock Equity'] if 'Common Stock Equity' in df_bal.index else df_bal.loc['Stockholders Equity']
    crecimiento = (ventas.pct_change(periods=-1) * 100).round(2)

    for i in range(4):
        fecha = ventas.index[i]
        monto_b = round(ventas.iloc[i] / 1_000_000_000, 2)
        porc_c = crecimiento.iloc[i]
        u_ttm = utilidad.iloc[i : i+4].sum()
        roe_ttm = round((u_ttm / equity.iloc[i]) * 100, 2)
        
        # Tarjeta visual para cada trimestre
        with st.container():
            st.write(f"### Trimestre: {fecha.date()}")
            col1, col2 = st.columns(2)
            
            # Lógica de colores para Crecimiento
            color_c = "red" if porc_c < 5 else "orange" if porc_c > 20 else "green"
            col1.metric("Crecimiento Ventas", f"{porc_c}%", delta_color="normal")
            st.markdown(f"<p style='color:{color_c}; font-weight:bold;'>Ventas: ${monto_b}B</p>", unsafe_allow_html=True)

            # Lógica de colores para ROE (Tu regla de 12%)
            color_r = "green" if roe_ttm >= 12 else "red"
            st.markdown(f"**ROE TTM:** <span style='color:{color_r}; font-size:20px; font-weight:bold;'>{roe_ttm}%</span>", unsafe_allow_html=True)
            st.divider()

except Exception as e:
    st.error(f"Error al cargar datos: {e}")
