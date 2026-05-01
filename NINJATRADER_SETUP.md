# Guía de Configuración: NinjaTrader

## Configuración Rápida para NinjaTrader

### 1. Cambiar la Fuente de Datos a NinjaTrader

Edita `data_source_config.json` y cambia:

```json
{
    "realtime_source": "ninjatrader",  // Cambiar de "mt5" a "ninjatrader"
    "historical_source": "yfinance",
    "ninja_exchange_dir": "C:\\QuantumGAN\\Exchange",  // Verificar esta ruta
    ...
}
```

O usa el API desde la GUI o terminal:

```bash
# Desde Python
from data_source_config import DataSourceConfig
config = DataSourceConfig()
config.set_realtime_source('ninjatrader')
```

### 2. Verificar Directorio de Intercambio

El sistema usa archivos para comunicarse con NinjaTrader. Verifica que la ruta sea correcta:

**Ruta por defecto**: `C:\QuantumGAN\Exchange`

Si tu directorio es diferente, actualiza la configuración:

```json
{
    "ninja_exchange_dir": "C:\\TU_RUTA\\Exchange"
}
```

### 3. Mapeo de Símbolos

El sistema mapea automáticamente los símbolos:

| Símbolo Interno | NinjaTrader | yfinance | MT5 |
|-----------------|-------------|----------|-----|
| MNQ | MNQ | MNQ=F | MNQH26 |
| MES | MES | MES=F | ES-MAR26 |
| NQ | NQ | NQ=F | NQ |
| ES | ES | ES=F | ES |

**Para agregar más símbolos**, edita `data_source_config.json`:

```json
{
    "symbol_mappings": {
        "YM": {
            "yfinance": "YM=F",
            "ninjatrader": "YM",
            "mt5": "YM"
        }
    }
}
```

### 4. Cómo Funciona con NinjaTrader

#### Flujo de Trading en Vivo

1. **Usuario ejecuta**: `python app.py` → Interfaz Web → Live Trading
2. **Sistema intenta NinjaTrader**:
   ```
   [FETCH] Ticker: MNQ=F, Source: ninjatrader, Mapped: MNQ
   [FETCH SUCCESS] Using NinjaTrader for MNQ=F
   [DATA] Using 1min OHLC from ninjatrader - Got 120 bars
   ```

3. **Si NinjaTrader no está disponible**:
   ```
   [FETCH FALLBACK] ninjatrader failed: No data found
   [FETCH FALLBACK] Trying yfinance as fallback...
   [FETCH SUCCESS] Fallback to yfinance successful
   ```

4. **Análisis FFT**: Siempre usa yfinance (datos históricos profundos)

### 5. Ejecutar Órdenes en NinjaTrader

El sistema puede enviar órdenes automáticamente a NinjaTrader:

```javascript
// Desde el frontend
{
  "symbol": "MNQ",
  "action": "BUY",  // o "SELL"
  "quantity": 1,
  "sl": 21400,      // Stop Loss
  "tp": 21500,      // Take Profit
  "platform": "ninjatrader"
}
```

El backend usa `ninjatrader_connector.py` para comunicarse con NinjaTrader mediante archivos en el directorio de intercambio.

### 6. Verificación

#### Probar Conexión con NinjaTrader

```bash
# Ejecutar desde la raíz del proyecto
python -c "from ninjatrader_connector import NinjaTraderConnector; c = NinjaTraderConnector(); print(c.fetch_data('MNQ', '1min', 10))"
```

**Resultado esperado**: DataFrame con datos de NinjaTrader

#### Probar desde la GUI

1. Ejecuta: `python app.py`
2. Selecciona "Interfaz Web"
3. Ve a Live Trading → MNQ=F
4. Verifica en la UI que muestre: **"🎯 NinjaTrader"** como fuente de datos

### 7. Logs de Debugging

Los logs del backend están en:
- `logs/backend.log` - Salida normal
- `logs/backend_error.log` - Errores

Busca líneas como:
```
[FETCH] Ticker: MNQ=F, Source: ninjatrader, Mapped: MNQ
[FETCH SUCCESS] Using NinjaTrader for MNQ=F
```

### 8. Solución de Problemas

#### Problema: "No data found for ticker MNQ from NinjaTrader"

**Soluciones**:
1. Verifica que NinjaTrader esté corriendo
2. Verifica que el directorio de intercambio sea correcto
3. Verifica que la estrategia de NinjaTrader esté activa
4. El sistema automáticamente usará yfinance como fallback

#### Problema: "NinjaTrader exchange directory not found"

**Solución**:
```json
{
    "ninja_exchange_dir": "C:\\RUTA_CORRECTA\\Exchange"
}
```

#### Problema: Símbolos no se mapean correctamente

**Solución**: Agrega el mapeo en `data_source_config.json`:
```json
{
    "symbol_mappings": {
        "TU_SIMBOLO": {
            "ninjatrader": "SIMBOLO_EN_NINJA",
            "yfinance": "SIMBOLO=F",
            "mt5": "SIMBOLO_MT5"
        }
    }
}
```

### 9. Sincronización Automática

Cualquier cambio en `data_source_config.json` se sincroniza automáticamente entre:
- Raíz del proyecto
- Frontend

No necesitas copiar manualmente el archivo.

### 10. Cambiar entre MT5 y NinjaTrader

**Opción 1: Editar JSON**
```json
{
    "realtime_source": "ninjatrader"  // o "mt5"
}
```

**Opción 2: Desde el Backend API**

El frontend puede cambiar la fuente mediante el endpoint:
```
POST /api/config/datasource
{
    "type": "realtime",
    "source": "ninjatrader"
}
```

**Opción 3: Script Python**
```python
from data_source_config import DataSourceConfig
config = DataSourceConfig()
config.set_realtime_source('ninjatrader')
print("✅ Cambiado a NinjaTrader")
```

## Resumen

✅ **NinjaTrader funciona perfectamente** con el mismo sistema de fallback automático que MT5

✅ **Cambiar entre MT5 y NinjaTrader** es tan simple como editar una línea en el JSON

✅ **Fallback automático** a yfinance si NinjaTrader no está disponible

✅ **Sincronización automática** de configuración entre raíz y frontend

✅ **Sin terminales visibles** - Todo funciona en segundo plano

✅ **Logs detallados** para debugging en `logs/`
