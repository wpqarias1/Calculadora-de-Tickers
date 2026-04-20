import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Executive Investor Twin", page_icon="📈", layout="wide")

# 2. ESTILOS CSS REFORZADOS
st.markdown("""
<style>
    .stApp { background-color: #f4f7f6; }
    h1 { color: #1a202c; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; text-align: center; margin-bottom: 0px; }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border-left: 8px solid #2d3748;
    }
    .metric-box { text-align: center; width: 33%; }
    .value { font-size: 24px; font-weight: bold; color: #1a202c; margin: 0; }
    .label { font-size: 11px; color: #718096; text-transform: uppercase; font-weight: 600; margin-bottom: 5px; }
    .badge {
        padding: 4px 10px;
        border-radius: 12px;
        color: white;
        font-size: 11px;
        font-weight: bold;
        display: inline-block;
        margin-top: 5px;
    }
    .bg-red { background-color: #e53e3e; }
    .bg-green { background-color: #38a169; }
    .bg-yellow { background-color: #d69e2e; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🚀 Executive Investor Twin</h1>", unsafe_allow_html=True)

# 3. BARRA DE BÚSQUEDA (Ticker Selector)
ticker_input = st.text_input("🔍 Ingresa el Ticker (ej: TSLA, AAPL, NVDA, MSFT):", value="TSLA").upper()

# Función para convertir fecha a Formato Q
def format_quarter(dt):
    quarter = (dt.month - 1) // 3 + 1
    return f"Q{quarter} {dt.year}"

if ticker_input:
    try:
        with st.spinner(f'Analizando {ticker_input}...'):
            tk = yf.Ticker(ticker_input)
            df_res = tk.quarterly_financials
            df_bal = tk.quarterly_balance_sheet
            
            # Limpieza y validación de etiquetas
            df_res.index = df_res.index.str.strip()
            df_bal.index = df_bal.index.str.strip()
            
            if 'Total Revenue' not in df_res.index or 'Net Income' not in df_res.index:
                st.warning(f"No hay suficientes datos financieros públicos para {ticker_input}.")
            else:
                ventas = df_res.loc['Total Revenue']
                utilidad = df_res.loc['Net Income']
                equity = df_bal.loc['Common Stock Equity'] if 'Common Stock Equity' in df_bal.index else df_bal.loc['Stockholders Equity']
                
                # Crecimiento QoQ
                crecimiento = (ventas.pct_change(periods=-1) * 100).round(2)

                st.subheader(f"Dashboard de Rentabilidad: {ticker_input}")

                for i in range(min(4, len(ventas)-1)):
                    fecha_q = format_quarter(ventas.index[i])
                    monto_b = round(ventas.iloc[i] / 1e9, 2)
                    porc_c = crecimiento.iloc[i]
                    
                    # Cálculo ROE TTM (Manejo de data histórica corta)
                    u_ttm = utilidad.iloc[i : i+4].sum()
                    roe_ttm = round((u_ttm / equity.iloc[i]) * 100, 2)
                    
                    # Lógica de Semáforos
                    if pd.isna(porc_c): b_c, t_c = "bg-yellow", "N/A"
                    elif porc_c < 5: b_c, t_c = "bg-red", "ALERTA"
                    elif porc_c > 20: b_c, t_c = "bg-yellow", "ALTO"
                    else: b_c, t_c = "bg-green", "OK"

                    b_r, t_r = ("bg-green", "EFICIENTE") if roe_ttm >= 12 else ("bg-red", "BAJO")

                    # Tarjeta Ejecutiva
                    st.markdown(f"""
                    <div class="card">
                        <h3 style="margin:0 0 15px 0; color:#2d3748; font-size:20px;">📊 {fecha_q}</h3>
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div class="metric-box">
                                <p class="label">Ventas</p>
                                <p class="value">${monto_b}B</p>
                            </div>
                            <div class="metric-box">
                                <p class="label">Crec. QoQ</p>
                                <p class="value">{porc_c}%</p>
                                <div class="badge {b_c}">{t_c}</div>
                            </div>
                            <div class="metric-box">
                                <p class="label">ROE TTM</p>
                                <p class="value">{roe_ttm}%</p>
                                <div class="badge {b_r}">{t_r}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"El ticker '{ticker_input}' no es válido o no tiene datos disponibles.")
