import streamlit as st

st.set_page_config(page_title="Perfil de Inversor", page_icon="👤", layout="wide")

# Asegurar que las variables globales existan si el usuario entra directamente a esta página
if 'survey_completed' not in st.session_state:
    st.session_state.survey_completed = False
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
if 'total_score' not in st.session_state:
    st.session_state.total_score = 0

st.title("👤 Cuestionario de Perfilado del Inversor")
st.markdown("Por favor, responde a las siguientes 10 preguntas para evaluar tu perfil de riesgo y horizonte temporal.")

# Creamos el formulario de captura de datos
with st.form("survey_form"):
    
    st.subheader("Dimensiones Demográficas y de Horizonte Temporal")
    
    q1 = st.selectbox(
        "1. ¿En qué rango de edad se encuentra?",
        options=["Más de 60 años", "Entre 45 y 60 años", "Entre 30 y 45 años", "Menos de 30 años"]
    )
    
    q2 = st.selectbox(
        "2. ¿Cuánto tiempo planea mantener la inversión?",
        options=["Menos de 1 año", "Entre 1 y 3 años", "Entre 3 y 7 años", "Más de 7 años"]
    )
    
    st.subheader("Objetivos Financieros y Tolerancia Psicológica al Riesgo")
    
    q3 = st.selectbox(
        "3. ¿Cuál es su principal objetivo al invertir?",
        options=["Preservar capital", "Obtener ingresos estables", "Crecimiento moderado", "Maximizar rentabilidad"]
    )
    
    q4 = st.selectbox(
        "4. Si su cartera pierde un 15% en un mes, ¿qué haría?",
        options=["Vendería toda la inversión", "Vendería una parte", "Mantendría la inversión", "Invertiría más aprovechando la caída"]
    )
    
    q5 = st.selectbox(
        "5. ¿Cuál es su experiencia invirtiendo?",
        options=["Ninguna", "Básica", "Intermedia", "Avanzada"]
    )
    
    st.subheader("Capacidad Financiera y Estabilidad Económica")
    
    q6 = st.selectbox(
        "6. ¿Qué porcentaje de sus ingresos mensuales puede ahorrar?",
        options=["Menos del 5%", "Entre 5% y 15%", "Entre 15% y 30%", "Más del 30%"]
    )
    
    q7 = st.selectbox(
        "7. ¿Qué prefiere?",
        options=[
            "Baja rentabilidad con mínimo riesgo",
            "Rentabilidad moderada con algo de riesgo",
            "Buena rentabilidad aceptando volatilidad",
            "Máxima rentabilidad aunque haya grandes pérdidas"
        ]
    )
    
    q8 = st.selectbox(
        "8. ¿Cómo describiría la estabilidad de sus ingresos?",
        options=["Muy inestables", "Algo inestables", "Bastante estables", "Totalmente estables"]
    )
    
    q9 = st.selectbox(
        "9. ¿Qué importancia tiene este dinero para sus necesidades actuales?",
        options=[
            "Es fundamental para mis gastos diarios",
            "Es importante, pero no imprescindible",
            "Apenas afecta a mi situación financiera",
            "No necesito este dinero a corto plazo"
        ]
    )
    
    q10 = st.selectbox(
        "10. ¿Cómo valoraría sus conocimientos financieros?",
        options=["Muy bajos", "Básicos", "Intermedios", "Avanzados"]
    )
    
    # Botón para procesar el formulario
    submit_button = st.form_submit_button("Analizar mi Perfil de Riesgo")

# Lógica de cálculo tras pulsar el botón
if submit_button:
    # Diccionario de asignación de puntos estandarizado según la metodología del TFM
    points_map = {
        # Opciones de posición 0 -> 5 pts, posición 1 -> 10 pts, posición 2 -> 15 pts, posición 3 -> 20 pts
        "q1": {"Más de 60 años": 5, "Entre 45 y 60 años": 10, "Entre 30 y 45 años": 15, "Menos de 30 años": 20},
        "q2": {"Menos de 1 año": 5, "Entre 1 y 3 años": 10, "Entre 3 y 7 años": 15, "Más de 7 años": 20},
        "q3": {"Preservar capital": 5, "Obtener ingresos estables": 10, "Crecimiento moderado": 15, "Maximizar rentabilidad": 20},
        "q4": {"Vendería toda la inversión": 5, "Vendería una parte": 10, "Mantendría la inversión": 15, "Invertiría más aprovechando la caída": 20},
        "q5": {"Ninguna": 5, "Básica": 10, "Intermedia": 15, "Avanzada": 20},
        "q6": {"Menos del 5%": 5, "Entre 5% y 15%": 10, "Entre 15% y 30%": 15, "Más del 30%": 20},
        "q7": {"Baja rentabilidad con mínimo riesgo": 5, "Rentabilidad moderada con algo de riesgo": 10, "Buena rentabilidad aceptando volatilidad": 15, "Máxima rentabilidad aunque haya grandes pérdidas": 20},
        "q8": {"Muy inestables": 5, "Algo inestables": 10, "Bastante estables": 15, "Totalmente estables": 20},
        "q9": {"Es fundamental para mis gastos diarios": 5, "Es importante, pero no imprescindible": 10, "Apenas afecta a mi situación financiera": 15, "No necesito este dinero a corto plazo": 20},
        "q10": {"Muy bajos": 5, "Básicos": 10, "Intermedios": 15, "Avanzados": 20}
    }
    
    # Sumar puntuación total
    total_score = (
        points_map["q1"][q1] + points_map["q2"][q2] + points_map["q3"][q3] +
        points_map["q4"][q4] + points_map["q5"][q5] + points_map["q6"][q6] +
        points_map["q7"][q7] + points_map["q8"][q8] + points_map["q9"][q9] +
        points_map["q10"][q10]
    )
    
    # Clasificación por rangos metodológicos
    if 50 <= total_score <= 95:
        profile = "Conservador"
        color = "blue"
    elif 96 <= total_score <= 145:
        profile = "Moderado"
        color = "orange"
    else:
        profile = "Agresivo"
        color = "red"
    
    # Guardar resultados en la memoria de sesión
    st.session_state.total_score = total_score
    st.session_state.user_profile = profile
    st.session_state.survey_completed = True
    
    # Mostrar resultados en pantalla
    st.success("¡Cuestionario procesado con éxito!")
    st.markdown(f"### Puntuación Total: **{total_score} / 200**")
    st.markdown(f"### Perfil Asignado: :{color}[**{profile}**]")

# Mostrar estado actual si ya se había completado antes
elif st.session_state.survey_completed:
    st.info(f"Perfil guardado previamente: {st.session_state.user_profile} ({st.session_state.total_score} puntos).")