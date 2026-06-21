# 🤖 Robo-Advisor

Prototipo de Sistema Automatizado de Gestión de Inversiones. Este sistema automatiza el perfilado de riesgo del usuario, la descarga de datos de mercado en tiempo real y la optimización estocástica de carteras.

## 🏗 Arquitectura del Sistema

El proyecto se divide en tres módulos principales integrados mediante **Streamlit**:
1. **Perfilado de Riesgo (`1_profile_survey.py`):** Evaluación cuantitativa del perfil demográfico y tolerancia al riesgo (Conservador, Moderado, Agresivo).
2. **Motor de Optimización (`2_portfolio.py`):** 
    - Descarga automatizada vía `yfinance`.
   - Asignación basada en la **Teoría Moderna de Carteras de Markowitz** (minimización de CVaR o maximización de Ratio de Sharpe).
    - Implementación de algoritmos avanzados de Machine Learning: **Paridad de Riesgo Jerárquica (HRP)**.
3. **Simulador de Escenarios (`3_monte_carlo.py`):** Proyecciones a un año mediante simulación estocástica (Movimiento Browniano Geométrico) para definir casos base, optimistas y pesimistas.

## 🛠️ Tecnologías Utilizadas

Librerias principales que potencian este sistema:

- **Python 3.9+**: Lenguaje base.
- **Streamlit**: Interfaz de usuario interactiva.
- **Riskfolio-Lib**: Motor de optimización de carteras.
- **yfinance**: Obtención de datos históricos.
- **Plotly**: Visualización de datos interactiva.

## 📱 Streamlit App

Prueba aquí el Robo-Advisor: https://the-robo-advisor.streamlit.app

## ⚙️ Instalación y Ejecución Local

Para ejecutar este entorno en tu máquina local, sigue estos pasos en tu terminal:

1. **Clonar el repositorio:**
```bash
git clone https://github.com/llynevalencia/robo_advisor.git
cd robo_advisor
```

2. **Crear y activar un entorno virtual (Recomendado):**
```bash
python3 -m venv .venv
source .venv/bin/activate  # En macOS/Linux
.venv\Scripts\activate   # En Windows
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Lanzar app:**
```bash
streamlit run app.py
```