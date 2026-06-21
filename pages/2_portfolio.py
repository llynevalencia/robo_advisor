import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Importamos todas las funciones del motor
from utils.engine import (
    get_all_tickers, download_market_data, calculate_daily_returns, 
    optimize_portfolio, calculate_portfolio_metrics, calculate_historical_performance,
    calculate_efficient_frontier_points
)

st.set_page_config(page_title="Mi Cartera Óptima", page_icon="pie_chart", layout="wide")
st.title("📊 Análisis y Optimización de Cartera")

if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
    st.warning("⚠️ Aún no has definido tu perfil de riesgo. Por favor, ve a la página '1 Profile Survey'.")
    st.stop()

perfil = st.session_state.user_profile
puntuacion = st.session_state.total_score

def perfil_color(p):
    if p == "Conservador": return "blue"
    if p == "Moderado": return "orange"
    return "red"

st.markdown(f"### Tu Perfil Asignado: :{perfil_color(perfil)}[**{perfil}**] *(Puntuación: {puntuacion} pts)*")
st.markdown("---")

with st.spinner('📡 Descargando datos de mercado y construyendo modelos cuantitativos...'):
    try:
        tickers = get_all_tickers()
        precios = download_market_data(tickers, start_date="2019-01-01")
        retornos = calculate_daily_returns(precios)
        
        # 1. Optimizar pesos de la cartera actual
        pesos = optimize_portfolio(retornos, perfil)
        pesos_limpios = pesos[pesos['weights'] >= 0.01].copy()
        pesos_limpios['weights'] = pesos_limpios['weights'] * 100 
        
        # 2. Calcular indicadores del perfil y simulación histórica
        retorno, riesgo, sharpe = calculate_portfolio_metrics(pesos, retornos)
        backtest = calculate_historical_performance(pesos, retornos)
        
        # 3. Calcular los puntos de la Frontera Eficiente académica
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
        # Etiquetamos el riesgo dinámicamente según la metodología usada
        label_riesgo = "Riesgo Anualizado (Volatilidad)" if medida_riesgo == 'MV' else "Riesgo Anualizado (CVaR 95%)"
        st.metric(label=label_riesgo, value=f"{riesgo * 100:.2f} %")
        st.metric(label="Ratio de Sharpe", value=f"{sharpe:.2f}")

    with col2:
        st.subheader("Frontera Eficiente de Markowitz")
        # Creamos la línea de la curva de la frontera eficiente
        etiqueta_eje_x = "Volatilidad (%)" if medida_riesgo == 'MV' else "CVaR (%)"
        
        fig_frontier = px.line(
            df_frontera, x='Riesgo', y='Retorno',
            labels={'Riesgo': etiqueta_eje_x, 'Retorno': 'Rentabilidad Esperada (%)'},
            title=f"Frontera Eficiente en Espacio Media-{medida_riesgo}"
        )
        fig_frontier.update_traces(line=dict(color='grey', width=2, dash='dash'))
        
        # Superponemos la cartera óptima elegida como una gran estrella dorada
        fig_frontier.add_scatter(
            x=[riesgo * 100], 
            y=[retorno * 100], 
            mode='markers',
            marker=dict(color='gold', size=16, symbol='star', line=dict(color='black', width=1.5)),
            name=f"Tu Cartera ({perfil})"
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