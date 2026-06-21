import streamlit as st

# 1. Configuración de la interfaz
st.set_page_config(
    page_title="Robo-Advisor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inicialización de la memoria global (Session State)
if 'survey_completed' not in st.session_state:
    st.session_state.survey_completed = False
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
if 'total_score' not in st.session_state:
    st.session_state.total_score = 0

# 3. Contenido de la Pantalla de Inicio
st.title("🤖 Sistema Automatizado de Gestión de Inversiones")
st.subheader("Prototipo de Robo-Advisor para la Asignación Óptima de Activos")

st.markdown("""
---
### Bienvenido al Sistema
Este entorno interactivo representa el componente práctico del Trabajo de Fin de Máster, enfocado en el desarrollo de un algoritmo de asignación automatizada de activos. 

#### Arquitectura del Prototipo:
* **Fase 1: Entrada de Datos (Perfilado):** Evaluación cuantitativa del perfil demográfico, financiero y de tolerancia al riesgo del inversor.
* **Fase 2: Procesamiento (Motor Financiero):** Descarga de datos de mercado en tiempo real y optimización matemática mediante enfoques clásicos y avanzados (Media-Varianza, Mean-CVaR y Paridad de Riesgo Jerárquica).
* **Fase 3: Salida (Visualización y Alertas):** Composición interactiva de la cartera sugerida y simulaciones predictivas.

👈 **Para comenzar, despliega el menú lateral izquierdo y selecciona `Profile Survey`.**
""")