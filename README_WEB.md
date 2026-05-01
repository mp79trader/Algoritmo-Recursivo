# QuantuM FFT - Interfaz Web Profesional

Sistema web profesional para análisis de mercados financieros utilizando el algoritmo FFT recursivo.

## 🚀 Inicio Rápido

### Requisitos Previos
- Node.js 18+ 
- Python 3.10+
- pip

### Instalación del Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

El backend estará disponible en `http://localhost:8000`

### Instalación del Frontend

```bash
cd frontend
npm install
npm run dev
```

El frontend estará disponible en `http://localhost:3000`

## 📁 Estructura del Proyecto

```
QuantuM FFT/
├── frontend/                 # React + Vite
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   ├── pages/           # Páginas principales
│   │   ├── services/        # API services
│   │   ├── styles/          # Estilos personalizados
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/                  # FastAPI
│   ├── app/
│   │   ├── api/            # Rutas API
│   │   ├── models/         # Modelos de datos
│   │   └── services/        # Lógica de negocio
│   ├── main.py
│   └── requirements.txt
│
├── docs/                     # Documentación técnica
├── algorithms/               # FFT recursivo existente
│   ├── fft_recursive.py
│   ├── prediction.py
│   ├── market_data.py
│   ├── visualization.py
│   └── config.py
│
└── README_WEB.md             # Este archivo
```

## 🎨 Sistema de Diseño

Basado en el estilo de llamaia.nbmsystemas.com:

### Colores Principales
- **Primary BG:** `#0a0a0f` - Fondo principal
- **Secondary BG:** `#1e1e24` - Fondo secundario
- **Accent Gold:** `#fbbf24` - Acento principal
- **Text Primary:** `#ffffff` - Texto principal
- **Text Secondary:** `#a0aec0` - Texto secundario

### Tipografía
- **Inter** - Fuente principal
- **JetBrains Mono** - Fuente monoespaciada

## 📱 Páginas Disponibles

### 1. Home Page (`/`)
- Hero section con branding
- Características principales
- Selección de tipos de mercado
- Información técnica básica

### 2. Dashboard (`/dashboard`)
- Selección de tipo de mercado
- Selector de símbolo
- Configuración de parámetros
- Ejecución de análisis

### 3. Analysis (`/analysis/:symbol`)
- Información del instrumento
- Dashboard de resumen
- Gráficos de predicción
- Análisis de tendencias
- Análisis de ciclos
- Tabla de predicciones

### 4. Compare (`/compare`)
- Comparación múltiple de símbolos
- Tabla comparativa
- Gráficos superpuestos

### 5. Documentation (`/documentation`)
- Algoritmo FFT Recursivo
- Fundamentos matemáticos
- Guía de uso
- FAQ

### 6. History (`/history`)
- Historial de análisis
- Filtros y búsqueda
- Re-ejecución de análisis

### 7. Settings (`/settings`)
- Configuración global
- Preferencias de visualización
- Configuración de alertas

## 🔌 API Endpoints

### Market Data
```python
GET  /api/markets/types              # Tipos de mercado
GET  /api/markets/symbols/{type}    # Símbolos por tipo
GET  /api/markets/data/{symbol}     # Datos históricos
```

### Analysis
```python
POST /api/analysis/execute          # Ejecutar análisis
GET  /api/analysis/{id}            # Obtener análisis
GET  /api/analysis/history         # Historial
```

### Comparison
```python
POST /api/compare/execute          # Comparar símbolos
GET  /api/compare/results/{id}     # Resultados comparación
```

## 📊 Tipos de Mercado Soportados

### Futuros de Índices
- MNQ=F (Micro Nasdaq-100)
- MES=F (Micro E-mini S&P 500)
- NQ=F (E-mini Nasdaq-100)
- ES=F (E-mini S&P 500)
- YM=F (E-mini Dow Jones)
- RTY=F (E-mini Russell 2000)
- M2K=F (Micro Russell 2000)
- MYM=F (Micro Dow Jones)

