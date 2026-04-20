iimport streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Executive Investor Twin", page_icon="📈", layout="wide")

# 2. ESTILOS CSS REFORZADOS (Optimizado para 5 métricas en móvil)
st.markdown("""
<style>
    .stApp { background-color: #f4f7f6; }
    h1 { color: #1a202c; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; text-align: center; }
    .card {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 8px solid #2d3748;
    }
    .metric-grid { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
    .metric-box { text-align: center; flex: 1; min-width: 65px; }
    .value { font-size: 17px; font-weight: bold; color: #1a202c; margin: 0; }
    .label { font-size: 9px; color: #718096; text-transform: uppercase; font-weight: 700; margin-bottom: 2px; }
    .badge {
        padding: 2px 5px;
        border-radius: 6px;
        color: white;
        font-size: 8px;
        font-weight: bold;
        display: inline-block;
        text-transform: uppercase;
    }
    .bg-red { background-color: #e53e3e; }
    .bg-green { background-color: #38a169; }
    .bg-yellow { background-color: #d69e2e; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🚀 Executive Investor Twin</h1>", unsafe_allow_html=True)

t_input = st.text_input("🔍 Ingresa el Ticker:", value="TSLA").upper()

def format_quarter(dt):
    quarter = (dt.month - 1) // 3 + 1
    return f"Q{quarter} {dt.year}"

if t_input:
    try:
        with st.spinner(f'Calculando Métricas TTM para {t_input}...'):
            tk = yf.Ticker(t_input)
            df_res = tk.quarterly_financials
            df_bal = tk.quarterly_balance_sheet
            info = tk.info
            
            df_res.index = df_res.index.str.strip()
            df_bal.index = df_bal.index.str.strip()
            
            if 'Total Revenue' in df_res.index:
                ventas = df_res.loc['Total Revenue']
                utilidad = df_res.loc['Net Income']
                op_income = df_res.loc['Operating Income']
                equity = df_bal.loc['Common Stock Equity'] if 'Common Stock Equity' in df_bal.index else df_bal.loc['Stockholders Equity']
                total_debt = df_bal.loc['Total Debt'] if 'Total Debt' in df_bal.index else 0
                invested_cap = equity + total_debt

                # Estimación de WACC
                risk_free = 0.042 
                beta = info.get('beta', 1.2)
                market_return = 0.10
                cost_equity = risk_free + beta * (market_return - risk_free)
                wacc_val = round(cost_equity * 100, 2) 

                crecimiento = (ventas.pct_change(periods=-1) * 100).round(2)

                for i in range(min(4, len(ventas)-1)):
                    fecha_q = format_quarter(ventas.index[i])
                    monto_b = round(ventas.iloc[i] / 1e9, 2)
                    porc_c = crecimiento.iloc[i]
                    roe_ttm = round((utilidad.iloc[i:i+4].sum() / equity.iloc[i]) * 100, 2)
                    roic = round((op_income.iloc[i:i+4].sum() / invested_cap.iloc[i]) * 100, 2)
                    
                    # SEMÁFOROS
                    b_c = "bg-red" if porc_c < 3.3 else "bg-yellow" if porc_c > 5.0 else "bg-green"
                    t_c = "ALERTA" if porc_c < 3.3 else "ALTO" if porc_c > 5.0 else "OK"
                    
                    b_roe = "bg-green" if roe_ttm >= 12 else "bg-red"
                    t_roe = "OK" if roe_ttm >= 12 else "BAJO"
                    
                    b_roic_wacc = "bg-green" if roic > wacc_val else "bg-red"
                    status_val = "CREA" if roic > wacc_val else "DESTRUYE"

                    st.markdown(f"""
                    <div class="card">
                        <h3 style="margin:0 0 10px 0; color:#2d3748; font-size:16px;">📊 {fecha_q}</h3>
                        <div class="metric-grid">
                            <div class="metric-box"><p class="label">Ventas</p><p class="value">${monto_b}B</p></div>
                            <div class="metric-box">
                                <p class="label">Crec. QoQ</p><p class="value">{porc_c}%</p>
                                <div class="badge {b_c}">{t_c}</div>
                            </div>
                            <div class="metric-box">
                                <p class="label">ROE TTM</p><p class="value">{roe_ttm}%</p>
                                <div class="badge {b_roe}">{t_roe}</div>
                            </div>
                            <div class="metric-box">
                                <p class="label">WACC</p><p class="value">{wacc_val}%</p>
                            </div>
                            <div class="metric-box">
                                <p class="label">ROIC vs WACC</p><p class="value">{roic}%</p>
                                <div class="badge {b_roic_wacc}">{status_val}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Datos no disponibles.")
    except Exception as e:
        st.error(f"Error: {e}")
