# Cambios Realizados - Soporte para Futuros de Indices

## Resumen
Se ha actualizado el proyecto para soportar analisis de futuros de indices ademas de acciones. El algoritmo FFT recursivo ahora puede analizar tanto futuros (MNQ, MES, NQ, ES, etc.) como acciones individuales.

## Archivos Modificados

### 1. config.py
**Cambios:**
- Cambio de ticker por defecto de "AAPL" a "MNQ=F" (Micro Nasdaq-100)
- Agregado diccionario `FUTURES_SYMBOLS` con simbolos de futuros soportados
- Agregado diccionario `STOCK_SYMBOLS` con simbolos de acciones populares
- Agregado metodo `get_symbol_name()` para obtener nombre descriptivo del simbolo
- Agregado metodo `is_future()` para identificar si un simbolo es futuro o accion

**Simbolos de Futuros Agregados:**
- MNQ=F - Micro Nasdaq-100
- MES=F - Micro E-mini S&P 500
- MYM=F - Micro Dow Jones
- NQ=F - E-mini Nasdaq-100
- ES=F - E-mini S&P 500
- YM=F - E-mini Dow Jones
- RTY=F - E-mini Russell 2000
- M2K=F - Micro Russell 2000

### 2. market_data.py
**Cambios:**
- Deteccion automatica de tipo de instrumento (futuro/accion)
- Ajuste de precios de futuros (multiplicacion por factor)
- Mejorado manejo de errores en `fetch_data()`
- Agregado metodo `get_symbol_info()` para obtener informacion del simbolo
- Agregado metodo `fetch_multiple_tickers()` para descargar datos de multiples simbolos
- Agregado metodo estatico `get_available_symbols()` para listar simbolos disponibles

### 3. main.py
**Cambios:**
- Refactorizacion a funcion `analyze_ticker(ticker)` para aceptar cualquier simbolo
- Mostrar informacion detallada del simbolo (nombre, tipo, etc.)
- Mejorada presentacion de resultados con informacion de tipo de instrumento
- Agregada funcion `list_available_symbols()` para listar simbolos disponibles

### 4. README.md
**Cambios:**
- Seccion completa de simbolos soportados (futuros y acciones)
- Ejemplos de uso con futuros
- Explicacion de diferencias entre futuros y acciones
- Documentacion de nuevo script `analyze_futures.py`

## Archivos Nuevos

### 1. analyze_futures.py
**Funcionalidad:**
- Analisis comparativo de multiples futuros simultaneamente
- Tabla comparativa con tendencia, fuerza y confianza para cada futuro
- Detalle de ciclos dominantes para cada instrumento
- Salida resumida para facil comparacion

**Futuros Analizados:**
- MNQ=F (Micro Nasdaq-100)
- MES=F (Micro E-mini S&P 500)
- ES=F (E-mini S&P 500)
- NQ=F (E-mini Nasdaq-100)

### 2. example_stock.py
**Funcionalidad:**
- Ejemplo simple para analizar una accion (AAPL por defecto)
- Demostracion de funcion `analyze_ticker()`

## Como Usar

### Analizar un Futuro Individual
```bash
# Configurar el ticker deseado en config.py
# o llamar directamente:
python -c "from main import analyze_ticker; analyze_ticker('MNQ=F')"
```

### Analizar una Accion Individual
```bash
# Configurar el ticker deseado en config.py
# o usar el ejemplo:
python example_stock.py
```

### Analisis Comparativo de Futuros
```bash
python analyze_futures.py
```

### Listar Simbolos Disponibles
```python
from market_data import MarketData
symbols = MarketData.get_available_symbols()
print("Futuros:", symbols['futures'])
print("Acciones:", symbols['stocks'])
```

## Caracteristicas Especificas para Futuros

1. **Ajuste de Precios**: Los futuros se multiplican por un factor para representar el valor del contrato
2. **Identificacion Automatica**: El sistema detecta si el simbolo es futuro o accion
3. **Comparacion Multiple**: Posibilidad de analizar y comparar multiples futuros
4. **Nomenclatura**: Futuros usan formato "SYMBOL=F" en yfinance

## Resultados de Pruebas

### Futuro MNQ=F (Micro Nasdaq-100)
- Datos obtenidos: 505 puntos
- Rango de precios: $168,697.50 - $262,625.00
- Ciclo dominante: 2.0 dias
- Tendencia: DOWN (en la ejecucion de prueba)

### Analisis Comparativo
- 4 futuros analizados exitosamente
- Tabla comparativa generada
- Ciclos dominantes identificados para cada futuro

## Notas Importantes

- Los futuros tienen valores mas altos que las acciones
- La volatilidad de futuros puede ser mayor
- Los horarios de operacion pueden diferir
- Los datos se obtienen en tiempo real desde yfinance

## Scripts Disponibles

1. **main.py** - Analiza el simbolo configurado en Config.TICKER
2. **analyze_futures.py** - Analisis comparativo de multiples futuros
3. **example_stock.py** - Ejemplo de analisis de accion individual