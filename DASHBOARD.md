# Dashboard Interactivo - FFT para Prediccion de Mercado

Se ha transformado la terminal en un dashboard interactivo profesional con tablas formateadas, visualizaciones claras y opciones de menú para analizar futuros de índices y acciones.

## Características del Dashboard

### Interfaz de Usuario Profesional
- **Tablas formateadas** con Rich - información clara y legible
- **Colores semánticos** - verde para alza, rojo para baja
- **Barras de progreso** visuales durante el procesamiento
- **Métricas de confianza** con indicadores visuales
- **Layouts profesionales** con paneles y secciones organizadas

### Visualizaciones en Terminal
1. **Información del Instrumento** - datos básicos del símbolo
2. **Resumen Ejecutivo** - tendencia, confianza, ciclo dominante
3. **Análisis de Tendencia** - dirección, fuerza, componentes
4. **Análisis de Ciclos** - tabla de 10 ciclos principales
5. **Resumen Espectral** - métricas de frecuencia
6. **Medidor de Confianza** - barra visual de porcentaje
7. **Tabla de Predicciones** - precios para los próximos 30 días

### Menú Interactivo
```
MENU PRINCIPAL

1. Analizar un unico instrumento (Futuro/Accion)
2. Analisis comparativo de multiples futuros
3. Lista de simbolos disponibles
4. Configuracion
5. Ver resultados anteriores
6. Salir
```

## Scripts Disponibles

### 1. app_ascii.py (Recomendado)
Versión ASCII sin emojis para máxima compatibilidad.

```bash
# Analizar un símbolo específico
python app_ascii.py MNQ=F

# Analizar acción
python app_ascii.py AAPL
```

**Salida de ejemplo:**
```
            Informacion del Instrumento             
+--------------------------------------------------+
| Propiedad            | Valor                     |
|----------------------+---------------------------|
| Simbolo              | MNQ=F                     |
| Nombre               | Micro Nasdaq-100 (Futuro) |
| Tipo                 | Future                    |
| Puntos de datos      | 505                       |
| Precio Minimo        | $168,697.50               |
| Precio Maximo        | $262,625.00               |
| Precio Actual        | $256,890.00               |
+--------------------------------------------------+
```

### 2. app_simple.py
Versión con menú interactivo básico.

```bash
python app_simple.py
```

### 3. app.py
Versión completa con `questionary` para terminales modernas.

**Nota:** Requiere terminal compatible (no funciona en todos los entornos).
```bash
python app.py
```

## Componentes del Dashboard

### TerminalDashboardASCII
Clase principal que genera todas las visualizaciones en la terminal:

```python
from dashboard_ascii import TerminalDashboardASCII

dashboard = TerminalDashboardASCII()

# Mostrar información del símbolo
dashboard.show_symbol_info_table(symbol_info, data)

# Mostrar resumen
dashboard.show_summary_dashboard(symbol_info, analysis, prediction, data)

# Mostrar análisis de tendencia
dashboard.show_trend_analysis(analysis)

# Mostrar ciclos
dashboard.show_cycles_table(cycles_data)

# Mostrar resumen espectral
dashboard.show_spectral_summary(spectral)

# Mostrar medidor de confianza
dashboard.show_confidence_meter(confidence)

# Mostrar tabla de predicciones
dashboard.show_prediction_table(prediction, config)
```

## Ejemplo Completo de Uso

### Análisis Individual

```bash
# Analizar futuro MNQ=F
python app_ascii.py MNQ=F
```

**Resultado:**
1. Progreso de 5 pasos con indicadores visuales
2. Tabla de información del instrumento
3. Dashboard de resumen con:
   - Símbolo, Nombre, Tipo
   - Tendencia (UP/DOWN en color)
   - Confianza del modelo
   - Ciclo dominante
4. Tabla de análisis de tendencia
5. Tabla de 10 ciclos detectados
6. Resumen espectral con métricas
7. Medidor de confianza visual
8. Tabla de predicciones para 30 días
9. Lista de visualizaciones generadas

### Análisis Comparativo

