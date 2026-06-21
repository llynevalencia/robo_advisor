import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Importamos las dependencias de nuestro motor
from utils.engine import (
    get_all_tickers, download_market_data, calculate_daily_returns, 
    optimize_portfolio, run_monte_carlo_simulation
)

st.set_page_config(page_title="Simulación 2027", page_icon="🔮", layout="wide")
st.title("🔮 Simulación de Monte Carlo (Proyección a 1 Año)")

if 'survey_completed' not in st.session_state or not st.session_state.survey_completed:
    st.warning("⚠️ Aún no has definido tu perfil de riesgo. Por favor, ve a la página '1 Profile Survey'.")
    st.stop()

perfil = st.session_state.user_profile

st.markdown(f"Generando miles de escenarios de mercado futuros para una **Cartera {perfil}**.")
st.markdown("---")

with st.spinner('🎲 Lanzando los dados... Ejecutando simulaciones estocásticas...'):
    try:
        # 1. Recuperar datos y optimizar la cartera (reutilizamos la lógica)
        tickers = get_all_tickers()
        precios = download_market_data(tickers, start_date="2019-01-01")
        retornos = calculate_daily_returns(precios)
        pesos = optimize_portfolio(retornos, perfil)
        
        # 2. Ejecutar Monte Carlo
        df_simulacion = run_monte_carlo_simulation(pesos, retornos, num_simulations=100, time_horizon=252)
        
        # 3. Analizar los resultados finales (Día 252)
        resultados_finales = df_simulacion.iloc[-1, :]
        escenario_pesimista = np.percentile(resultados_finales, 5)   # Peor 5%
        escenario_mediano = np.percentile(resultados_finales, 50)  # Caso base
        escenario_optimista = np.percentile(resultados_finales, 95)  # Mejor 5%
        
        calculo_exitoso = True
    except Exception as e:
        st.error(f"Error en la simulación: {e}")
        calculo_exitoso = False

if calculo_exitoso:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Caminos Aleatorios del Precio")
        # Dibujamos las simulaciones usando Plotly Graph Objects para mayor control
        fig = go.Figure()
        
        # Añadimos cada simulación como una línea fina
        for col in df_simulacion.columns:
            fig.add_trace(go.Scatter(
                y=df_simulacion[col], 
                mode='lines', 
                line=dict(width=1, color='rgba(100, 150, 250, 0.1)'), # Azul casi transparente
                showlegend=False
            ))
            
        # Añadimos la línea de tendencia central (Mediana)
        mediana_serie = df_simulacion.median(axis=1)
        fig.add_trace(go.Scatter(
            y=mediana_serie, 
            mode='lines', 
            line=dict(width=3, color='navy'),
            name='Mediana Esperada'
        ))
        
        fig.update_layout(
            xaxis_title='Días de Trading (1 Año)',
            yaxis_title='Capitalización Acumulada (Base 1)',
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Análisis de Escenarios")
        st.info("Asumiendo una inversión inicial de **10.000 €** hoy, este sería el valor esperado dentro de un año:")
        
        st.metric(
            label="🌟 Escenario Optimista (Top 5%)", 
            value=f"{10000 * escenario_optimista:,.2f} €",
            delta="Excelente"
        )
        
        st.metric(
            label="📊 Escenario Base (Mediana)", 
            value=f"{10000 * escenario_mediano:,.2f} €",
            delta=f"{((escenario_mediano - 1) * 100):.2f} % rentabilidad",
            delta_color="normal"
        )
        
        st.metric(
            label="⚠️ Escenario Pesimista (Bottom 5%)", 
            value=f"{10000 * escenario_pesimista:,.2f} €",
            delta=f"Pérdida de {10000 * (1 - escenario_pesimista):,.2f} €",
            delta_color="inverse"
        )