### Acciones
- AAPL (Apple)
- GOOGL (Alphabet)
- MSFT (Microsoft)
- TSLA (Tesla)
- AMZN (Amazon)
- META (Meta)
- NVDA (NVIDIA)

### Criptomonedas
- BTC-USD (Bitcoin)
- ETH-USD (Ethereum)
- SOL-USD (Solana)
- ADA-USD (Cardano)
- DOT-USD (Polkadot)

### ETFs
- SPY (SPDR S&P 500)
- QQQ (Invesco QQQ Trust)
- IWM (iShares Russell 2000)
- GLD (SPDR Gold Shares)

## 🎯 Features Principales

### 1. Análisis FFT Recursivo
- Implementación Cooley-Tukey O(n log n)
- Filtrado adaptativo de frecuencias
- Detección automática de ciclos

### 2. Visualizaciones Interactivas
- Gráficos con Plotly.js
- Zoom y pan en gráficos
- Exportación a PNG
- Descarga de datos (CSV/Excel)

### 3. Predicciones
- Predicción de precios futuros
- Análisis de tendencia (UP/DOWN)
- Detección de ciclos dominantes
- Métricas de confianza

### 4. Backtesting
- Simulación histórica
- Métricas de performance
- Drawdown analysis
- Sharpe ratio

### 5. Sistema de Alertas
- Email notifications
- SMS (Twilio)
- Push notifications
- Webhooks personalizados

## 🔧 Configuración

### Backend (`backend/config.py`)
```python
TICKER = "MNQ=F"              # Símbolo por defecto
PERIOD = "2y"                # Período de datos
INTERVAL = "1d"              # Intervalo de tiempo
PREDICTION_DAYS = 30         # Días a predecir
FFT_COMPONENTS = 10          # Componentes FFT
FREQUENCY_THRESHOLD = 0.05   # Umbral de frecuencia
```

### Frontend (`.env`)
```bash
VITE_API_URL=http://localhost:8000
```

## 📚 Documentación Técnica

### Algoritmo FFT Recursivo

#### Fundamento Matemático
La Transformada de Fourier descompone una señal en sus componentes de frecuencia fundamentales:

```
X(k) = Σ x(n) * e^(-i2πkn/N)
     n=0
```

#### Algoritmo Cooley-Tukey
Implementación recursiva que divide el problema en subproblemas más pequeños:

```python
def fft_recursive(x):
    n = len(x)
    if n <= 1:
        return x
    
    even = fft_recursive(x[::2])
    odd = fft_recursive(x[1::2])
    
    T = exp(-2j * π * k / n) * odd
    return concatenate([even + T, even - T])
```

#### Aplicación a Finanzas
- **Baja frecuencia:** Tendencias de largo plazo
- **Media frecuencia:** Ciclos estacionales
- **Alta frecuencia:** Volatilidad y ruido

### Uso en Producción

#### 1. Validación del Modelo
- Backtesting histórico (2-3 años)
- Forward-testing (últimos 6 meses)
- Métricas de performance
- Validación cruzada

#### 2. Gestión de Riesgos
- Position sizing (1-2% del capital)
- Stop-loss dinámico (2-3% del precio)
- Take-profit (3-4% del precio)
- Diversificación (máx. 5 posiciones)

#### 3. Ejecución
- Confirmar con múltiples indicadores
- Horarios óptimos (9:30-16:00 EST)
- Evitar noticias importantes
- Monitorización en tiempo real

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd frontend
npm run build
vercel deploy
```

### Backend (Railway/Render)
```bash
cd backend
pip install -r requirements.txt
# Deploy en Railway/Render
```

### Docker
```bash
docker-compose up -d
```

## 📞 Soporte

### Documentación
- Guía de inicio: `docs/quickstart.md`
- API Reference: `docs/api.md`
- Algoritmos: `docs/algorithms.md`
- FAQ: `docs/faq.md`

### Contacto
- Email: support@quantumfft.com
- Issues: GitHub Issues

## 📄 Licencia

Proprietary - Todos los derechos reservados

---

**QuantuM FFT** - Potenciando tus decisiones de trading con análisis espectral avanzado.