```python
from app_ascii import FFTDashboardAppASCII

app = FFTDashboardAppASCII()

# Comparar múltiples futuros
app.analyze_multiple_futures()
```

**Resultado:**
- Tabla comparativa de 4 futuros principales
- Detalles de ciclos dominantes para cada uno
- Top 3 ciclos por instrumento

## Visualizaciones Generadas

Además de las tablas en terminal, se generan 5 archivos PNG en `results/`:

1. **price_prediction.png** - Precio histórico vs predicción
2. **spectrum.png** - Espectro de frecuencias
3. **cycles.png** - Componentes cíclicos identificados
4. **decomposition.png** - Descomposición de señal
5. **trend_prediction.png** - Predicción de tendencia

## Dependencias

```txt
rich>=13.0.0          # Tablas y formato de terminal
questionary>=2.0.0    # Menús interactivos (opcional)
numpy>=1.21.0
pandas>=1.3.0
yfinance>=0.2.0
seaborn>=0.11.0
matplotlib>=3.4.0
scipy>=1.7.0
```

## Instalación

```bash
pip install -r requirements.txt
```

## Casos de Uso

### Caso 1: Análisis Rápido de un Futuro
```bash
python app_ascii.py ES=F
```

### Caso 2: Comparación de Futuros Principales
```python
from app_ascii import FFTDashboardAppASCII

app = FFTDashboardAppASCII()
app.analyze_multiple_futures()
```

### Caso 3: Análisis de Acción Específica
```bash
python app_ascii.py AAPL
```

## Personalización

### Cambiar el Número de Predicciones
En `config.py`:
```python
PREDICTION_DAYS = 30  # Cambiar a 60, 90, etc.
```

### Ajustar Componentes FFT
En `config.py`:
```python
FFT_COMPONENTS = 10  # Cambiar a 5, 15, 20, etc.
```

### Modificar Umbral de Frecuencia
En `config.py`:
```python
FREQUENCY_THRESHOLD = 0.05  # Ajustar para más/menos filtrado
```

## Interpretación de Resultados

### Tendencia
- **UP** (verde) - Precio proyectado al alza
- **DOWN** (rojo) - Precio proyectado a la baja

### Confianza del Modelo
- **Alta (>=70%)** - Modelo confiable
- **Media (40-69%)** - Confianza moderada
- **Baja (<40%)** - Baja confianza en predicción

### Ciclos
- **Período**: Días del ciclo (menor = más corto)
- **Frecuencia**: Frecuencia del ciclo (mayor = más frecuente)
- **Magnitud**: Importancia del ciclo en la señal

## Troubleshooting

### Errores de Codificación en Windows
```bash
# Usa la versión ASCII
python app_ascii.py MNQ=F
```

### Visualizaciones No Se Abren
```bash
# Abre el directorio manualmente
cd results
# Abre los archivos PNG con tu visor de imágenes
```

### Problemas con `questionary`
```bash
# Usa la versión simple sin interactividad avanzada
python app_simple.py
```

## Rendimiento

- Tiempo de análisis: ~30-60 segundos por instrumento
- Uso de memoria: ~200-500 MB
- Datos requeridos: 2-3 años de datos históricos

## Soporte de Símbolos

### Futuros de Índices
- MNQ=F (Micro Nasdaq-100)
- MES=F (Micro S&P 500)
- NQ=F (E-mini Nasdaq-100)
- ES=F (E-mini S&P 500)
- YM=F (E-mini Dow Jones)
- RTY=F (E-mini Russell 2000)

### Acciones
- AAPL (Apple)
- GOOGL (Alphabet)
- MSFT (Microsoft)
- TSLA (Tesla)
- AMZN (Amazon)
- META (Meta)
- NVDA (NVIDIA)

## Próximas Mejoras

- [ ] Interfaz web con Flask/FastAPI
- [ ] Alertas por email/sms
- [ ] Backtesting de estrategias
- [ ] Integración con más APIs de datos
- [ ] Análisis de sentimiento de noticias
- [ ] Machine learning avanzado