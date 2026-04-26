import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Executive Investor Twin", page_icon="📈", layout="wide")

# 2. MOTOR DE DATOS CON PROTECCIÓN (Caché de 24h)
@st.cache_data(ttl=86400)
def get_executive_data(ticker):
    """Descarga centralizada para evitar bloqueos por exceso de consultas."""
    try:
        tk = yf.Ticker(ticker)
        data = {
            "info": tk.info,
            "financials": tk.quarterly_financials,
            "balance": tk.quarterly_balance_sheet,
            "cashflow": tk.quarterly_cashflow
        }
        return data
    except Exception:
        return None

def safe_get(df, keys, default=0):
    """Evita KeyError buscando múltiples variantes de nombres contables."""
    if df is None or df.empty:
        return pd.Series([default] * 4)
    for key in keys:
        if key in df.index:
            return df.loc[key]
    return pd.Series([default] * len(df.columns), index=df.columns)

# 3. ESTILOS CSS (UI Ejecutiva)
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .card {
        background-color: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 25px;
        border-top: 4px solid #1e293b;
    }
    .metric-title { font-size: 14px; font-weight: 700; color: #64748b; margin-bottom: 15px; }
    .value-main { font-size: 24px; font-weight: 800; color: #0f172a; }
    .status-badge { padding: 4px 10px; border-radius: 5px; font-size: 11px; font-weight: 700; }
    .bg-ok { background-color: #dcfce7; color: #166534; }
    .bg-alert { background-color: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)

# 4. DASHBOARD PRINCIPAL
st.title("📈 Executive Investor Twin v2.0")
t_input = st.text_input("Ingrese Ticker (ej. TSLA, AAPL, MSFT):", value="TSLA").upper()

if t_input:
    raw_data = get_executive_data(t_input)
    
    if raw_data and not raw_data["financials"].empty:
        info = raw_data["info"]
        df_res = raw_data["financials"]
        df_bal = raw_data["balance"]

        # Extracción segura de métricas clave
        rev = safe_get(df_res, ['Total Revenue', 'Operating Revenue'])
        net_inc = safe_get(df_res, ['Net Income'])
        op_inc = safe_get(df_res, ['Operating Income'])
        equity = safe_get(df_bal, ['Stockholders Equity', 'Total Equity Gross Minority Interest'])
        total_debt = safe_get(df_bal, ['Total Debt'], default=0)
        cash = safe_get(df_bal, ['Cash And Cash Equivalents'], default=0)

        # Lógica Financiera: WACC Estimado
        beta = info.get('beta', 1.2)
        ke = 0.043 + (beta * 0.055) # Costo Equity (Rf + Beta * ERP)
        mkt_cap = info.get('marketCap', 1)
        d_val = total_debt.iloc[0] if isinstance(total_debt, pd.Series) else 0
        v_val = mkt_cap + d_val
        tax_rate = 0.21
        wacc = ((mkt_cap/v_val) * ke) + ((d_val/v_val) * 0.06 * (1 - tax_rate))

        # Renderizado de Análisis Trimestral
        st.subheader(f"Análisis de Creación de Valor: {info.get('longName', t_input)}")
        
        for i in range(min(4, len(rev)-1)):
            # Cálculo de ROIC TTM (Simplificado para el Dashboard)
            oi_ttm = op_inc.iloc[i:i+4].sum()
            ic = equity.iloc[i] + d_val - cash.iloc[i]
            roic = (oi_ttm * (1 - tax_rate)) / ic if ic > 0 else 0
            
            crecimiento = ((rev.iloc[i] / rev.iloc[i+1]) - 1) * 100
            m_op = (op_inc.iloc[i] / rev.iloc[i]) * 100
            
            st.markdown(f"""
            <div class="card">
                <div class="metric-title">PERIODO: Q{(rev.index[i].month-1)//3+1} {rev.index[i].year}</div>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; text-align: center;">
                    <div>
                        <div style="color:#64748b; font-size:12px;">REVENUE</div>
                        <div class="value-main">${rev.iloc[i]/1e9:.2f}B</div>
                        <span class="status-badge {'bg-ok' if crecimiento > 5 else 'bg-alert'}">{crecimiento:.1f}% QoQ</span>
                    </div>
                    <div>
                        <div style="color:#64748b; font-size:12px;">M. OPERATIVO</div>
                        <div class="value-main">{m_op:.1f}%</div>
                        <span class="status-badge {'bg-ok' if m_op > 15 else 'bg-alert'}">{'SALUDABLE' if m_op > 15 else 'BAJO'}</span>
                    </div>
                    <div>
                        <div style="color:#64748b; font-size:12px;">ROIC (TTM)</div>
                        <div class="value-main">{roic*100:.1f}%</div>
                        <span class="status-badge {'bg-ok' if roic > wacc else 'bg-alert'}">WACC: {wacc*100:.1f}%</span>
                    </div>
                    <div>
                        <div style="color:#64748b; font-size:12px;">ESTRATEGIA</div>
                        <div class="value-main" style="color:{'#166534' if roic > wacc else '#991b1b'}">
                            {'CREA VALOR' if roic > wacc else 'DESTRUYE'}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No se pudieron recuperar datos. Yahoo Finance podría estar limitando la conexión o el Ticker es inválido.")
                    </div>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.info("Yahoo Finance está procesando tu solicitud. Si el error persiste, espera un par de minutos.")
