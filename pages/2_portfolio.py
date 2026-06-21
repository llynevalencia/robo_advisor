import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Importamos las funciones del motor financiero (añadiendo optimize_hrp)
from utils.engine import (
    get_all_tickers, download_market_data, calculate_daily_returns, 
    optimize_portfolio, optimize_hrp, calculate_portfolio_metrics, 
    calculate_historical_performance, calculate_efficient_frontier_points
)

st.set_page_config(page_title="Mi Cartera Óptima", page_icon="pie_chart", layout="wide")
st.title("📊 Análisis y Optimización de Cartera")

if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
    st.warning("⚠️ Aún no has definido tu perfil de riesgo. Por favor, ve a la página '1 Profile Survey'.")
    st.stop()

perfil = st.session_state.user_profile
puntuacion = st.session_state.total_score

# --- CONTROLES EN LA BARRA LATERAL ---
st.sidebar.header("Configuración del Modelo")

# El usuario puede elegir el cerebro matemático de la cartera
metodo_opt = st.sidebar.selectbox(
    "Algoritmo de Optimización",
    options=["Teoría Moderna (Markowitz / CVaR)", "Enfoque Avanzado (HRP / Machine Learning)"],
    help="Markowitz optimiza según tu perfil de riesgo. HRP distribuye el riesgo basándose en clustering jerárquico sin depender del perfil."
)

def perfil_color(p):
    if p == "Conservador": return "blue"
    if p == "Moderado": return "orange"
    return "red"

st.markdown(f"### Tu Perfil Asignado: :{perfil_color(perfil)}[**{perfil}**] *(Puntuación: {puntuacion} pts)*")
st.markdown(f"**Algoritmo activo:** {metodo_opt}")
st.markdown("---")

with st.spinner('📡 Ejecutando modelos cuantitativos de asignación de activos...'):
    try:
        tickers = get_all_tickers()
        precios = download_market_data(tickers, start_date="2019-01-01")
        retornos = calculate_daily_returns(precios)
        
        # LÓGICA CONDICIONAL: Seleccionar el optimizador según el control lateral
        if metodo_opt == "Teoría Moderna (Markowitz / CVaR)":
            pesos = optimize_portfolio(retornos, perfil)
        else:
            pesos = optimize_hrp(retornos)
        
        # Procesar pesos para el gráfico
        pesos_limpios = pesos[pesos['weights'] >= 0.01].copy()
        pesos_limpios['weights'] = pesos_limpios['weights'] * 100 
        
        # Calcular métricas y backtest para la cartera elegida
        retorno, riesgo, sharpe = calculate_portfolio_metrics(pesos, retornos)
        backtest = calculate_historical_performance(pesos, retornos)
        
        # La frontera eficiente tiene sentido académico principalmente para el espacio Media-Varianza/CVaR
        df_frontera, medida_riesgo = calculate_efficient_frontier_points(retornos, perfil)
        
        calculo_exitoso = True
    except Exception as e:
        st.error(f"Error al calcular la cartera: {e}")
        calculo_exitoso = False

if calculo_exitoso:
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
        
        # Ajuste de etiquetas dinámicas para el riesgo
        if metodo_opt == "Teoría Moderna (Markowitz / CVaR)" and perfil == "Conservador":
            label_riesgo = "Riesgo Anualizado (CVaR 95%)"
        else:
            label_riesgo = "Riesgo Anualizado (Volatilidad)"
            
        st.metric(label=label_riesgo, value=f"{riesgo * 100:.2f} %")
        st.metric(label="Ratio de Sharpe", value=f"{sharpe:.2f}")

    with col2:
        st.subheader("Ubicación en la Frontera Eficiente")
        # Graficamos la curva de referencia
        fig_frontier = px.line(
            df_frontera, x='Riesgo', y='Retorno',
            labels={'Riesgo': 'Volatilidad (%)', 'Retorno': 'Rentabilidad Esperada (%)'},
            title="Comparativa de la Cartera Frente a la Frontera de Markowitz"
        )
        fig_frontier.update_traces(line=dict(color='grey', width=2, dash='dash'))
        
        # Colocamos la estrella de la cartera actual (sea Markowitz o HRP)
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

        # --- MÓDULO DE EXPORTACIÓN ---
        st.markdown("---")
        st.subheader("📥 Exportar Propuesta de Inversión")
        st.info("Descarga la composición detallada de tu cartera para ejecutar las órdenes en tu bróker.")
        
        # Preparamos el DataFrame para la descarga (añadimos nombre de columna para claridad)
        df_descarga = pesos_limpios.copy()
        df_descarga.columns = ['Peso_Porcentual']
        csv_data = df_descarga.to_csv().encode('utf-8')
        
        st.download_button(
            label="Descargar Cartera en CSV",
            data=csv_data,
            file_name=f"cartera_optima_{perfil.lower()}_2026.csv",
            mime="text/csv"
        )