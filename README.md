# Algoritmo FFT Recursivo para Prediccion de Mercado

Algoritmo recursivo de Transformada Rapida de Fourier (FFT) para predecir movimientos en los mercados financieros, incluyendo futuros de indices y acciones.

## Caracteristicas

- **FFT recursivo**: Implementacion propia del algoritmo Cooley-Tukey (O(n log n))
- **Trading en Vivo**: Sistema de scalping intradía con detección automática de señales
- **Integración MT5/NinjaTrader**: Conexión directa con plataformas de trading
- **Auto-Trading**: Ejecución automática de órdenes con gestión de riesgo
- **Futuros de indices**: Soporte para MNQ, MES, NQ, ES, YM, RTY
- **Acciones**: Soporte para acciones populares (AAPL, GOOGL, TSLA, etc.)
- **Prediccion de precio**: Extrapolacion basada en componentes de frecuencia
- **Analisis de tendencia**: Deteccion de componentes de baja frecuencia
- **Identificacion de ciclos**: Descubrimiento de patrones ciclicos dominantes
- **Analisis comparativo**: Comparacion multiple de futuros
- **Visualizaciones**: Graficos interactivos con lightweight-charts y Plotly
- **GUI Moderna**: Interfaz web con React y Tailwind CSS 

## Simbolos Soportados

### Futuros de Indices (E-mini y Micro)
| Simbolo | Descripcion |
|---------|-------------|
| MNQ=F | Micro Nasdaq-100 |
| MES=F | Micro E-mini S&P 500 |
| MYM=F | Micro Dow Jones |
| NQ=F | E-mini Nasdaq-100 |
| ES=F | E-mini S&P 500 |
| YM=F | E-mini Dow Jones |
| RTY=F | E-mini Russell 2000 |
| M2K=F | Micro Russell 2000 |

### Acciones Populares
| Simbolo | Descripcion |
|---------|-------------|
| AAPL | Apple Inc. |
| GOOGL | Alphabet Inc. |
| MSFT | Microsoft Corporation |
| TSLA | Tesla Inc. |
| AMZN | Amazon.com Inc. |
| META | Meta Platforms Inc. |
| NVDA | NVIDIA Corporation |

## Requisitos

- Python 3.7 o superior
- Dependencias listadas en `requirements.txt`

## Instalacion

```bash
pip install -r requirements.txt
```

## Configuracion

Edita `config.py` para personalizar:

```python
TICKER = "MNQ=F"             # Simbolo (futuro o accion)
PERIOD = "2y"                # Periodo de datos historicos
INTERVAL = "1d"              # Intervalo de tiempo (1d, 1wk, 1h)
PREDICTION_DAYS = 30         # Dias a predecir
FFT_COMPONENTS = 10          # Componentes de frecuencia a usar
FREQUENCY_THRESHOLD = 0.05   # Umbral de filtrado
```

## Uso

### Iniciar la Aplicación Completa

```bash
# Opción 1: Iniciar con interfaz gráfica (GUI)
python app.py

# Opción 2: Iniciar manualmente
# Terminal 1 - Backend
python backend/main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

La aplicación estará disponible en:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

### Trading en Vivo (Scalping Intradía)

El sistema incluye un módulo de trading en tiempo real que:

1. **Monitorea el mercado cada 5 segundos**
2. **Detecta señales de scalping** usando análisis FFT
3. **Calcula automáticamente TP y SL** con ATR (Average True Range)
4. **Valida señales** con criterios de riesgo (Risk:Reward ≥ 1.5:1)
5. **Ejecuta órdenes** automáticamente en MT5 o NinjaTrader

#### Acceso al Trading en Vivo

1. Abre la GUI en http://localhost:5173
2. Navega a **"Trading en Vivo"** en el menú lateral
3. Selecciona tu plataforma (MT5 o NinjaTrader)
4. Activa **"AUTO-TRADING"** para ejecución automática

#### Criterios de Detección de Señales

**Condiciones para generar señal:**
- Período de ciclo: 0.1 - 3.0 días (scalping intradía)
- Confianza mínima: 60%
- Fuerza de tendencia: > 30%
- Dirección clara: UP (BUY) o DOWN (SELL)

**Validación de señales:**
- Risk:Reward ratio ≥ 1.5:1
- Stop Loss ≤ 5% del precio de entrada
- Cálculo ATR para SL dinámico
- Take Profit = SL × 2.0 (ratio 2:1)

#### Clasificación de Señales

- **FUERTE**: Confianza ≥ 80%
- **MODERADA**: Confianza 65-79%
- **DÉBIL**: Confianza 60-64%

### Analizar un solo simbolo (Futuro o Accion)

```bash
python main.py
```

### Analisis comparativo de multiples futuros

```bash
python analyze_futures.py
```

### Listar simbolos disponibles

Desde Python:
```python
from market_data import MarketData
from config import Config

