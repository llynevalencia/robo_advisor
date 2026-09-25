import streamlit as st


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

**Para comenzar, clica en el menú superior `Perfilado de Riesgo`.**
""")