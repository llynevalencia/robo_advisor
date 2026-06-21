import yfinance as yf
import pandas as pd
import numpy as np
import riskfolio as rp

# 1. Definición del Universo de Activos
# Seleccionamos ETFs representativos y criptos para tener liquidez y datos fiables
ASSET_UNIVERSE = {
    "Renta Variable": ["SPY", "URTH"],  # S&P 500 y MSCI World
    "Renta Fija": ["AGG", "TLT"],       # Bonos Globales y Bonos del Tesoro EE.UU. a +20 años
    "Materias Primas": ["GLD", "SLV"],  # Oro y Plata
    "Criptomonedas": ["BTC-USD", "ETH-USD"] # Bitcoin y Ethereum
}

def get_all_tickers():
    """Extrae una lista plana de todos los tickers del diccionario."""
    tickers = []
    for category_tickers in ASSET_UNIVERSE.values():
        tickers.extend(category_tickers)
    return tickers

def download_market_data(tickers, start_date="2018-01-01", end_date=None):
    """
    Descarga los precios de cierre ajustados de Yahoo Finance.
    En las versiones recientes de yfinance, 'Close' ya viene auto-ajustado por defecto.
    """
    data = yf.download(tickers, start=start_date, end=end_date)
    
    # Usamos 'Close' en lugar de 'Adj Close' por la nueva API de yfinance
    adj_close = data['Close']
    
    # Limpiamos los datos: eliminamos filas con valores nulos (días festivos, etc.)
    adj_close = adj_close.dropna()
    
    return adj_close

def calculate_daily_returns(prices_df):
    """
    Calcula los retornos diarios logarítmicos o porcentuales.
    Para la optimización clásica, usamos la variación porcentual simple.
    """
    # pct_change() calcula (Precio_hoy - Precio_ayer) / Precio_ayer
    returns = prices_df.pct_change().dropna()
    return returns


def optimize_portfolio(returns, user_profile):
    """
    Riskfolio-Lib para calcular los pesos óptimos de la cartera 
    basándose en el perfil de riesgo del usuario.
    """
    # 1. Crear el objeto Portafolio de Riskfolio
    port = rp.Portfolio(returns=returns)

    # 2. Estimar retornos esperados (mu) y matriz de covarianza (cov) usando datos históricos
    port.assets_stats(method_mu='hist', method_cov='hist')

    # 3. Traducir el Perfil del Inversor a Matemáticas Cuantitativas
    # rm = Risk Measure (Medida de riesgo)
    # obj = Objective function (Función objetivo)
    
    if user_profile == "Conservador":
        # Según tu TFM: Enfoque en pérdidas extremas.
        # Minimizamos el Conditional Value at Risk (CVaR).
        rm = 'CVaR' 
        obj = 'MinRisk'
        
    elif user_profile == "Moderado":
        # Según tu TFM: Teoría Clásica de Markowitz.
        # Maximizar el Ratio de Sharpe (Equilibrio Retorno / Varianza Clásica 'MV').
        rm = 'MV' 
        obj = 'Sharpe'
        
    elif user_profile == "Agresivo":
        # Perfil de alto riesgo: Maximizar rentabilidad asumiendo la volatilidad.
        rm = 'MV'
        obj = 'MaxRet'
        
    else:
        # Fallback de seguridad
        rm = 'MV'
        obj = 'Sharpe'

    # 4. Ejecutar el Optimizador Matemático
    # model='Classic' -> Modelo histórico clásico
    # rf=0 -> Tasa libre de riesgo (Risk Free rate). Para la demo asumimos 0.
    # hist=True -> Usar los datos históricos reales
    weights = port.optimization(model='Classic', rm=rm, obj=obj, rf=0, l=0, hist=True)
    
    return weights


def calculate_portfolio_metrics(weights, returns):
    """
    Calcula el retorno anualizado, la volatilidad y el Ratio de Sharpe de la cartera óptima.
    Asume 252 días hábiles de trading al año.
    """
    # 1. Anualizamos los datos históricos
    mu_anual = returns.mean() * 252
    cov_anual = returns.cov() * 252
    
    # 2. Extraemos los pesos (w) como un array matemático de numpy
    w = weights['weights'].values
    
    # 3. Aplicamos las fórmulas de la Teoría Moderna de Carteras
    retorno_esperado = np.sum(mu_anual * w)
    volatilidad = np.sqrt(np.dot(w.T, np.dot(cov_anual, w)))
    
    # 4. Calculamos el Ratio de Sharpe (Asumimos Tasa Libre de Riesgo = 0% para la demo)
    sharpe = retorno_esperado / volatilidad if volatilidad > 0 else 0
    
    return retorno_esperado, volatilidad, sharpe