# Obtener simbolos disponibles
symbols = MarketData.get_available_symbols()
print("Futuros:", symbols['futures'])
print("Acciones:", symbols['stocks'])
```

### Cambiar simbolo a analizar

Opcion 1: Editar `config.py`:
```python
TICKER = "ES=F"  # E-mini S&P 500
```

Opcion 2: Modificar `main.py`:
```python
if __name__ == "__main__":
    analyze_ticker("NQ=F")  # E-mini Nasdaq-100
```

## Resultados

Resultados guardados en el directorio `results/`:

1. **price_prediction.png** - Precio historico vs prediccion
2. **spectrum.png** - Espectro de frecuencias (magnitud vs frecuencia)
3. **cycles.png** - Componentes ciclicos identificados
4. **decomposition.png** - Descomposicion de senal (tendencia + ciclos + residuo)
5. **trend_prediction.png** - Prediccion de tendencia con bandas de confianza

## Estructura del Proyecto

```
├── app.py                    # Lanzador principal de la aplicación
├── backend/
│   ├── main.py              # API FastAPI con WebSocket
│   ├── fft_recursive.py     # Implementación FFT Cooley-Tukey
│   ├── prediction.py        # Análisis espectral y predicción
│   └── visualization.py     # Generación de gráficos
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Analysis.jsx      # Análisis histórico
│   │   │   └── LiveTrading.jsx   # Trading en vivo
│   │   ├── components/           # Componentes reutilizables
│   │   └── services/api.js       # Cliente API
│   ├── package.json
│   └── vite.config.js
├── scalping_detector.py     # Detector de señales de scalping
├── market_data.py           # Obtención de datos (yfinance/MT5/Ninja)
├── mt5_connector.py         # Conector MetaTrader 5
├── ninjatrader_connector.py # Conector NinjaTrader
├── data_source_config.py    # Configuración de fuentes de datos
├── config.py                # Configuración global
├── requirements.txt         # Dependencias Python
└── README.md               # Documentación
```

## Ejemplo de Salida

```
============================================================
ALGORITMO FFT RECURSIVO PARA PREDICCION DE MERCADO
============================================================

Simbolo: MNQ=F
Nombre: Micro Nasdaq-100 (Futuro)
Tipo: Future
Periodo: 2y
Dias a predecir: 30
Intervalo: 1d

============================================================

[1/5] Obteniendo datos del mercado...
[OK] Datos obtenidos: 503 puntos
[OK] Rango de precios: $11235.00 - $20583.00

[2/5] Preparando senal para analisis...
[OK] Senal normalizada: media=-0.0000, std=1.0000

[3/5] Ejecutando analisis espectral con FFT recursivo...
[OK] Analisis completado
[OK] Componentes ciclicos identificados: 10
[OK] Ciclo dominante: periodo=1.0 dias, frecuencia=1.0020

[4/5] Generando predicciones...
[OK] Tendencia: UP
[OK] Fuerza de tendencia: 1.23
[OK] Confianza del modelo: 65.42%

[5/5] Creando visualizaciones...
[OK] 5 visualizaciones creadas

============================================================
RESUMEN DE RESULTADOS
============================================================

Prediccion para los proximos 30 dias:
  Precio inicial predicho: $18452.35
  Precio final predicho: $19123.87
  Cambio esperado: +3.64% (ALZA)

Analisis de ciclos:
  1. Periodo: 1.0 dias | Magnitud: 345.6789
  2. Periodo: 0.5 dias | Magnitud: 45.1234
  3. Periodo: 0.3 dias | Magnitud: 23.4567

