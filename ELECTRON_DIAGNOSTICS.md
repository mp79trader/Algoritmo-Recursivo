# Diagnóstico de Electron - Trading en Vivo

## Problema Reportado
El Trading en Vivo **carga pero no muestra datos** en modo Electron.

## Cambios Aplicados

### 1. Actualización de `frontend/electron/main.cjs`
**Archivo**: `frontend/electron/main.cjs` (líneas 37-58)

**Cambio**: Modificado el inicio del backend Python para mostrar logs en desarrollo:

```javascript
// ANTES:
pythonProcess = spawn(pythonExe, [backendPath], {
  windowsHide: true,
  stdio: 'ignore' // Ocultaba todos los logs
});

// AHORA:
const stdioMode = isDev ? 'inherit' : 'pipe';
pythonProcess = spawn(pythonExe, [backendPath], {
  windowsHide: !isDev,
  stdio: stdioMode
});

if (!isDev) {
  pythonProcess.stderr.on('data', (data) => {
    console.error(`Backend Error: ${data.toString()}`);
  });
  
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data.toString()}`);
  });
}
```

**Beneficio**: Ahora se pueden ver los logs del backend Python en la terminal al ejecutar `npm run electron:dev`.

## Pasos de Verificación (Usuario debe ejecutar)

### 1. Iniciar Electron en Modo Desarrollo

```bash
cd frontend
npm run electron:dev
```

### 2. Verificar Logs del Backend

**Logs Esperados (Backend funcionando correctamente):**
```
Starting backend from: D:\Betas\Algoritmo Recursivo\backend\main.py
Connected to MetaTrader 5
MT5 version: (500, 5430, '14 Nov 2025')
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

**Síntomas de Problema:**
- ❌ No aparece "Starting backend from..."
  - **Causa**: Python no se encuentra o path incorrecto
  - **Solución**: Verificar que `.venv/Scripts/python.exe` existe
  
- ❌ Aparece "Failed to start backend: [error]"
  - **Causa**: Dependencias faltantes o error en backend
  - **Solución**: Ejecutar `pip install -r requirements.txt` en `.venv`
  
- ❌ Aparece "Address already in use" o "port 8001"
  - **Causa**: Puerto 8001 ocupado
  - **Solución**: Cerrar proceso usando puerto 8001 o cambiar puerto

### 3. Verificar WebSocket en DevTools

1. Una vez que Electron abra, presiona **F12** para abrir DevTools
2. Ve a la pestaña **Console**
3. Navega a **Trading en Vivo** → **MNQ=F**
4. Busca mensajes de WebSocket:

**Logs Esperados (WebSocket funcionando):**
```
📡 Mensaje WebSocket recibido: {hasPrice: true, price: 25418.75, ...}
[WS] Historical data received: 100 candles
[WS] Loading historical data into chart
```

**Síntomas de Problema:**
- ❌ `WebSocket connection failed`
  - **Causa**: Backend no está corriendo
  - **Solución**: Verificar logs del backend en Paso 2
  
- ❌ `Error: connect ECONNREFUSED 127.0.0.1:8001`
  - **Causa**: Backend no escucha en puerto 8001
  - **Solución**: Verificar que backend inició correctamente

### 4. Verificar Network en DevTools

1. En DevTools, ve a pestaña **Network**
2. Filtra por **WS** (WebSocket)
3. Busca conexión a `ws://localhost:8001/ws/live/MNQ%3DF`

**Estados Esperados:**
- ✅ **Status: 101 Switching Protocols** (conexión exitosa)
- ✅ **Messages**: Debe mostrar mensajes entrantes con datos

**Estados de Error:**
- ❌ **Status: Failed** (backend no responde)
- ❌ **Status: 404** (endpoint no existe)

## Correcciones Adicionales Aplicadas

### 1. Backend - Más datos históricos
**Archivo**: `backend/main.py` (línea 425)

Cambiado de:
```python
data = market_data.fetch_data(period='1d', interval='1min')  # Solo 1 barra
```

A:
```python
data = market_data.fetch_data(period='2h', interval='1min')  # 120 barras
```

### 2. Backend - Mapping de períodos corregido
**Archivo**: `market_data.py` (líneas 96-100)

Agregado soporte para períodos en horas:
```python
period_map = {
    '1h': 60, '2h': 120, '4h': 240, '1d': 390,
    '5d': 1950, '1mo': 11700, '3mo': 35100,
    '6mo': 70200, '1y': 252, '2y': 504, '5y': 1260
}
```

### 3. Backend - Logs detallados de WebSocket
**Archivo**: `backend/main.py` (líneas 394-420)

Agregados logs de diagnóstico:
```python
print(f"\n{'='*60}")
print(f"[WS CONNECT] Nueva conexion WebSocket iniciada")
print(f"[WS CONNECT] Symbol recibido: {symbol}")
print(f"{'='*60}\n")
```

## Problemas Conocidos y Soluciones

### Problema 1: Solo se muestra 1 vela en el gráfico
**Causa**: El backend solo enviaba 1 vela histórica en lugar de 100
**Solución**: ✅ Corregido en `backend/main.py` y `market_data.py`

### Problema 2: RuntimeWarning en normalización
**Síntoma**: `RuntimeWarning: invalid value encountered in divide`
**Causa**: MT5 devuelve solo 1 barra y `std()` es cero
**Solución**: ✅ Corregido solicitando 120 barras en lugar de 1

### Problema 3: Trading en Vivo funciona en navegador pero no en Electron
**Causa Posible**: Backend no inicia en Electron o usa puerto diferente
**Diagnóstico**: Ejecutar pasos de verificación arriba
**Solución Temporal**: Iniciar backend manualmente antes de abrir Electron:
```bash
# Terminal 1:
cd backend
python main.py

# Terminal 2:
cd frontend
npm run electron:dev
```

## Configuración de Red

### Variables de Entorno
**Archivo**: `frontend/.env`
```
VITE_API_URL=http://localhost:8001
```

### WebSocket URL
**Archivo**: `frontend/src/pages/LiveTrading.jsx` (línea 10)
```javascript
const WS_BASE_URL = API_BASE_URL.replace('http', 'ws')
// Resultado: ws://localhost:8001
```

### Backend Listen Address
**Archivo**: `backend/main.py` (línea 660 aproximadamente)
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

## Próximos Pasos

1. **Usuario debe ejecutar**: `cd frontend && npm run electron:dev`
2. **Usuario debe capturar**: Logs de la terminal donde se ejecutó el comando
3. **Usuario debe verificar**: DevTools Console y Network (F12 en Electron)
4. **Usuario debe reportar**: Cualquier error o mensaje anormal

## Contacto para Soporte

Si después de seguir estos pasos el problema persiste:
1. Capturar **screenshot de Electron** mostrando Trading en Vivo
2. Capturar **logs completos de la terminal**
3. Capturar **DevTools Console** (F12 → Console tab)
4. Capturar **DevTools Network** (F12 → Network → WS filter)

---

**Última actualización**: 2026-01-19
**Versión**: 1.0.0