def calculate_historical_performance(weights, returns):
    """
    Simula el comportamiento histórico de la cartera (Backtesting).
    Muestra el crecimiento de la inversión a partir de una base de 1.
    """
    # Multiplicamos el retorno diario de cada activo por el peso que le hemos asignado
    retorno_diario_cartera = (returns * weights['weights'].values).sum(axis=1)
    
    # Calculamos el interés compuesto acumulado: (1 + r).cumprod()
    retorno_acumulado = (1 + retorno_diario_cartera).cumprod()
    
    return retorno_acumulado

def calculate_efficient_frontier_points(returns, user_profile):
    """
    Calcula los puntos de riesgo y retorno que componen la Frontera Eficiente
    adaptando la medida de riesgo al perfil del usuario (MV o CVaR).
    """
    port = rp.Portfolio(returns=returns)
    port.assets_stats(method_mu='hist', method_cov='hist')
    
    # Mantenemos la consistencia académica: la frontera se mide en la misma métrica de riesgo que optimizamos
    if user_profile == "Conservador":
        rm = 'CVaR'
    else:
        rm = 'MV'
        
    # Riskfolio calcula una matriz de pesos para N carteras óptimas a lo largo de la curva
    frontier_weights = port.efficient_frontier(model='Classic', rm=rm, points=40, rf=0)
    
    mu_anual = returns.mean() * 252
    cov_anual = returns.cov() * 252
    
    frontier_data = []
    
    # Calculamos el riesgo y retorno exacto de cada uno de los 40 puntos
    for col in frontier_weights.columns:
        w = frontier_weights[col].values
        ret_esperado = np.sum(mu_anual * w)
        
        if rm == 'MV':
            # Riesgo = Volatilidad Estándar
            riesgo_calculado = np.sqrt(np.dot(w.T, np.dot(cov_anual, w)))
        elif rm == 'CVaR':
            # Riesgo = Pérdida media del peor 5% de los escenarios (Anualizado)
            retornos_historicos_cartera = (returns * w).sum(axis=1)
            var_95 = np.percentile(retornos_historicos_cartera, 5)
            cvar = retornos_historicos_cartera[retornos_historicos_cartera <= var_95].mean()
            riesgo_calculado = -cvar * np.sqrt(252)
            
        frontier_data.append({
            'Riesgo': riesgo_calculado * 100,
            'Retorno': ret_esperado * 100
        })
        
    return pd.DataFrame(frontier_data), rm

def run_monte_carlo_simulation(weights, returns, num_simulations=100, time_horizon=252):
    """
    Ejecuta una simulación de Monte Carlo para proyectar el valor de la cartera.
    time_horizon = 252 (días hábiles en un año financiero).
    Calculará la media y la desviación estándar diarias de la cartera óptima elegida, y generará 100 caminos aleatorios asumiendo una distribución normal de los retornos.
    """
    # 1. Obtener la serie de retornos históricos de la cartera exacta
    w = weights['weights'].values
    retorno_diario_cartera = (returns * w).sum(axis=1)
    
    # 2. Extraer los parámetros estadísticos básicos
    mu = retorno_diario_cartera.mean()
    sigma = retorno_diario_cartera.std()
    
    # 3. Construir la matriz de simulaciones
    # Empezamos asumiendo una inversión base de 1 unidad (100%)
    simulation_df = pd.DataFrame()
    
    for x in range(num_simulations):
        # Generamos 252 retornos diarios aleatorios basados en la campana de Gauss de la cartera
        shocks_diarios = np.random.normal(loc=mu, scale=sigma, size=time_horizon)
        
        # Calculamos el efecto compuesto día a día
        camino_precios = [1.0] # Día 0
        for shock in shocks_diarios:
            nuevo_precio = camino_precios[-1] * (1 + shock)
            camino_precios.append(nuevo_precio)
            
        simulation_df[f'Sim_{x}'] = camino_precios
        
    return simulation_df

def optimize_hrp(returns):
    """
    Utiliza Riskfolio-Lib para calcular los pesos óptimos usando
    el algoritmo avanzado de Paridad de Riesgo Jerárquica (HRP).
    HRP utiliza clustering jerárquico para distribuir el riesgo de forma óptima.
    """
    # 1. Instanciar el objeto de Cartera de Clustering Jerárquico
    port = rp.HCPortfolio(returns=returns)
    
    # 2. Ejecutar la optimización avanzada
    # model='HRP' -> Hierarchical Risk Parity
    # rm='MV' -> Usamos la varianza estándar para medir el riesgo de los clusters
    # linkage='ward' -> Método de enlace robusto para el clustering jerárquico
    weights = port.optimization(model='HRP', rm='MV', rf=0, linkage='ward', max_k=10, leaf_order=True)
    
    return weights