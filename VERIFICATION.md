# Verificación de Sistema de Trading en Vivo

Este documento describe los procedimientos de verificación para el sistema de trading en vivo, incluyendo patrones de logs esperados, pasos de diagnóstico y criterios de éxito.

---

## 1. Verificación de Mapeo de Símbolos

### Procedimiento de Inicio

1. **Iniciar el Backend**:
   ```bash
   python backend/main.py
   ```

2. **Abrir la GUI** en el navegador:
   ```
   http://localhost:5173/live/MNQ=F
   ```

3. **Abrir DevTools Console** (F12)

### Patrones de Logs Esperados

#### ✅ **Escenario Exitoso - MT5 con Mapeo Correcto**:

```
[WS INIT] Symbol: MNQ=F, Data source: mt5
[WS INIT] Decoded symbol: MNQ=F
[FETCH] Ticker: MNQ=F, Source: mt5, Mapped: NQ-MAR26, Interval: 1min
Connected to MetaTrader 5
MT5 version: (500, 5430, '14 Nov 2025')
[DATA] Using 1min OHLC from mt5
[LIVE DATA] Symbol: MNQ=F, Price: 21234.5, Source: mt5
[FFT] Cycle period: 1.2, Trend: UP, Strength: 0.542, Confidence: 0.782
[OK] Sending 100 real OHLC candles (1min)
[SEND] Response sent - Price: 21234.5, Trend: UP, Historical candles: 100
```

#### ✅ **Escenario Exitoso - NinjaTrader**:

```
[WS INIT] Symbol: MNQ=F, Data source: ninjatrader
[WS INIT] Decoded symbol: MNQ=F
[FETCH] Ticker: MNQ=F, Source: ninjatrader, Mapped: MNQ, Interval: 1min
[DATA] Using 1min OHLC from ninjatrader
[LIVE DATA] Symbol: MNQ=F, Price: 21234.5, Source: ninjatrader
[OK] Sending 100 real OHLC candles (1min)
```

#### ⚠️ **Fallback a yfinance (sin MT5/Ninja configurado)**:

```
[WS INIT] Symbol: MNQ=F, Data source: yfinance
[WS INIT] Decoded symbol: MNQ=F
[FETCH] Ticker: MNQ=F, Source: yfinance, Mapped: MNQ=F, Interval: 5min
[DATA] Using 5min OHLC from yfinance (1min not available)
[LIVE DATA] Symbol: MNQ=F, Price: 21234.5, Source: yfinance
[OK] Sending 100 real OHLC candles (1min)
```

#### ❌ **Error - Símbolo No Encontrado**:

```
[WS INIT] Symbol: MNQ=F, Data source: mt5
[WS INIT] Decoded symbol: MNQ=F
[FETCH] Ticker: MNQ=F, Source: mt5, Mapped: NQ-MAR26, Interval: 1min
Connected to MetaTrader 5
[ERROR] Exception in WebSocket loop: No data available for NQ-MAR26 from MT5. Error: ...
```

#### ❌ **Error - Mapeo Incorrecto**:

```
[WS INIT] Symbol: MNQ=F, Data source: mt5
[WS INIT] Decoded symbol: MNQ=F
[FETCH] Ticker: MNQ=F, Source: mt5, Mapped: MNQ=F, Interval: 1min
[ERROR] Exception in WebSocket loop: No data found for ticker MNQ=F
```

---

## 2. Pasos de Diagnóstico

### Problema 1: "No data found for ticker MNQ=F"

**Causa**: El símbolo no se está mapeando correctamente para MT5/NinjaTrader.

**Solución**:

1. **Verificar configuración de fuente de datos**:
   ```bash
   # Verificar si data_source_config.json existe
   ls data_source_config.json
   ```

2. **Revisar mapeo en `data_source_config.py`** (líneas 29-51):
   ```python
   SYMBOL_MAPPINGS = {
       'MNQ': {
           SOURCE_YFINANCE: 'MNQ=F',
           SOURCE_NINJATRADER: 'MNQ',
           SOURCE_MT5: 'NQ-MAR26'  # ← Verificar símbolo correcto de tu broker
       }
   }
   ```

3. **Verificar símbolo en MT5**:
   - Abrir MT5 → Market Watch
   - Buscar el símbolo correcto (puede ser `NQ-MAR26`, `NQH26`, `MNQH26`, etc.)
   - Actualizar el mapeo con el símbolo exacto

4. **Actualizar mapeo manualmente**:
   ```python
   # En data_source_config.py, cambiar:
   SOURCE_MT5: 'SIMBOLO_CORRECTO_DE_TU_BROKER'
   ```

### Problema 2: "Data source is yfinance but should be mt5"

**Causa**: La fuente de datos en tiempo real no está configurada como MT5.

**Solución**:

1. **Verificar GUI → Configuración → Fuente de Datos en Vivo**
   - Debe estar seleccionado "MT5" o "NinjaTrader"

