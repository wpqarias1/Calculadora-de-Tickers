import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURACIÓN Y CACHÉ (La solución al Rate Limit)
st.set_page_config(page_title="Executive Investor Twin", page_icon="📈", layout="wide")

# Función con caché para no saturar a Yahoo Finance
@st.cache_data(ttl=3600) # Guarda los datos por 1 hora (3600 segundos)
def get_stock_data(ticker):
    tk = yf.Ticker(ticker)
    # Forzamos la descarga de lo necesario
    res = tk.quarterly_financials
    bal = tk.quarterly_balance_sheet
    inf = tk.info
    return res, bal, inf

# 2. ESTILOS CSS
st.markdown("""
<style>
    .stApp { background-color: #f4f7f6; }
    .card {
        background-color: white; padding: 15px; border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px;
        border-left: 6px solid #2d3748;
    }
    .metric-row { display: flex; justify-content: space-between; margin-bottom: 10px; text-align: center; }
    .metric-box { flex: 1; }
    .label { font-size: 10px; color: #718096; text-transform: uppercase; font-weight: bold; }
    .value { font-size: 18px; font-weight: bold; color: #1a202c; display: block; }
    .badge { padding: 2px 8px; border-radius: 4px; color: white; font-size: 10px; font-weight: bold; text-transform: uppercase; }
    .bg-red { background-color: #e53e3e; }
    .bg-green { background-color: #38a169; }
    .bg-yellow { background-color: #d69e2e; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 Executive Investor Twin")

t_input = st.text_input("🔍 Ingresa el Ticker:", value="TSLA").upper()

if t_input:
    try:
        # Llamada a la función con caché
        df_res, df_bal, info = get_stock_data(t_input)
        
        if not df_res.empty:
            df_res.index = df_res.index.str.strip()
            df_bal.index = df_bal.index.str.strip()
            
            rev = df_res.loc['Total Revenue']
            net_inc = df_res.loc['Net Income']
            op_inc = df_res.loc['Operating Income']
            gross_prof = df_res.loc['Gross Profit'] if 'Gross Profit' in df_res.index else rev
            equity = df_bal.loc['Common Stock Equity'] if 'Common Stock Equity' in df_bal.index else df_bal.loc['Stockholders Equity']
            total_debt = df_bal.loc['Total Debt'] if 'Total Debt' in df_bal.index else 0
            
            wacc_val = round((0.042 + info.get('beta', 1.2) * (0.10 - 0.042)) * 100, 2)
            crecimiento = (rev.pct_change(periods=-1) * 100).round(2)

            for i in range(min(4, len(rev)-1)):
                m_bruto = round((gross_prof.iloc[i] / rev.iloc[i]) * 100, 2)
                m_op = round((op_inc.iloc[i] / rev.iloc[i]) * 100, 2)
                m_neto = round((net_inc.iloc[i] / rev.iloc[i]) * 100, 2)
                roe_ttm = round((net_inc.iloc[i:i+4].sum() / equity.iloc[i]) * 100, 2)
                ic = equity.iloc[i] + (total_debt.iloc[i] if isinstance(total_debt, pd.Series) else total_debt)
                roic = round((op_inc.iloc[i:i+4].sum() / ic) * 100, 2)
                
                # Colores (M. Neto > 5%)
                c_crec = "bg-red" if crecimiento.iloc[i] < 3.3 else "bg-yellow" if crecimiento.iloc[i] > 5 else "bg-green"
                c_roe = "bg-green" if roe_ttm >= 12 else "bg-red"
                c_roic = "bg-green" if roic > wacc_val else "bg-red"
                c_bruto = "bg-green" if m_bruto >= 20 else "bg-red"
                c_op = "bg-green" if m_op >= 10 else "bg-red"
                c_neto = "bg-green" if m_neto >= 5 else "bg-red"

                st.markdown(f"""
                <div class="card">
                    <div style="font-weight:bold; margin-bottom:10px;">📊 Q{(rev.index[i].month-1)//3+1} {rev.index[i].year}</div>
                    <div class="metric-row">
                        <div class="metric-box"><span class="label">Ventas</span><span class="value">${round(rev.iloc[i]/1e9,1)}B</span></div>
                        <div class="metric-box"><span class="label">Crec. QoQ</span><span class="value">{crecimiento.iloc[i]}%</span><span class="badge {c_crec}">STATUS</span></div>
                        <div class="metric-box"><span class="label">ROE TTM</span><span class="value">{roe_ttm}%</span><span class="badge {c_roe}">ROE</span></div>
                        <div class="metric-box"><span class="label">ROIC/WACC</span><span class="value">{roic}%</span><span class="badge {c_roic}">{roic>wacc_val and 'CREA' or 'DESTRUYE'}</span></div>
                    </div>
                    <hr style="margin:10px 0; border:0; border-top:1px solid #eee;">
                    <div class="metric-row">
                        <div class="metric-box"><span class="label">M. Bruto (>20%)</span><span class="value">{m_bruto}%</span><span class="badge {c_bruto}">{m_bruto>=20 and 'OK' or 'BAJO'}</span></div>
                        <div class="metric-box"><span class="label">M. Op (>10%)</span><span class="value">{m_op}%</span><span class="badge {c_op}">{m_op>=10 and 'OK' or 'ALERTA'}</span></div>
                        <div class="metric-box"><span class="label">M. Neto (>5%)</span><span class="value">{m_neto}%</span><span class="badge {c_neto}">{m_neto>=5 and 'OK' or 'ALERTA'}</span></div>
                        <div class="metric-box"><span class="label">WACC</span><span class="value">{wacc_val}%</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.info("Yahoo Finance está procesando tu solicitud. Si el error persiste, espera un par de minutos.")
