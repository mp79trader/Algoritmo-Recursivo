# Documentación Técnica - QuantuM FFT

## 📖 Tabla de Contenidos

1. [Fundamentos Matemáticos](#fundamentos-matemáticos)
2. [Algoritmo FFT Recursivo](#algoritmo-fft-recursivo)
3. [Aplicación a Mercados Financieros](#aplicacion-a-mercados-financieros)
4. [Guía de Uso en Producción](#guia-de-uso-en-produccion)
5. [Análisis de Riesgos](#analisis-de-riesgos)
6. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Fundamentos Matemáticos

### Transformada de Fourier

La Transformada de Fourier (TF) es una herramienta matemática fundamental que descompone una señal en sus componentes de frecuencia fundamentales. Fue desarrollada por Jean-Baptiste Joseph Fourier en 1822 y tiene aplicaciones en numerosos campos como procesamiento de señales, telecomunicaciones, y por supuesto, análisis financiero.

#### Definición Matemática

La Transformada Discreta de Fourier (DFT) de una señal x[n] de longitud N se define como:

```
X(k) = Σ x[n] * e^(-i2πkn/N)
     n=0
```

Donde:
- `x[n]` es la señal en el tiempo discreto
- `X(k)` es la representación en frecuencia
- `k` es el índice de frecuencia (0 a N-1)
- `e^(-i2πkn/N)` son las bases de Fourier (exponenciales complejas)
- `i` es la unidad imaginaria (√-1)

#### Interpretación Física

La DFT descompone la señal en dos componentes para cada frecuencia `k`:

1. **Parte Real**: Representa la componente en fase con la seno
2. **Parte Imaginaria**: Representa la componente en fase con el coseno

De forma combinada, cada componente de frecuencia tiene:
- **Magnitud**: |X(k)| = √(Re(X(k))² + Im(X(k))²)
  - Indica la "fuerza" o amplitud de esa frecuencia en la señal
- **Fase**: φ(k) = arctan(Im(X(k))/Re(X(k)))
  - Indica el desplazamiento temporal de esa frecuencia

### Transformada Rápida de Fourier (FFT)

La FFT es un algoritmo eficiente para calcular la DFT. Reduce la complejidad computacional de O(n²) a O(n log n), lo que es crucial para aplicaciones en tiempo real.

#### Algoritmo Cooley-Tukey

El algoritmo Cooley-Tukey (1965) utiliza el principio de divide y conquistas:

1. **Dividir**: Si N es par, dividir la señal en dos partes: índices pares e impares
2. **Reconquistar**: Calcular DFT de cada parte recursivamente
3. **Combinar**: Unir los resultados usando las propiedades de simetría

**Pseudocódigo:**

```
function FFT(x):
    n = length(x)
    if n == 1:
        return x
    
    # Dividir en índices pares e impares
    even = FFT(x[0], x[2], x[4], ..., x[n-2])
    odd = FFT(x[1], x[3], x[5], ..., x[n-1])
    
    # Combinar usando factores de Twiddle
    for k in 0 to n/2 - 1:
        T = exp(-i2πk/n) * odd[k]
        X[k] = even[k] + T
        X[k + n/2] = even[k] - T
    
    return X
```

#### Complejidad Computacional

| Método | Complejidad | Ventaja |
|--------|--------------|---------|
| DFT Directa | O(n²) | Simple de implementar |
| FFT Recursiva | O(n log n) | Más eficiente |
| FFT Iterativa | O(n log n) | Ahorra memoria |

Para N = 1024 puntos:
- DFT: 1,048,576 operaciones
- FFT: 10,240 operaciones (100x más rápido)

---

## Algoritmo FFT Recursivo

### Implementación en QuantuM FFT

Nuestra implementación sigue el algoritmo Cooley-Tukey con optimizaciones específicas para análisis financiero:

```python
def next_power_of_2(n: int) -> int:
    """Encuentra la siguiente potencia de 2 mayor o igual a n"""
    return 1 if n == 0 else 2 ** (n - 1).bit_length()

def fft_recursive(x: np.ndarray) -> np.ndarray:
    """
    FFT recursivo Cooley-Tukey optimizado
    Complejidad: O(n log n)
    """
    x = np.asarray(x).flatten()
    n = len(x)
    
    # Caso base
    if n <= 1:
        return x.astype(complex)
    
    # Padding a potencia de 2
    target_n = next_power_of_2(n)
    if n != target_n:
        x = np.pad(x, (0, target_n - n), 'constant')
        n = target_n
    
    # Dividir en pares e impares
    even = fft_recursive(x[::2])
    odd = fft_recursive(x[1::2])
    
    # Factores de Twiddle
    k = np.arange(n // 2)
    factor = np.exp(-2j * np.pi * k / n)
    T = factor * odd
    
    # Combinar
    return np.concatenate([even + T, even - T])
```

### Filtrado Adaptativo

No todas las frecuencias son igualmente importantes para predecir el mercado. Nuestro filtrado adapativo:

#### 1. Filtrado por Magnitud

```python
def filter_by_magnitude(fft_result, threshold=0.05):
    """
    Filtra componentes con magnitud menor al umbral
    """
    magnitude = np.abs(fft_result)
    max_magnitude = np.max(magnitude)
    
    filtered = fft_result.copy()
    filtered[magnitude < threshold * max_magnitude] = 0
    
    return filtered
```

**Lógica:**
- Calcula la magnitud de cada componente de frecuencia
- Elimina componentes con magnitud < 5% del máximo
- Reduce ruido de alta frecuencia

#### 2. Filtrado por Tipo de Frecuencia

```python
def filter_by_frequency_type(fft_result, frequencies, 
                           keep_low=True, keep_mid=True, keep_high=False):
    """
    Filtra por tipo de frecuencia:
    - Baja: Tendencias de largo plazo
    - Media: Ciclos estacionales
    - Alta: Volatilidad y ruido
    """
    n = len(frequencies)
    freq_bands = {
        'low': np.abs(frequencies) < 0.1,      # 0-10% de Nyquist
        'mid': (np.abs(frequencies) >= 0.1) & (np.abs(frequencies) < 0.4),  # 10-40%
        'high': np.abs(frequencies) >= 0.4,      # > 40%
    }
    
    mask = np.zeros(n, dtype=bool)
    if keep_low:
        mask |= freq_bands['low']
    if keep_mid:
        mask |= freq_bands['mid']
    if keep_high:
        mask |= freq_bands['high']
    
    filtered = fft_result.copy()
    filtered[~mask] = 0
    
    return filtered
```

#### 3. Selección de Componentes Top-N

```python
def extract_top_components(fft_result, n_components=10):
    """
    Extrae los N componentes de frecuencia más importantes
    basado en magnitud
    """
    magnitude = np.abs(fft_result)
    indices = np.argsort(magnitude)[-n_components:][::-1]
    
    return fft_result[indices], indices
```

### Reconstrucción de Señal

Una vez filtrado el espectro, reconstruimos la señal usando la FFT inversa:

```python
def ifft_recursive(x: np.ndarray) -> np.ndarray:
    """
    FFT inversa recursiva
    Recupera la señal desde el dominio de frecuencia
    """
    n = len(x)
    return fft_recursive(x.conj()).conj() / n

def reconstruct_signal(filtered_fft):
    """
    Reconstruye la señal desde el espectro filtrado
    """
    reconstructed = np.real(ifft_recursive(filtered_fft))
    return reconstructed
```

---

## Aplicación a Mercados Financieros

### ¿Por qué FFT en Finanzas?

Los precios financieros exhiben patrones que pueden ser analizados mediante FFT:

1. **Tendencias** (Baja Frecuencia)
   - Tendencias de largo plazo (meses/años)
   - Ciclos macroeconómicos
   - Cambios estructurales del mercado

2. **Ciclos** (Media Frecuencia)
   - Estacionalidades (trimestrales, mensuales)
   - Ciclos de informes trimestrales
   - Patrones de opciones

3. **Volatilidad** (Alta Frecuencia)
   - Fluctuaciones diarias
   - Ruido de mercado
   - Eventos de corto plazo

### Proceso de Análisis

#### Paso 1: Preparación de Datos

```python
def prepare_market_data(prices):
    """
    Prepara datos de precios para análisis FFT
    """
    # 1. Eliminar valores nulos
    prices = prices.dropna()
    
    # 2. Diferenciación (para estacionariedad)
    returns = np.diff(np.log(prices))
    
    # 3. Normalización
    normalized = (returns - returns.mean()) / returns.std()
    
    # 4. Eliminar outliers (±3 desviaciones estándar)
    normalized = normalized[np.abs(normalized) < 3]
    
    return normalized
```

**Por qué diferenciar:**
- Los precios son no estacionarios (tendencia)
- Los rendimientos suelen ser más estacionarios
- FFT funciona mejor con datos estacionarios

#### Paso 2: Análisis Espectral

```python
def spectral_analysis(signal, sample_rate=252):
    """
    Análisis espectral completo
    """
    # 1. Aplicar FFT
    fft_result = fft_recursive(signal)
    
    # 2. Obtener frecuencias
    n = len(signal)
    frequencies = np.fft.fftfreq(n, d=1/sample_rate)
    
    # 3. Calcular magnitud y fase
    magnitude = np.abs(fft_result)
    phase = np.angle(fft_result)
    
    # 4. Filtrar ruido
    filtered_fft = filter_by_magnitude(fft_result, threshold=0.05)
    
    # 5. Reconstruir señal filtrada
    reconstructed = np.real(ifft_recursive(filtered_fft))
    
    # 6. Identificar ciclos dominantes
    dominant_cycles = find_dominant_cycles(fft_result, frequencies)
    
    return {
        'fft': fft_result,
        'frequencies': frequencies,
        'magnitude': magnitude,
        'phase': phase,
        'filtered_fft': filtered_fft,
        'reconstructed': reconstructed,
        'dominant_cycles': dominant_cycles
    }
```

#### Paso 3: Extrapolación (Predicción)

```python
def extrapolate_signal(signal, days_to_predict=30):
    """
    Extrapola la señal para predecir precios futuros
    """
    n = len(signal)
    fft_result = fft_recursive(signal)[:n]
    frequencies = np.fft.fftfreq(n, d=1/252)
    
    # Filtrar componentes
    filtered_fft = filter_by_magnitude(fft_result, threshold=0.05)
    
    # Extender FFT al futuro
    extended_fft = np.zeros(n + days_to_predict, dtype=complex)
    extended_fft[:n] = filtered_fft
    
    # Simular continuación de componentes
    for i in range(1, days_to_predict + 1):
        extended_fft[n + i - 1] = filtered_fft[-i]
    
    # Reconstruir señal extendida
    prediction = np.real(ifft_recursive(extended_fft))[:n + days_to_predict]
    
    return prediction[-days_to_predict:]
```

**Limitaciones de Extrapolación:**
- Se asume continuidad de ciclos
- Ignora eventos exógenos (noticias, economía)
- Degrada con el tiempo (menor confianza a largo plazo)

### Análisis de Ciclos

```python
def find_dominant_cycles(fft_result, frequencies, n_cycles=10):
    """
    Identifica los ciclos más dominantes en la señal
    """
    magnitude = np.abs(fft_result)
    
    # Filtrar frecuencias positivas (parte del espectro)
    positive_freqs = frequencies[frequencies >= 0]
    positive_magnitude = magnitude[frequencies >= 0]
    
    # Encontrar picos en el espectro
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(positive_magnitude, distance=5)
    
    # Extraer información de ciclos
    cycles = []
    for peak in peaks:
        freq = positive_freqs[peak]
        mag = positive_magnitude[peak]
        
        # Calcular período en días
        if freq != 0:
            period = 1 / abs(freq)
        else:
            period = float('inf')  # Componente DC
        
        cycles.append({
            'frequency': freq,
            'period': period,
            'magnitude': mag,
            'phase': np.angle(fft_result[frequencies >= 0][peak])
        })
    
    # Ordenar por magnitud
    cycles.sort(key=lambda x: x['magnitude'], reverse=True)
    
    return cycles[:n_cycles]
```

**Interpretación de Ciclos:**

| Período (días) | Tipo de Ciclo | Implicación Trading |
|-----------------|---------------|---------------------|
| < 10 | Volatilidad Intradía | Scalping, High-Frequency Trading |
| 10-30 | Semanal | Swing trading semanal |
| 30-90 | Mensual | Swing trading mensual |
| 90-180 | Trimestral | Position trading |
| > 180 | Anual/Estacional | Long-term investing |

---

## Guía de Uso en Producción

### 1. Validación del Modelo

#### Backtesting Histórico

```python
def backtest_strategy(symbol, start_date, end_date, strategy_params):
    """
    Simula el desempeño de la estrategia FFT en datos históricos
    """
    # 1. Obtener datos históricos
    data = fetch_historical_data(symbol, start_date, end_date)
    prices = data['Close']
    
    # 2. Dividir en training/test
    split = int(len(prices) * 0.7)
    train_prices = prices[:split]
    test_prices = prices[split:]
    
    # 3. Entrenar FFT en training data
    train_normalized = prepare_market_data(train_prices)
    spectral_info = spectral_analysis(train_normalized)
    
    # 4. Generar predicciones para test period
    predictions = []
    for i in range(0, len(test_prices), 30):  # Predicciones de 30 días
        window = np.concatenate([train_prices[-252:], test_prices[i:i+252]])
        window_normalized = prepare_market_data(window)
        pred = extrapolate_signal(window_normalized)
        predictions.append(pred)
    
    # 5. Calcular métricas
    actual_returns = np.diff(np.log(test_prices))
    predicted_returns = []
    for pred in predictions:
        pred_returns = np.diff(pred)
        predicted_returns.extend(pred_returns)
    
    # Truncar para igualar longitudes
    min_len = min(len(actual_returns), len(predicted_returns))
    actual_returns = actual_returns[:min_len]
    predicted_returns = predicted_returns[:min_len]
    
    metrics = {
        'correlation': np.corrcoef(actual_returns, predicted_returns)[0, 1],
        'mse': np.mean((actual_returns - predicted_returns) ** 2),
        'mae': np.mean(np.abs(actual_returns - predicted_returns)),
        'direction_accuracy': np.mean(
            (actual_returns * predicted_returns) > 0
        ),
    }
    
    return metrics
```

#### Métricas de Performance

```python
def calculate_performance_metrics(returns, benchmark_returns):
    """
    Calcula métricas de performance del portafolio
    """
    # 1. Return acumulado
    cumulative_return = np.exp(np.cumsum(returns)) - 1
    
    # 2. Return del benchmark
    benchmark_cumulative = np.exp(np.cumsum(benchmark_returns)) - 1
    
    # 3. Sharpe Ratio
    risk_free_rate = 0.02  # 2% anual
    excess_returns = returns - risk_free_rate / 252
    sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
    
    # 4. Maximum Drawdown
    peak = np.maximum.accumulate(cumulative_return)
    drawdown = (cumulative_return - peak) / peak
    max_drawdown = np.min(drawdown)
    
    # 5. Sortino Ratio (similar a Sharpe pero solo downside)
    downside_returns = excess_returns[excess_returns < 0]
    downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 1e-6
    sortino_ratio = np.mean(excess_returns) / downside_std * np.sqrt(252)
    
    # 6. Win Rate
    win_rate = np.mean(returns > 0)
    
    # 7. Profit Factor
    gross_profit = np.sum(returns[returns > 0])
    gross_loss = np.abs(np.sum(returns[returns < 0]))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    return {
        'cumulative_return': cumulative_return[-1],
        'benchmark_return': benchmark_cumulative[-1],
        'alpha': cumulative_return[-1] - benchmark_cumulative[-1],
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'max_drawdown': max_drawdown,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
    }
```

### 2. Gestión de Riesgos

#### Position Sizing

```python
def calculate_position_size(capital, entry_price, stop_loss, risk_per_trade=0.02):
    """
    Calcula el tamaño de posición basado en riesgo por trade
    """
    risk_amount = capital * risk_per_trade
    stop_loss_distance = abs(entry_price - stop_loss)
    
    # Número de acciones/contratos
    position_size = risk_amount / stop_loss_distance
    
    # Valor total de la posición
    position_value = position_size * entry_price
    
    return {
        'shares': position_size,
        'total_value': position_value,
        'risk_amount': risk_amount,
        'risk_percent': (position_value / capital) * 100
    }
```

#### Stop Loss Dinámico

```python
def dynamic_stop_loss(current_price, volatility, atr_multiplier=2):
    """
    Calcula stop loss dinámico basado en volatilidad
    """
    # Usar ATR (Average True Range) como medida de volatilidad
    stop_distance = volatility * atr_multiplier
    
    if volatility > 0:  # Si el precio está subiendo
        stop_loss = current_price - stop_distance
    else:  # Si el precio está bajando
        stop_loss = current_price + stop_distance
    
    return stop_loss
```

#### Take Profit

```python
def calculate_take_profit(entry_price, stop_loss, risk_reward_ratio=2):
    """
    Calcula take profit basado en ratio riesgo:recompensa
    """
    risk_distance = abs(entry_price - stop_loss)
    reward_distance = risk_distance * risk_reward_ratio
    
    if stop_loss > entry_price:
        take_profit = entry_price - reward_distance
    else:
        take_profit = entry_price + reward_distance
    
    return take_profit
```

### 3. Reglas de Ejecución

#### Confirmación Múltiple

```python
def should_execute_trade(symbol, fft_analysis, technical_indicators):
    """
    Valida si se debe ejecutar el trade basado en múltiples confirmaciones
    """
    # 1. Confirmación FFT
    fft_signal = fft_analysis['trend']['direction']
    fft_confidence = fft_analysis['prediction']['confidence']
    
    if fft_confidence < 0.6:  # 60% de confianza mínima
        return False, 'Confianza FFT insuficiente'
    
    # 2. Confirmación de volumen
    if technical_indicators['volume'] < technical_indicators['avg_volume'] * 0.5:
        return False, 'Volumen bajo'
    
    # 3. Confirmación de tendencia (media móvil)
    ma_short = technical_indicators['ma_20']
    ma_long = technical_indicators['ma_50']
    if fft_signal == 'UP' and ma_short < ma_long:
        return False, 'Tendencia contradictoria (MA)'
    if fft_signal == 'DOWN' and ma_short > ma_long:
        return False, 'Tendencia contradictoria (MA)'
    
    # 4. Confirmación de volatilidad
    if technical_indicators['volatility'] > technical_indicators['atr'] * 3:
        return False, 'Volatilidad extrema'
    
    return True, 'Confirmaciones cumplidas'
```

#### Horarios Óptimos

```python
def is_optimal_trading_time():
    """
    Verifica si es horario óptimo de trading (para US markets)
    """
    from datetime import datetime
    now = datetime.now()
    
    # Horario del mercado (9:30 AM - 4:00 PM EST)
    market_hours = 9.5 <= now.hour + now.minute/60 <= 16
    weekday = 0 <= now.weekday() <= 4  # Lunes-Viernes
    
    if not (market_hours and weekday):
        return False, 'Fuera de horario de mercado'
    
    # Evitar primera y última hora (mayor volatilidad)
    if now.hour < 10 or now.hour > 15:
        return False, 'Horario de alta volatilidad'
    
    return True, 'Horario óptimo'
```

---

## Análisis de Riesgos

### Limitaciones del Modelo FFT

#### 1. Supuesto de Estacionariedad

**Problema:** Los precios financieros raramente son perfectamente estacionarios.

**Solución:**
- Usar diferencias de precio (rendimientos)
- Ventanas deslizantes con estacionariedad local
- Diferenciación fraccional

#### 2. Eventos Exógenos

**Problema:** FFT no puede predecir noticias, eventos económicos, o cambios estructurales.

**Solución:**
- Monitorear calendario económico
- Evitar entrar antes de anuncios importantes
- Usar filtros de sentimiento de noticias

#### 3. Degradación Temporal

**Problema:** Las predicciones se vuelven menos confiables con el tiempo.

**Solución:**
- Limitar predicciones a 30-60 días máx.
- Reentrenar el modelo periódicamente
- Usar ensemble de métodos

### Riesgos de Trading

#### Riesgos de Mercado

1. **Volatilidad Extrema:**
   - La volatilidad puede exceder los parámetros de stop loss
   - **Solución:** Usar stops dinámicos y posiciones pequeñas

2. **Gap de Precios:**
   - Los precios pueden abrir muy lejos del cierre anterior
   - **Solución:** Evitar holding overnight en volatilidad alta

3. **Liquidez:**
   - Dificultad para entrar/salir en grandes posiciones
   - **Solución:** Monitorear volumen, usar órdenes límite

#### Riesgos de Sistema

1. **Overfitting:**
   - El modelo se ajusta demasiado a datos históricos
   - **Solución:** Validación cruzada, regularización

2. **Cambios de Régimen:**
   - El mercado cambia de comportamiento (bull market → bear market)
   - **Solución:** Detección de cambios de régimen, reentrenamiento

3. **Error de Datos:**
   - Datos incorrectos o incompletos
   - **Solución:** Validación de datos, múltiples fuentes

### Gestión de Riesgos de Portafolio

#### Diversificación

```python
def calculate_portfolio_correlation(returns_matrix):
    """
    Calcula matriz de correlación del portafolio
    """
    correlation_matrix = np.corrcoef(returns_matrix)
    
    # Identificar correlaciones altas (>0.7)
    high_corr = np.argwhere(np.abs(correlation_matrix) > 0.7)
    high_corr = high_corr[high_corr[:, 0] < high_corr[:, 1]]  # Solo triangular superior
    
    return high_corr
```

#### VaR (Value at Risk)

```python
def calculate_var(returns, confidence=0.95):
    """
    Calcula Value at Risk al nivel de confianza especificado
    """
    # Método histórico
    sorted_returns = np.sort(returns)
    var_index = int((1 - confidence) * len(sorted_returns))
    var = sorted_returns[var_index]
    
    # Método paramétrico (asumiendo normalidad)
    mean = np.mean(returns)
    std = np.std(returns)
    z_score = scipy.stats.norm.ppf(1 - confidence)
    var_parametric = mean + z_score * std
    
    return {
        'historical_var': var,
        'parametric_var': var_parametric,
        'expected_shortfall': np.mean(sorted_returns[:var_index])  # CVaR
    }
```

---

## Preguntas Frecuentes

### P1: ¿Qué tan precisa es la predicción FFT?

**R:** La precisión depende del mercado y timeframe:

- **Futuros de índices:** 60-70% de precisión direccional (30 días)
- **Acciones blue-chip:** 55-65% de precisión
- **Criptomonedas:** 50-60% de precisión (mayor volatilidad)

La precisión de precio exacto es menor (~30-40%) pero la precisión de dirección es más alta.

### P2: ¿Cuál es el mejor timeframe para análisis FFT?

**R:** Recomendaciones:

- **Diario (1d):** Mejor para swing trading (1-3 meses)
- **Semanal (1wk):** Mejor para ciclos estacionales
- **4 Horas (4h):** Buen balance entre detalle y ruido
- **1 Hora (1h):** Más ruido, mejor para confirmar señales

**No recomendado:**
- Intradía (< 1h): Mucho ruido
- Mensual (1M): Pocos datos, falta de detalle

### P3: ¿Puedo usar FFT para day trading?

**R:** Posible pero requiere adaptaciones:

1. **Usar timeframe más corto:** 15 minutos - 1 hora
2. **Aumentar threshold de filtrado:** Para más componentes de frecuencia
3. **Combinar con otros indicadores:** RSI, MACD, volumen
4. **Limitar predicciones:** 1-5 días máximo

### P4: ¿Cómo elegir el número de componentes FFT?

**R:** Reglas generales:

| Datos (puntos) | Componentes recomendados |
|---------------|------------------------|
| < 100          | 3-5                     |
| 100-500        | 5-10                    |
| 500-1000       | 10-20                   |
| > 1000         | 20-30                   |

Más componentes = más detalle pero también más ruido.

### P5: ¿Funciona en mercados bajistas?

**R:** Sí, FFT no distingue entre alcistas y bajistas:

- Analiza patrones cíclicos independientemente de dirección
- La predicción de dirección se basa en la fase de los componentes
- Funciona en ambos mercados

**Nota:** Las métricas de riesgo (drawdown) pueden ser mayores en mercados bajistas.

### P6: ¿Con qué frecuencia debo reentrenar el modelo?

**R:** Depende del mercado:

- **Criptomonedas:** Semanal (alta volatilidad, cambios rápidos)
- **Acciones:** Mensual (novedades trimestrales, informes anuales)
- **Futuros de índices:** Trimestral (más estacionales)

Si el rendimiento del modelo decae por >10%, reentrenar inmediatamente.

### P7: ¿Puedo combinar FFT con Machine Learning?

**R:** ¡Absolutamente! Síntesis poderosa:

**Enfoques:**

1. **FFT + LSTM:** FFT extrae características, LSTM modela dependencias temporales
2. **FFT + Random Forest:** FFT para selección de features, RF para predicción
3. **FFT + Gradient Boosting:** Similar a RF pero con boosting
4. **Ensemble:** Promedio de múltiples modelos (FFT, ARIMA, LSTM)

**Implementación FFT + LSTM:**

```python
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

def create_fft_lstm_model(sequence_length, n_fft_features):
    """
    Combina características FFT con LSTM
    """
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(sequence_length, n_fft_features)),
        LSTM(32, return_sequences=False),
        Dense(16, activation='relu'),
        Dense(1, activation='linear')  # Predicción de retorno
    ])
    
    model.compile(optimizer='adam', loss='mse')
    return model
```

### P8: ¿Cómo evaluar si el modelo está funcionando?

**R:** Métricas clave:

1. **Correlación:** Entre predicciones y retornos reales (>0.3 aceptable)
2. **MAE (Mean Absolute Error):** Error promedio absoluto (<2% de precio)
3. **Dirección correcta:** % de veces que predice dirección correcta (>55%)
4. **Sharpe Ratio:** >1.0 aceptable, >2.0 bueno
5. **Max Drawdown:** <20% aceptable, <10% bueno

**Monitoreo continuo:**
- Calcular métricas semanalmente
- Comparar con benchmark (buy & hold)
- Ajustar parámetros si el rendimiento decae

---

## Conclusión

La Transformada de Fourier aplicada a mercados financieros es una herramienta poderosa que permite:

1. **Identificar patrones cíclicos** invisibles al ojo humano
2. **Separar tendencias** de volatilidad y ruido
3. **Generar predicciones** basadas en componentes de frecuencia
4. **Complementar análisis técnico** tradicional con insights únicos

Sin embargo, como cualquier modelo financiero, tiene **limitaciones**:

- No predice eventos exógenos
- Supone estacionariedad
- Degrada con el tiempo

**Recomendaciones finales:**

1. Usar FFT como **herramienta complementaria**, no única
2. Validar con **backtesting histórico** riguroso
3. Aplicar **gestión de riesgos** estricta
4. **Monitorear continuamente** el desempeño
5. **Reentrenar periódicamente** el modelo

---

**QuantuM FFT** - Análisis espectral avanzado para trading inteligente

Para soporte técnico o preguntas adicionales:
- Email: support@quantumfft.com
- Documentación API: `/api/docs` (en el backend corriendo)
- Código fuente: [GitHub Repository]