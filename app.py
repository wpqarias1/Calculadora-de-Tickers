# Asegúrate de que este bloque st.markdown esté alineado con el 'for' superior
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
        st.warning("No se pudieron recuperar datos. Verifica el Ticker.")