Archivos generados:
  - results/price_prediction.png
  - results/spectrum.png
  - results/cycles.png
  - results/decomposition.png
  - results/trend_prediction.png

============================================================
¡ANALISIS COMPLETADO!
============================================================
```

## Diferencias entre Futuros y Acciones

1. **Precios**: Los futuros tienen valores mas altos y se multiplican por un factor (ej. MNQ x20, ES x50)
2. **Horarios**: Los futuros pueden tener horarios de operacion extendidos
3. **Volatilidad**: Los futuros de indices suelen ser mas volatiles que las acciones individuales
4. **Liquidez**: Los futuros principales (ES, NQ) tienen mayor liquidez que los micro futuros (MES, MNQ)

## Notas Importantes

- Este algoritmo es para fines educativos y de investigacion
- Las predicciones no deben usarse como consejo financiero
- Los mercados financieros son impredecibles y este modelo es simplificado
- Los futuros tienen riesgos adicionales: apalancamiento, margin calls, etc.
- Para uso en produccion, considera agregar validaciones mas rigurosas
- Siempre realiza tu propio analisis y consulta con un asesor financiero

## Dependencias

- numpy >= 1.21.0
- pandas >= 1.3.0
- yfinance >= 0.2.0
- seaborn >= 0.11.0
- matplotlib >= 3.4.0
- scipy >= 1.7.0
- fastapi >= 0.104.0
- uvicorn >= 0.24.0
- websockets >= 12.0
- MetaTrader5 (opcional, para integración MT5)

### Frontend
- React 18
- Vite 5
- Tailwind CSS 3
- lightweight-charts 4.1.3
- React Router 6
- Axios

---

## Sistema de Trading en Vivo - Flujo Detallado

### 1. Conexión y Monitoreo

```
┌─────────────────────────────────────────────────────────────┐
│ WebSocket se conecta cada 5 segundos                        │
│ ws://localhost:8001/ws/live/MNQ=F                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Obtiene precio en tiempo real desde MT5/NinjaTrader         │
│ [LIVE DATA] Symbol: MNQ=F, Price: 21234.5, Source: mt5     │
└─────────────────────────────────────────────────────────────┘
```

### 2. Análisis FFT

```
┌─────────────────────────────────────────────────────────────┐
│ Ejecuta análisis FFT en 200 puntos históricos               │
│ [FFT] Cycle: 1.2d, Trend: UP, Strength: 0.542, Conf: 0.78  │
└─────────────────────────────────────────────────────────────┘
                          ↓
        Extrae del análisis FFT:
        • Ciclo dominante (período en días)
        • Tendencia (UP/DOWN)
        • Fuerza de tendencia (0-1)
        • Confianza del modelo (0-1)