2. **O configurar manualmente en `data_source_config.json`**:
   ```json
   {
     "realtime_source": "mt5",
     "historical_source": "yfinance"
   }
   ```

3. **O usar la API**:
   ```bash
   curl -X POST http://localhost:8001/api/config/realtime-source \
     -H "Content-Type: application/json" \
     -d '{"source": "mt5"}'
   ```

### Problema 3: Velas no coinciden con MT5/NinjaTrader

**Causa**: Timeframe incorrecto o datos históricos vs tiempo real.

**Solución**:

1. **Verificar logs de timeframe**:
   ```
   [DATA] Using 1min OHLC from mt5  ← Debe ser 1min para MT5/Ninja
   [DATA] Using 5min OHLC from yfinance  ← Solo si es yfinance
   ```

2. **Verificar que MT5/Ninja esté enviando datos de 1min**:
   - En `mt5_connector.py` línea 73: `'1min': mt5.TIMEFRAME_M1`
   - En `ninjatrader_connector.py` línea 46: `'1min': '1min'`

3. **Verificar que el gráfico use temporalidad de 1 minuto**:
   - En `LiveTrading.jsx` línea 126: `Math.floor(time / 60) * 60`

---

## 3. Verificación de Actualización en Tiempo Real

### Patrones de Logs (cada 5 segundos)

#### Frontend (Console del Navegador):

```javascript
// Recepción de mensaje
📡 Mensaje WebSocket recibido: {hasPrice: true, price: 21234.7, hasHistoricalData: true, ...}

// Primera carga
[WS] Historical data received: 100 candles
[WS] Loading historical data into chart
[WS] Historical data loaded successfully

// Actualizaciones en tiempo real
[WS] Calling updateChart with price: 21234.7 timestamp: 1737340567
[CHART UPDATE] Price: 21234.7, Timestamp: 1737340567, Current minute: 1737340560
[CHART] Last candle: {time: 1737340560, open: 21230, high: 21235, low: 21228, close: 21234.5}
[CHART] Comparing times - Last: 1737340560, Current: 1737340560
[CHART] Updating existing candle: {time: 1737340560, open: 21230, high: 21235, low: 21228, close: 21234.7}
```

#### Backend (Terminal):

```
[LIVE DATA] Symbol: MNQ=F, Price: 21234.7, Source: mt5
[FFT] Cycle period: 1.2, Trend: UP, Strength: 0.542, Confidence: 0.782
[NO SIGNAL] Waiting for scalping opportunity...
[SEND] Response sent - Price: 21234.7, Trend: UP, Historical candles: 0
```

### Criterios de Éxito

✅ **Sistema Funcionando Correctamente**:

1. **Conexión Establecida**:
   - Backend muestra: `INFO: connection open`
   - Frontend muestra indicador verde: "EN VIVO"

2. **Mapeo Correcto**:
   - Logs muestran: `Mapped: NQ-MAR26` (o símbolo correcto de tu broker)
   - NO muestra: `Mapped: MNQ=F` cuando fuente es MT5/Ninja

3. **Datos OHLC Reales**:
   - Logs muestran: `[DATA] Using 1min OHLC from mt5`
   - Logs muestran: `[OK] Sending 100 real OHLC candles (1min)`

4. **Velas Actualizándose**:
   - Logs muestran cada 5s: `[CHART] Updating existing candle` o `[CHART] Creating new candle`
   - Gráfico muestra velas idénticas a MT5/NinjaTrader

5. **Precio en Tiempo Real**:
   - Panel "Datos en Tiempo Real" muestra precio actualizado
   - Precio coincide con MT5/NinjaTrader

6. **FFT Funcionando**:
   - Logs muestran: `[FFT] Cycle period: X, Trend: UP/DOWN, Strength: X, Confidence: X`
   - Valores de confianza razonables (0.5 - 0.9)

---

## 4. Troubleshooting por Síntoma

### Síntoma: Gráfico Negro / No Aparece

**Verificar**:
1. ¿Aparece el log `[WS] Loading historical data into chart`?
   - No → Backend no está enviando datos históricos
   - Sí → Problema en frontend

2. ¿Aparece el log `[OK] Sending X real OHLC candles`?
   - No → Error al preparar datos OHLC
   - Revisar traceback completo

3. ¿Hay errores en Console del navegador?
   - `candleSeriesRef not available` → Gráfico no inicializado
   - `Failed to load historical data` → Formato de datos incorrecto

**Solución**:
- Verificar que `lightweight-charts` esté instalado: `npm list lightweight-charts`
- Recargar página (F5)
- Revisar logs completos de frontend

### Síntoma: Velas no se Actualizan en Tiempo Real

**Verificar**:
1. ¿Aparece log `[CHART UPDATE]` cada 5 segundos?
   - No → WebSocket no está recibiendo datos
   - Sí → Problema con `updateChart()`

