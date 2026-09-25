import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Importamos las funciones del motor financiero
from utils.engine import (
    get_all_tickers, download_market_data, calculate_daily_returns, 
    optimize_portfolio, optimize_hrp, calculate_portfolio_metrics, 
    calculate_historical_performance, calculate_efficient_frontier_points,
    calculate_advanced_metrics
)

st.set_page_config(page_title="Mi Cartera Óptima", page_icon="pie_chart", layout="wide")

# --- CSS PARA OCULTAR LA BARRA LATERAL NATIVA ---
st.markdown("""
    <style>
    /* Oculta los enlaces de navegación automáticos de Streamlit */
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Oculta toda la barra lateral completamente para ganar el 100% del ancho */
    [data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# --- MENÚ DE NAVEGACIÓN SUPERIOR HORIZONTAL ---
col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)

with col_nav1:
    st.page_link("app.py", label="Inicio", icon="🏠")
with col_nav2:
    # Ajusta el nombre del archivo si en tu carpeta se llama distinto
    st.page_link("pages/1_profile_survey.py", label="Perfilado de Riesgo", icon="📋")
with col_nav3:
    st.page_link("pages/2_portfolio.py", label="Mi Cartera Óptima", icon="📊")
with col_nav4:
    st.page_link("pages/3_monte_carlo.py", label="Simulación Estocástica", icon="🔮")

st.markdown("---")

# --- CSS PERSONALIZADO PARA EL CENTRADO DEL SPINNER ---
st.markdown("""
    <style>
    /* Forzar que el círculo clásico de carga (spinner) aparezca en el centro exacto */
    div[data-testid="stSpinner"] {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 20vh; /* Empuja el spinner hacia el centro vertical de la pantalla */
        margin-bottom: 20vh;
    }
    /* Aumentar ligeramente el tamaño del texto del spinner para darle presencia */
    div[data-testid="stSpinner"] > div > div {
        font-size: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Análisis y Optimización de Cartera")

# Validación de seguridad del estado
if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
    st.warning("⚠️ Aún no has definido tu perfil de riesgo. Por favor, ve a la página '1 Profile Survey'.")
    st.stop()

perfil = st.session_state.user_profile
puntuacion = st.session_state.total_score

def perfil_color(p):
    if p == "Conservador": return "blue"
    if p == "Moderado": return "orange"
    return "red"

# --- CONTROLES EN LA BARRA SUPERIOR (Sustituye a la barra lateral) ---
st.markdown("### ⚙️ Configuración del Modelo")

# Usamos columnas para crear una barra horizontal elegante y equilibrada
col_info, col_control = st.columns([1, 2])

with col_info:
    st.info(f"**Tu Perfil Asignado:** :{perfil_color(perfil)}[**{perfil}**] *(Puntuación: {puntuacion} pts)*")

with col_control:
    metodo_opt = st.radio(
        "Selecciona el Algoritmo de Optimización:",
        options=["Teoría Moderna (Markowitz / CVaR)", "Enfoque Avanzado (HRP / Machine Learning)"],
        horizontal=True, # Convierte el menú en una barra horizontal
        label_visibility="collapsed" # Ocultamos el label porque ya es intuitivo
    )

st.markdown("---")

# Contenedor vacío donde volcaremos los resultados. 
# Esto asegura que el spinner sea lo único que se vea en el centro de la pantalla mientras carga.
contenedor_resultados = st.empty()

with st.spinner('📡 Ejecutando modelos cuantitativos y descargando datos de mercado...'):
    try:
        # 1. Ingesta de datos del Asset Pool y del Benchmark (SPY)
        tickers = get_all_tickers()
        precios = download_market_data(tickers, start_date="2019-01-01")
        retornos = calculate_daily_returns(precios)
        
        precios_benchmark = download_market_data(["SPY"], start_date="2019-01-01")
        retornos_benchmark = calculate_daily_returns(precios_benchmark)
        
        # 2. Lógica Condicional: Optimización
        if metodo_opt == "Teoría Moderna (Markowitz / CVaR)":
            pesos = optimize_portfolio(retornos, perfil)
        else:
            pesos = optimize_hrp(retornos)
        
        # Procesamiento de pesos para gráficos
        pesos_limpios = pesos[pesos['weights'] >= 0.01].copy()
        pesos_limpios['weights'] = pesos_limpios['weights'] * 100 
        
        # 3. Cálculo de métricas base y proyecciones
        retorno, riesgo, sharpe = calculate_portfolio_metrics(pesos, retornos)
        backtest = calculate_historical_performance(pesos, retornos)
        df_frontera, medida_riesgo = calculate_efficient_frontier_points(retornos, perfil)
        
        # 4. Preparación para Métricas Avanzadas
        retorno_diario_cartera = (retornos * pesos['weights'].values).sum(axis=1)
        metricas = calculate_advanced_metrics(retorno_diario_cartera, retornos_benchmark)
        
        calculo_exitoso = True
    except Exception as e:
        st.error(f"Error crítico durante la ejecución de los modelos: {e}")
        calculo_exitoso = False

# Renderizamos todo el panel dentro del contenedor una vez que los cálculos han finalizado
if calculo_exitoso:
    with contenedor_resultados.container():
        # --- BLOQUE 1: VISUALIZACIÓN PRINCIPAL ---
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Composición Sugerida")
            fig_donut = px.pie(
                pesos_limpios, values='weights', names=pesos_limpios.index, 
                hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_donut.update_traces(textposition='inside', textinfo='percent+label')
            fig_donut.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_donut, use_container_width=True)
            
            st.subheader("Métricas Clave")
            st.metric(label="Rentabilidad Esperada (Anual)", value=f"{retorno * 100:.2f} %")
            
            if metodo_opt == "Teoría Moderna (Markowitz / CVaR)" and perfil == "Conservador":
                label_riesgo = "Riesgo Anualizado (CVaR 95%)"
            else:
                label_riesgo = "Riesgo Anualizado (Volatilidad)"
                
            st.metric(label=label_riesgo, value=f"{riesgo * 100:.2f} %")
            st.metric(label="Ratio de Sharpe", value=f"{sharpe:.2f}")

        with col2:
            st.subheader("Ubicación en la Frontera Eficiente")
            fig_frontier = px.line(
                df_frontera, x='Riesgo', y='Retorno',
                labels={'Riesgo': 'Volatilidad (%)', 'Retorno': 'Rentabilidad Esperada (%)'},
                title="Comparativa de la Cartera Frente a la Frontera de Markowitz"
            )
            fig_frontier.update_traces(line=dict(color='grey', width=2, dash='dash'))
            
            nombre_marcador = f"Tu Cartera ({perfil})" if metodo_opt == "Teoría Moderna (Markowitz / CVaR)" else "Cartera HRP Avanzada"
            fig_frontier.add_scatter(
                x=[riesgo * 100], 
                y=[retorno * 100], 
                mode='markers',
                marker=dict(color='gold', size=16, symbol='star', line=dict(color='black', width=1.5)),
                name=nombre_marcador
            )
            fig_frontier.update_layout(margin=dict(t=40, b=10, l=10, r=10))
            st.plotly_chart(fig_frontier, use_container_width=True)
            
            st.subheader("Evolución Histórica (Backtest)")
            fig_line = px.line(
                backtest, 
                labels={'value': 'Capital Acumulado (Base 1)', 'Date': 'Fecha'}
            )
            fig_line.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_line, use_container_width=True)

        # --- BLOQUE 2: DASHBOARD INSTITUCIONAL DE MÉTRICAS AVANZADAS ---
        st.markdown("---")
        st.subheader("📊 Análisis Avanzado de la Cartera vs Mercado (S&P 500)")
        
        col_riesgo, col_rendimiento, col_ajustado = st.columns(3)

        with col_riesgo:
            st.markdown("#### ⚠️ Métricas de Riesgo")
            st.metric(label="Value at Risk (VaR 95%)", value=f"{metricas['VaR (95%)'] * 100:.2f} %")
            st.metric(label="Maximum Drawdown (MDD)", value=f"{metricas['Max Drawdown'] * 100:.2f} %")
            
            dias_recuperacion = metricas['Días Recuperación']
            st.metric(label="Periodo de Recuperación", value=f"{dias_recuperacion} días" if isinstance(dias_recuperacion, (int, float)) else dias_recuperacion)

        with col_rendimiento:
            st.markdown("#### 📈 Rendimiento y Atribución")
            st.metric(label="Time-Weighted Return (TWR)", value=f"{metricas['TWR (Acumulado)'] * 100:.2f} %")
            st.metric(label="Active Return (vs SPY)", value=f"{metricas['Active Return'] * 100:.2f} %")
            st.metric(label="Tracking Error", value=f"{metricas['Tracking Error'] * 100:.2f} %")
            st.metric(label="Alpha de Jensen", value=f"{metricas['Alpha de Jensen'] * 100:.2f} %")

        with col_ajustado:
            st.markdown("#### ⚖️ Retorno Ajustado al Riesgo")
            st.metric(label="Ratio Sortino", value=f"{metricas['Ratio Sortino']:.2f}")
            st.metric(label="Ratio Calmar", value=f"{metricas['Ratio Calmar']:.2f}")
            st.metric(label="Ratio de Información", value=f"{metricas['Ratio de Información']:.2f}")

        # --- BLOQUE 3: MÓDULO DE EXPORTACIÓN ---
        st.markdown("---")
        st.subheader("📥 Exportar Propuesta y Reporte")
        st.info("Descarga la composición de tu cartera para ejecutar las órdenes o el informe completo de riesgo.")
        
        col_down1, col_down2 = st.columns(2)
        
        with col_down1:
            # 1. Descarga de los pesos (para el bróker)
            df_pesos = pesos_limpios.copy()
            df_pesos.columns = ['Peso_Porcentual']
            csv_pesos = df_pesos.to_csv().encode('utf-8')
            
            st.download_button(
                label="📊 Descargar Pesos de la Cartera (CSV)",
                data=csv_pesos,
                file_name=f"cartera_pesos_{perfil.lower()}_2026.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        with col_down2:
            # 2. Descarga del reporte de métricas (para auditoría)
            # Transformamos el diccionario de métricas avanzadas en un DataFrame estructurado
            df_metricas = pd.DataFrame(list(metricas.items()), columns=['Métrica Avanzada', 'Valor Calculado'])
            
            # Añadimos también las métricas básicas al reporte para que sea un informe completo
            df_metricas.loc[len(df_metricas)] = ['Rentabilidad Esperada (Base)', retorno]
            df_metricas.loc[len(df_metricas)] = ['Volatilidad Estándar (Base)', riesgo]
            df_metricas.loc[len(df_metricas)] = ['Ratio de Sharpe (Base)', sharpe]
            
            csv_metricas = df_metricas.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📈 Descargar Informe de Riesgo (CSV)",
                data=csv_metricas,
                file_name=f"auditoria_riesgo_{perfil.lower()}_2026.csv",
                mime="text/csv",
                use_container_width=True
            )