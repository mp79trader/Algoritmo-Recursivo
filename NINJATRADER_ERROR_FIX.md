# Solución: Error de NinjaTrader - Archivo de Datos No Encontrado

## Problema

```
Error fetching data for MNQ=F: NinjaTrader data file not found: 
C:\QuantumGAN\Exchange\data_MNQ_1min.csv
```

## Causas Posibles

1. **La estrategia de NinjaTrader no está corriendo**
2. **El directorio de intercambio es incorrecto**
3. **El símbolo no está mapeado correctamente**
4. **La estrategia no está generando los archivos CSV**

## Soluciones

### 1. Verificar que la Estrategia de NinjaTrader Esté Corriendo

La estrategia `SystemAILearning.cs` debe estar:
- ✅ Compilada sin errores
- ✅ Aplicada a un gráfico
- ✅ Habilitada (botón "Enabled")
- ✅ Configurada con el símbolo correcto (MNQ MAR26)

### 2. Verificar el Directorio de Intercambio

**Paso 1**: Verifica que el directorio existe:
```
C:\QuantumGAN\Exchange
```

Si no existe, créalo o actualiza la configuración:

**Edita `data_source_config.json`**:
```json
{
    "ninja_exchange_dir": "C:\\TU_DIRECTORIO\\Exchange"
}
```

**Paso 2**: Verifica que la estrategia de NinjaTrader use el mismo directorio:

En `SystemAILearning.cs`, busca:
```csharp
private string exchangeDir = @"C:\QuantumGAN\Exchange";
```

Debe coincidir con `data_source_config.json`.

### 3. Verificar el Mapeo de Símbolos

El símbolo en la GUI es `MNQ=F`, pero NinjaTrader usa `MNQ MAR26`.

**Actualiza el mapeo en `data_source_config.json`**:

```json
{
    "symbol_mappings": {
        "MNQ": {
            "yfinance": "MNQ=F",
            "ninjatrader": "MNQ MAR26",  // ← Cambiar aquí
            "mt5": "MNQH26"
        }
    }
}
```

**IMPORTANTE**: Después de cambiar, ejecuta:
```bash
python sync_config.py
```

### 4. Verificar que la Estrategia Genere los Archivos

La estrategia de NinjaTrader debe generar archivos como:
```
C:\QuantumGAN\Exchange\data_MNQ MAR26_1min.csv
```

**Nota**: El nombre del archivo usa el símbolo de NinjaTrader, no el interno.

Si el archivo no existe:
1. Verifica que la estrategia esté corriendo
2. Espera unos segundos para que se genere el primer archivo
3. Verifica los logs de NinjaTrader

### 5. Solución Temporal: Usar yfinance Directamente

Mientras configuras NinjaTrader, puedes usar yfinance:

**Edita `data_source_config.json`**:
```json
{
    "realtime_source": "yfinance"
}
```

Ejecuta:
```bash
python sync_config.py
```

Ahora el sistema usará yfinance directamente (datos de 5 minutos).

### 6. Verificación Paso a Paso

#### Paso 1: Verificar Directorio
```bash
# En PowerShell
Test-Path "C:\QuantumGAN\Exchange"
# Debe retornar: True
```

#### Paso 2: Verificar Archivos
```bash
# Listar archivos en el directorio
Get-ChildItem "C:\QuantumGAN\Exchange"
```

Deberías ver archivos como:
- `data_MNQ MAR26_1min.csv`
- `data_MES MAR26_1min.csv`

#### Paso 3: Verificar Contenido del Archivo
```bash
# Ver primeras líneas
Get-Content "C:\QuantumGAN\Exchange\data_MNQ MAR26_1min.csv" -Head 5
```

Debe tener formato:
```
Time,Open,High,Low,Close,Volume
2026-01-19 10:00:00,21450.50,21455.25,21448.00,21452.75,1234
```

### 7. Configuración Correcta para NinjaTrader

**`data_source_config.json`** (raíz):
```json
{
    "realtime_source": "ninjatrader",
    "historical_source": "yfinance",
    "ninja_exchange_dir": "C:\\QuantumGAN\\Exchange",
    "symbol_mappings": {
        "MNQ": {
            "yfinance": "MNQ=F",
            "ninjatrader": "MNQ MAR26",
            "mt5": "MNQH26"
        },
        "MES": {
            "yfinance": "MES=F",
            "ninjatrader": "MES MAR26",
            "mt5": "ES-MAR26"
        }
    }
}
```

**Sincronizar**:
```bash
python sync_config.py
```

### 8. Fallback Automático Mejorado

He mejorado el fallback para que cuando NinjaTrader falle:
1. Intenta yfinance con intervalo compatible (5min en lugar de 1min)
2. Obtiene datos del último día
3. Continúa funcionando sin errores

**Logs esperados**:
```
[FETCH] Ticker: MNQ=F, Source: ninjatrader, Mapped: MNQ MAR26
[FETCH FALLBACK] ninjatrader failed: NinjaTrader data file not found
[FETCH FALLBACK] Trying yfinance as fallback...
[FETCH FALLBACK] yfinance no soporta 1min, usando 5min
[FETCH FALLBACK] Fetching MNQ=F with interval=5m, period=1d
[FETCH SUCCESS] Fallback to yfinance successful for MNQ=F (78 bars)
```

### 9. Checklist de Verificación

- [ ] Directorio `C:\QuantumGAN\Exchange` existe
- [ ] Estrategia `SystemAILearning.cs` compilada
- [ ] Estrategia aplicada a gráfico de NinjaTrader
- [ ] Estrategia habilitada (Enabled)
- [ ] Símbolo correcto en NinjaTrader (MNQ MAR26)
- [ ] Archivos CSV se están generando en el directorio
- [ ] `data_source_config.json` tiene el mapeo correcto
- [ ] Ejecutado `python sync_config.py`
- [ ] Reiniciado la aplicación Electron

### 10. Si Nada Funciona

**Opción 1**: Usar yfinance temporalmente
```json
{"realtime_source": "yfinance"}
```

**Opción 2**: Verificar logs
```
logs/backend.log
logs/backend_error.log
```

**Opción 3**: Probar manualmente
```python
from ninjatrader_connector import NinjaTraderConnector
c = NinjaTraderConnector()
data = c.fetch_data('MNQ MAR26', '1min', 10)
print(data)
```

## Resumen

✅ **Fallback mejorado**: Ahora usa intervalos compatibles con yfinance (5min)

✅ **Mapeo correcto**: Actualiza el símbolo a `"MNQ MAR26"` en la configuración

✅ **Sincronización**: Ejecuta `python sync_config.py` después de cambios

✅ **Verificación**: Asegúrate que la estrategia de NinjaTrader esté corriendo y generando archivos

🎯 **Próximo paso**: Actualiza el mapeo del símbolo y sincroniza la configuración
