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
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 8px solid #2d3748;
    }
    .metric-grid { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 5px; }
    .metric-box { text-align: center; flex: 1; min-width: 60px; }
    .value { font-size: 15px; font-weight: bold; color: #1a202c; margin: 0; }
    .label { font-size: 8px; color: #718096; text-transform: uppercase; font-weight: 700; margin-bottom: 1px; }
    .badge {
        padding: 1px 4px;
        border-radius: 4px;
        color: white;
        font-size: 7px;
        font-weight: bold;
        display: inline-block;
        text-transform: uppercase;
    }
    .bg-red { background-color: #e53e3e; }
    .bg-green { background-color: #38a169; }
    .bg-yellow { background-color: #d69e2e; }
    .section-divider { border-top: 1px solid #edf2f7; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🚀 Executive Investor Twin</h1>", unsafe_allow_html=True)

t_input = st.text_input("🔍 Ingresa el Ticker:", value="TSLA").upper()

def format_quarter(dt):
    quarter = (dt.month - 1) // 3 + 1
    return f"Q{quarter} {dt.year}"

if t_input:
    try:
        with st.spinner(f'Analizando Márgenes de Excelencia para {t_input}...'):
            tk = yf.Ticker(t_input)
            df_res = tk.quarterly_financials
            df_bal = tk.quarterly_balance_sheet
            info = tk.info
            
            df_res.index = df_res.index.str.strip()
            df_bal.index = df_bal.index.str.strip()
            
            if 'Total Revenue' in df_res.index:
                rev = df_res.loc['Total Revenue']
                net_inc = df_res.loc['Net Income']
                op_inc = df_res.loc['Operating Income']
                gross_prof = df_res.loc['Gross Profit'] if 'Gross Profit' in df_res.index else (rev - df_res.loc['Cost Of Revenue'] if 'Cost Of Revenue' in df_res.index else rev * 0)
                equity = df_bal.loc['Common Stock Equity'] if 'Common Stock Equity' in df_bal.index else df_bal.loc['Stockholders Equity']
                total_debt = df_bal.loc['Total Debt'] if 'Total Debt' in df_bal.index else 0
                invested_cap = equity + total_debt

                # WACC Estimado
                risk_free = 0.042 
                beta = info.get('beta', 1.2)
                wacc_val = round((risk_free + beta * (0.10 - risk_free)) * 100, 2) 

                crecimiento = (rev.pct_change(periods=-1) * 100).round(2)

                for i in range(min(4, len(rev)-1)):
                    # Cálculos de Márgenes
                    m_bruto = round((gross_prof.iloc[i] / rev.iloc[i]) * 100, 2)
                    m_op = round((op_inc.iloc[i] / rev.iloc[i]) * 100, 2)
                    m_neto = round((net_inc.iloc[i] / rev.iloc[i]) * 100, 2)
                    
                    roe_ttm = round((net_inc.iloc[i:i+4].sum() / equity.iloc[i]) * 100, 2)
                    roic = round((op_inc.iloc[i:i+4].sum() / invested_cap.iloc[i]) * 100, 2)
                    
                    # SEMÁFOROS EXISTENTES
                    b_c = "bg-red" if crecimiento.iloc[i] < 3.3 else "bg-yellow" if crecimiento.iloc[i] > 5.0 else "bg-green"
                    b_roe = "bg-green" if roe_ttm >= 12 else "bg-red"
                    b_roic = "bg-green" if roic > wacc_val else "bg-red"
                    
                    # NUEVOS SEMÁFOROS DE ALTA RENTABILIDAD
                    b_mbruto = "bg-green" if m_bruto >= 40 else "bg-red"
                    b_mop = "bg-green" if m_op >= 20 else "bg-red"
                    b_mneto = "bg-green" if m_neto >= 15 else "bg-red"

                    st.markdown(f"""
                    <div class="card">
                        <h3 style="margin:0 0 10px 0; color:#2d3748; font-size:15px;">📊 {format_quarter(rev.index[i])}</h3>
                        
                        <div class="metric-grid">
                            <div class="metric-box"><p class="label">Ventas</p><p class="value">${round(rev.iloc[i]/1e9,2)}B</p></div>
                            <div class="metric-box"><p class="label">Crec. QoQ</p><p class="value">{crecimiento.iloc[i]}%</p><div class="badge {b_c}">STATUS</div></div>
                            <div class="metric-box"><p class="label">ROE TTM</p><p class="value">{roe_ttm}%</p><div class="badge {b_roe}">ROE</div></div>
                            <div class="metric-box"><p class="label">ROIC vs WACC</p><p class="value">{roic}%</p><div class="badge {b_roic}">{roic > wacc_val and 'CREA' or 'DESTRUYE'}</div></div>
                        </div>
                        
                        <div class="section-divider"></div>
                        
                        <div class="metric-grid">
                            <div class="metric-box"><p class="label">M. Bruto (>40%)</p><p class="value">{m_bruto}%</p><div class="badge {b_mbruto}">{m_bruto >= 40 and 'EXCELENTE' or 'BAJO'}</div></div>
                            <div class="metric-box"><p class="label">M. Operativo (>20%)</p><p class="value">{m_op}%</p><div class="badge {b_mop}">{m_op >= 20 and 'EFICIENTE' or 'ALERTA'}</div></div>
                            <div class="metric-box"><p class="label">M. Neto (>15%)</p><p class="value">{m_neto}%</p><div class="badge {b_mneto}">{m_neto >= 15 and 'PREMIUM' or 'ALERTA'}</div></div>
                            <div class="metric-box"><p class="label">WACC</p><p class="value">{wacc_val}%</p></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Datos no disponibles.")
    except Exception as e:
        st.error(f"Error: {e}")
