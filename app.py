import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Executive Investor Twin", page_icon="📈", layout="wide")

# 2. ESTILOS CSS
st.markdown("""
<style>
    .stApp { background-color: #f4f7f6; }
    h1 { color: #1a202c; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; text-align: center; }
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

# 3. BUSCADOR
t_input = st.text_input("🔍 Ingresa el Ticker:", value="TSLA").upper()

def format_quarter(dt):
    quarter = (dt.month - 1) // 3 + 1
    return f"Q{quarter} {dt.year}"

if t_input:
    try:
        with st.spinner(f'Analizando {t_input}...'):
            tk = yf.Ticker(t_input)
            df_res = tk.quarterly_financials
            df_bal = tk.quarterly_balance_sheet
            
            df_res.index = df_res.index.str.strip()
            df_bal.index = df_bal.index.str.strip()
            
            if 'Total Revenue' in df_res.index and 'Net Income' in df_res.index:
                ventas = df_res.loc['Total Revenue']
                utilidad = df_res.loc['Net Income']
                equity = df_bal.loc['Common Stock Equity'] if 'Common Stock Equity' in df_bal.index else df_bal.loc['Stockholders Equity']
                
                crecimiento = (ventas.pct_change(periods=-1) * 100).round(2)

                st.subheader(f"Resultados para {t_input}")

                for i in range(min(4, len(ventas)-1)):
                    fecha_q = format_quarter(ventas.index[i])
                    monto_b = round(ventas.iloc[i] / 1e9, 2)
                    porc_c = crecimiento.iloc[i]
                    
                    u_ttm = utilidad.iloc[i : i+4].sum()
                    roe_ttm = round((u_ttm / equity.iloc[i]) * 100, 2)
                    
                    # TUS REGLAS ESPECÍFICAS DE COLOR PARA VENTAS
                    if pd.isna(porc_c):
                        b_c, t_c = "bg-yellow", "N/A"
                    elif porc_c < 3.3:
                        b_c, t_c = "bg-red", "ALERTA"
                    elif porc_c > 5.0:
                        b_c, t_c = "bg-yellow", "ALTO"
                    else:
                        b_c, t_c = "bg-green", "OK"

                    # ROE TTM (Meta 12%)
                    b_r, t_r = ("bg-green", "EFICIENTE") if roe_ttm >= 12 else ("bg-red", "BAJO")

                    # TARJETA FINAL (CERRADA CORRECTAMENTE)
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
            else:
                st.warning(f"La empresa {t_input} no tiene suficientes datos financieros trimestrales.")

    except Exception as e:
        st.error(f"Error técnico: {e}")