2. ¿El timestamp está correcto?
   - Debe ser Unix timestamp en segundos
   - Ejemplo correcto: `1737340567`
   - Ejemplo incorrecto: `1737340567000` (milisegundos)

3. ¿Se está actualizando el estado `priceHistory`?
   - Logs muestran: `[CHART] Last candle: {time: ...}`
   - Si `Last candle: undefined` → Estado no inicializado

**Solución**:
- Verificar que `data.timestamp` existe en respuesta WebSocket
- Verificar multiplicación por 1000: `data.timestamp * 1000`
- Revisar lógica de comparación de minutos en `updateChart()`

### Síntoma: Velas Diferentes a MT5/NinjaTrader

**Verificar**:
1. ¿Qué fuente de datos está usando?
   - `[DATA] Using 1min OHLC from mt5` → Correcto
   - `[DATA] Using 5min OHLC from yfinance` → Cambiará temporalidad

2. ¿El mapeo de símbolo es correcto?
   - Verificar que `Mapped: NQ-MAR26` coincida con símbolo en MT5

3. ¿Los datos OHLC son reales o simulados?
   - Logs deben mostrar: `real OHLC candles`
   - NO debe mostrar: valores como `close * 1.001` para high

**Solución**:
- Configurar fuente en tiempo real como MT5
- Verificar mapeo de símbolo en `data_source_config.py`
- Reiniciar backend después de cambios

---

## 5. Comandos Útiles de Verificación

### Verificar Estado del Sistema

```bash
# Ver configuración actual
cat data_source_config.json

# Ver mapeos de símbolos
grep -A 5 "SYMBOL_MAPPINGS" data_source_config.py

# Ver logs del backend en tiempo real
python backend/main.py 2>&1 | grep -E "\[WS INIT\]|\[FETCH\]|\[DATA\]|\[ERROR\]"

# Verificar puerto del backend
netstat -an | grep 8001

# Verificar WebSocket
curl http://localhost:8001/api/live/signals/MNQ=F
```

### Verificar Instalación de Dependencias

```bash
# Frontend
cd frontend
npm list lightweight-charts

# Backend
pip list | grep MetaTrader5
python -c "import MetaTrader5 as mt5; print(mt5.version())"
```

### Test Manual de Mapeo

```python
# Ejecutar en Python
from data_source_config import DataSourceConfig
from market_data import MarketData

# Test de mapeo
ds = DataSourceConfig()
print(f"Realtime source: {ds.get_realtime_source()}")
print(f"MNQ mapped to MT5: {ds.map_symbol('MNQ', 'mt5')}")

# Test de fetch
md = MarketData('MNQ=F', 'mt5')
data = md.fetch_data(period='1d', interval='1min')
print(f"Data shape: {data.shape}")
print(f"Columns: {data.columns.tolist()}")
```

---

## 6. Criterios de Éxito Final

### ✅ Sistema Completamente Operativo

- [ ] Backend inicia sin errores
- [ ] Frontend muestra indicador "EN VIVO" verde
- [ ] Logs muestran mapeo correcto del símbolo
- [ ] Logs muestran `Using 1min OHLC from mt5/ninjatrader`
- [ ] Gráfico muestra 100 velas históricas al cargar
- [ ] Velas se actualizan cada 5 segundos
- [ ] Velas coinciden con las de MT5/NinjaTrader
- [ ] Precio en tiempo real se actualiza
- [ ] Análisis FFT muestra tendencia y confianza
- [ ] Señales de scalping se detectan cuando aplica
- [ ] Auto-trading puede activarse sin errores

### 📊 Comparación Visual

Para verificar que las velas son correctas:

1. Abre MT5/NinjaTrader en timeframe 1min
2. Abre la GUI en `http://localhost:5173/live/MNQ=F`
3. Compara las últimas 10 velas:
   - ✅ Open, High, Low, Close deben ser idénticos
   - ✅ Timestamps deben coincidir (minuto exacto)
   - ✅ Colores (verde/rojo) deben coincidir

Si hay diferencias:
- Verificar que ambos usan el mismo símbolo
- Verificar que ambos usan timeframe 1min
- Verificar que no hay retraso en datos (delay)

---

## 7. Contacto y Soporte

Si después de seguir todos los pasos el sistema no funciona:

1. **Recopilar información**:
   - Logs completos del backend (últimos 50 líneas)
   - Logs de Console del navegador (F12)
   - Símbolo que estás intentando usar
   - Broker de MT5 que usas
   - Versión de MT5

2. **Verificar requisitos**:
   - Python 3.10+
   - Node.js 18+
   - MetaTrader5 package instalado
   - MT5 abierto y conectado
   - Símbolo disponible en Market Watch de MT5

3. **Probar con símbolo de prueba**:
   - Usar yfinance temporalmente: Cambiar `realtime_source` a `yfinance`
   - Si funciona con yfinance, el problema es el conector MT5/Ninja
   - Si no funciona con yfinance, el problema es el WebSocket o frontend