```

### 3. Detección de Señales

```
┌─────────────────────────────────────────────────────────────┐
│ Detector evalúa criterios:                                  │
│   ✓ Ciclo 1.2d ∈ [0.1, 3.0]?     → ✅ Sí                   │
│   ✓ Confianza 0.78 ≥ 0.60?       → ✅ Sí                   │
│   ✓ Fuerza 0.542 > 0.30?         → ✅ Sí                   │
│   → GENERA SEÑAL BUY                                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Cálculo de TP/SL con ATR:                                   │
│   ATR = 25.0 (volatilidad promedio)                         │
│   Entry = 21234.5                                           │
│   SL = Entry - (ATR × 1.5) = 21197.0                       │
│   TP = Entry + (ATR × 1.5 × 2.0) = 21309.5                │
│                                                              │
│ [SIGNAL DETECTED] BUY at 21234.5                           │
│   TP: 21309.5, SL: 21197.0, Confidence: 78%               │
└─────────────────────────────────────────────────────────────┘
```

### 4. Validación de Señales

```
┌─────────────────────────────────────────────────────────────┐
│ Valida criterios de riesgo:                                 │
│                                                              │
│   Risk = |Entry - SL| = |21234.5 - 21197.0| = 37.5        │
│   Reward = |TP - Entry| = |21309.5 - 21234.5| = 75.0      │
│   R:R = Reward/Risk = 75.0/37.5 = 2.00:1                  │
│                                                              │
│   ✓ R:R 2.00 ≥ 1.5?              → ✅ Válido               │
│   ✓ SL distance 0.18% < 5%?      → ✅ Válido               │
│                                                              │
│ [SIGNAL VALIDATION] Valid: True, R:R: 2.00:1               │
│ [SIGNAL STRENGTH] FUERTE                                    │
└─────────────────────────────────────────────────────────────┘
```

### 5. Ejecución de Órdenes

```
┌─────────────────────────────────────────────────────────────┐
│ Frontend recibe señal y muestra en panel                    │
│                                                              │
│ SI AUTO-TRADING ACTIVO:                                     │
│   → Ejecuta automáticamente                                 │
│                                                              │
│ SI AUTO-TRADING INACTIVO:                                   │
│   → Muestra botón "Ejecutar Manualmente"                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ executeSignal() → POST /api/live/execute                    │
│                                                              │
│ [ORDER] Executing BUY for MNQ=F on MT5                     │
│   Qty: 1, SL: 21197.0, TP: 21309.5                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ MT5Connector.send_order():                                  │
│   1. Conecta a MetaTrader 5                                 │
│   2. Verifica símbolo disponible                            │
│   3. Obtiene precio Ask actual                              │
│   4. Envía orden con:                                       │
│      - Magic Number: 234000                                 │
│      - Comment: "QuantumFFT"                                │
│      - Type: BUY                                            │
│      - Volume: 1.0                                          │
│      - SL: 21197.0                                          │
│      - TP: 21309.5                                          │
│   5. Retorna resultado                                      │
│                                                              │
│ [MT5] Order executed: #12345, volume: 1.0, price: 21235.0 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Frontend muestra confirmación                               │
│ ✅ "Orden BUY ejecutada en MT5"                            │
└─────────────────────────────────────────────────────────────┘
```

### Logs del Backend en Producción

Cuando el sistema está funcionando, verás logs como:

```bash
# Cada 5 segundos:
[LIVE DATA] Symbol: MNQ=F, Price: 21234.5, Source: mt5
[FFT] Cycle period: 1.2, Trend: UP, Strength: 0.542, Confidence: 0.782

# Si detecta señal:
[SIGNAL DETECTED] BUY at 21234.5, TP: 21309.5, SL: 21197.0, Confidence: 78.20%
[SIGNAL VALIDATION] Valid: True, R:R: 2.00:1
[SIGNAL STRENGTH] FUERTE

# Si no hay señal:
[NO SIGNAL] Waiting for scalping opportunity...

# Al ejecutar orden:
[ORDER] Executing BUY order for MNQ=F on MT5, Qty: 1, SL: 21197.0, TP: 21309.5
Connected to MetaTrader 5
MT5 version: (500, 5430, '14 Nov 2025')
Order executed: 12345, volume: 1.0, price: 21235.0
[MT5] Order result: {'order': 12345, 'volume': 1.0, 'price': 21235.0}
```

---

## Configuración de Plataformas de Trading

### MetaTrader 5 (MT5)

1. **Instalar librería Python**:
   ```bash
   pip install MetaTrader5
   ```

2. **Configurar símbolos en `data_source_config.py`**:
   ```python
   SYMBOL_MAPPINGS = {
       'MNQ': {
           SOURCE_MT5: 'NQ-MAR26'  # Símbolo específico de tu broker
       }
   }
   ```

3. **Abrir MetaTrader 5** en tu computadora antes de iniciar la aplicación

4. **Verificar conexión** en la GUI → Configuración → Fuente de Datos en Vivo → MT5

### NinjaTrader

1. **Configurar directorio de intercambio**:
   ```python
   # En data_source_config.py
   NINJA_EXCHANGE_DIR = r"C:\QuantumGAN\Exchange"
   ```

2. **Crear directorio** si no existe

3. **Sistema de archivos**:
   - NinjaTrader escribe: `data_MNQ_1min.csv`, `positions.csv`, `account.csv`
   - QuantumFFT escribe: `commands.txt` (formato: `BUY|MNQ|1|21197.0|21309.5`)

4. **Configurar script en NinjaTrader** para leer `commands.txt` y ejecutar órdenes

---
