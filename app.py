import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA PREMIUM (Ancha y con Icono Profesional)
st.set_page_config(
    page_title="Executive Investor Twin",
    page_icon="📈",
    layout="wide", # Usa todo el ancho de la pantalla del celular
    initial_sidebar_state="collapsed"
)

# 2. INYECCIÓN DE ESTILO CSS PERSONALIZADO (Aquí está la "magia" visual)
st.markdown("""
<style>
    /* Fondo general de la app */
    .stApp {
        background-color: #f4f7f6;
    }
    
    /* Títulos y Subtítulos más Profesionales */
    h1 {
        color: #1a202c;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
    }
    h3, h4 {
        color: #2d3748;
        font-family: 'Helvetica Neue', sans-serif;
    }

    /* Diseño de la Tarjeta Trimestral (Executive Card) */
    .executive-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 20px;
        border-left: 8px solid #4a5568; /* Borde gris elegante por defecto */
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        margin-bottom: 30px;
        transition: transform 0.2s; /* Efecto sutil al pasar el mouse */
    }
    
    .executive-card:hover {
        transform: translateY(-5px);
    }

    /* Estilo para los Semáforos Profesionales */
    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 50px;
        font-weight: bold;
        color: white;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .badge-green { background-color: #48bb78; } /* Semáforo Verde */
    .badge-red { background-color: #f56565; }   /* Semáforo Rojo */
    .badge-yellow { background-color: #ecc94b; color: #744210; } /* Amarillo con texto oscuro */

    /* Diseño de las Métricas Grandes */
    .metric-value {
        font-size: 36px;
        font-weight: 800;
        color: #1a202c;
        margin: 0;
    }
    .metric-label {
        font-size: 16px;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

</style>
""", unsafe_allow_html=True)

# 3. CABECERA DE LA APP
st.markdown("<h1>🚀 Executive Investor Twin</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#718096; font-size:18px;'>Senior Manager Dashboard | Análisis Fundamental</p>", unsafe_allow_html=True)

try:
    ticker = "TSLA"
    tk = yf.Ticker(ticker)
    df_res = tk.quarterly_financials
    df_bal = tk.quarterly_balance_sheet
    
    # Limpieza de datos (CRÍTICO para evitar errores)
    df_res.index = df_res.index.str.strip()
    df_bal.index = df_bal.index.str.strip()
    
    ventas = df_res.loc['Total Revenue']
    utilidad = df_res.loc['Net Income']
    equity = df_bal.loc['Common Stock Equity'] if 'Common Stock Equity' in df_bal.index else df_bal.loc['Stockholders Equity']
    crecimiento = (ventas.pct_change(periods=-1) * 100).round(2)

    st.markdown(f"<h3>Análisis de Rentabilidad: {ticker}</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True) # Espacio

    # 4. ITERACIÓN Y DISEÑO DE TARJETAS (Executive Cards)
    for i in range(4):
        fecha = ventas.index[i]
        monto_b = round(ventas.iloc[i] / 1e9, 2)
        porc_c = crecimiento.iloc[i]
        u_ttm = utilidad.iloc[i : i+4].sum()
        roe_ttm = round((u_ttm / equity.iloc[i]) * 100, 2)
        
        # Lógica de Semáforos Profesionales (Crecimiento Reglas Originales)
        if pd.isna(porc_c): badge_class_c, text_c = RESET, "PENDIENTE"
        elif porc_c < 5: badge_class_c, text_c = "badge-red", "ALERTA BAJA"
        elif porc_c > 20: badge_class_c, text_c = "badge-yellow", "CREC. ALTO"
        else: badge_class_c, text_c = "badge-green", "SALUDABLE"

        # Lógica de Semáforo Profesional (ROE Regla del 12%)
        if roe_ttm >= 12: 
            badge_class_r, text_r = "badge-green", "EFICIENTE"
        else: 
            badge_class_r, text_r = "badge-red", "BAJO REND."

        # Contenedor de la Tarjeta Ejecutiva
        with st.container():
            st.markdown(f"""
                <div class="executive-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4>📅 Trimestre: {fecha.date()}</h4>
                    </div>
                    <hr style="margin: 15px 0;">
                    
                    <div style="display:flex; justify-content:space-around; text-align:center;">
                        <div>
                            <p class="metric-label">Ventas Totales</p>
                            <p class="metric-value">${monto_b}B</p>
                        </div>
                        <div>
                            <p class="metric-label">Crecimiento QoQ</p>
                            <p class="metric-value">{porc_c}%</p>
                            <span class="status-badge {badge_class_c}">{text_c}</span>
                        </div>
                        <div>
                            <p class="metric-label">ROE TTM (Meta: 12%)</p>
                            <p class="metric-value">{roe_ttm}%</p>
                            <span class="status-badge {badge_class_r}">{text_r}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Esperando actualización de datos... {e}")

# PIE DE PÁGINA
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#a0aec0;'>Datos en tiempo real de Yahoo Finance</p>", unsafe_allow_html=True)
