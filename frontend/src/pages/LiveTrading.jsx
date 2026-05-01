import React, { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { Card } from '../components/common/Card'
import { Button } from '../components/common/Button'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { TrendingUp, TrendingDown, Zap, DollarSign, Activity, PlayCircle, StopCircle, AlertCircle } from 'lucide-react'
import { createChart } from 'lightweight-charts'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'
const WS_BASE_URL = API_BASE_URL.replace('http', 'ws')

export function LiveTrading() {
  const { symbol } = useParams()
  const [liveData, setLiveData] = useState(null)
  const [signals, setSignals] = useState([])
  const [autoTrading, setAutoTrading] = useState(false)
  const [tradingPlatform, setTradingPlatform] = useState('mt5')
  const [isConnected, setIsConnected] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [priceHistory, setPriceHistory] = useState([])
  
  const wsRef = useRef(null)
  const chartContainerRef = useRef(null)
  const chartRef = useRef(null)
  const candleSeriesRef = useRef(null)

  useEffect(() => {
    // Conectar WebSocket
    connectWebSocket()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (chartRef.current) {
        chartRef.current.remove()
        chartRef.current = null
      }
    }
  }, [symbol])

  // Efecto separado para inicializar el gráfico cuando el ref esté disponible
  useEffect(() => {
    if (isConnected && chartContainerRef.current && !chartRef.current) {
      console.log('📊 Inicializando gráfico...')
      const timer = setTimeout(() => {
        createLiveChart()
      }, 300)
      
      return () => clearTimeout(timer)
    }
  }, [isConnected, symbol])

  const createLiveChart = () => {
    if (!chartContainerRef.current) {
      console.error('❌ chartContainerRef no está disponible')
      return
    }

    try {
      console.log('📊 Creando gráfico lightweight-charts...')
      
      const chart = createChart(chartContainerRef.current, {
        width: chartContainerRef.current.clientWidth,
        height: chartContainerRef.current.clientHeight,
        layout: {
          background: { color: '#0f1419' },
          textColor: '#d1d5db',
        },
        grid: {
          vertLines: { color: '#1f2937' },
          horzLines: { color: '#1f2937' },
        },
        crosshair: {
          mode: 1,
        },
        timeScale: {
          borderColor: '#4b5563',
          timeVisible: true,
          secondsVisible: false,
        },
        rightPriceScale: {
          borderColor: '#4b5563',
        },
      })

      const candleSeries = chart.addCandlestickSeries({
        upColor: '#22c55e',
        downColor: '#ef4444',
        borderUpColor: '#22c55e',
        borderDownColor: '#ef4444',
        wickUpColor: '#22c55e',
        wickDownColor: '#ef4444',
      })

      chartRef.current = chart
      candleSeriesRef.current = candleSeries

      console.log('✅ Gráfico creado exitosamente')

      // Responsive
      const handleResize = () => {
        if (chartContainerRef.current && chartRef.current) {
          chartRef.current.applyOptions({
            width: chartContainerRef.current.clientWidth,
          })
        }
      }

      window.addEventListener('resize', handleResize)

      return () => window.removeEventListener('resize', handleResize)
    } catch (error) {
      console.error('❌ Error al crear gráfico:', error)
    }
  }

  const updateChart = (price, timestamp) => {
    if (!candleSeriesRef.current) {
      console.warn('[CHART] candleSeriesRef not available')
      return
    }

    try {
      const time = Math.floor(timestamp / 1000)
      const currentMinute = Math.floor(time / 60) * 60
      
      console.log(`[CHART UPDATE] Price: ${price}, Timestamp: ${time}, Current minute: ${currentMinute}`)
      
      // Obtener última vela del estado
      setPriceHistory(prev => {
        const lastCandle = prev[prev.length - 1]
        
        console.log(`[CHART] Last candle:`, lastCandle)
        console.log(`[CHART] Comparing times - Last: ${lastCandle?.time}, Current: ${currentMinute}`)

        if (!lastCandle || lastCandle.time !== currentMinute) {
          // Nueva vela
          const newCandle = {
            time: currentMinute,
            open: price,
            high: price,
            low: price,
            close: price,
          }
          console.log('[CHART] Creating new candle:', newCandle)
          candleSeriesRef.current.update(newCandle)
          return [...prev.slice(-200), newCandle]
        } else {
          // Actualizar vela actual
          const updatedCandle = {
            ...lastCandle,
            high: Math.max(lastCandle.high, price),
            low: Math.min(lastCandle.low, price),
            close: price,
          }
          console.log('[CHART] Updating existing candle:', updatedCandle)
          candleSeriesRef.current.update(updatedCandle)
          return [...prev.slice(0, -1), updatedCandle]
        }
      })
    } catch (error) {
      console.error('[CHART ERROR]', error)
    }
  }

  const drawOrderLines = (signal) => {
    // Según la especificación del proyecto, el gráfico NO debe mostrar
    // las líneas de Entry/TP/SL cuando se envían órdenes
    // Los datos están disponibles en el panel de señales activas
    return
  }

  const connectWebSocket = () => {
    const ws = new WebSocket(`${WS_BASE_URL}/ws/live/${symbol}`)

    ws.onopen = () => {
      setIsConnected(true)
      showMessage('success', 'Conectado al stream en tiempo real')
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      console.log('📡 Mensaje WebSocket recibido:', {
        hasPrice: !!data.price,
        price: data.price,
        hasHistoricalData: !!data.historical_data,
        historicalLength: data.historical_data?.length,
        trend: data.trend,
        confidence: data.confidence
      })
      
      setLiveData(data)

      // Si hay datos históricos en el primer mensaje, cargarlos
      if (data.historical_data && data.historical_data.length > 0) {
        console.log('[WS] Historical data received:', data.historical_data.length, 'candles')
        console.log('[WS] First candle:', data.historical_data[0])
        console.log('[WS] Last candle:', data.historical_data[data.historical_data.length - 1])
        
        if (candleSeriesRef.current) {
          // Verificar si ya se cargaron datos históricos comparando longitudes
          setPriceHistory(prev => {
            if (prev.length === 0 || prev.length < data.historical_data.length) {
              try {
                console.log('[WS] Loading historical data into chart')
                candleSeriesRef.current.setData(data.historical_data)
                console.log('[WS] Historical data loaded successfully')
                return data.historical_data
              } catch (error) {
                console.error('[WS ERROR] Failed to load historical data:', error)
                return prev
              }
            }
            return prev
          })
        } else {
          console.warn('[WS] candleSeriesRef not available yet')
        }
      }

      // Actualizar gráfico con precio en tiempo real
      if (data.price && data.timestamp) {
        console.log('[WS] Calling updateChart with price:', data.price, 'timestamp:', data.timestamp)
        updateChart(data.price, data.timestamp * 1000)
      } else {
        console.warn('[WS] Missing price or timestamp in data')
      }

      // Si hay nueva señal, agregarla
      if (data.new_signal && data.signal) {
        setSignals(prev => [data.signal, ...prev].slice(0, 10))
        showMessage('info', `Nueva señal ${data.signal.direction} detectada`)

        // Si auto-trading está activo, ejecutar orden
        if (autoTrading) {
          executeSignal(data.signal)
        }
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      showMessage('error', 'Error en la conexión')
    }

    ws.onclose = () => {
      setIsConnected(false)
      showMessage('warning', 'Desconectado. Reconectando...')
      
      // Reconectar después de 5 segundos
      setTimeout(connectWebSocket, 5000)
    }

    wsRef.current = ws
  }

  const showMessage = (type, text) => {
    setMessage({ type, text })
    setTimeout(() => setMessage({ type: '', text: '' }), 5000)
  }

  const executeSignal = async (signal) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/live/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: signal.symbol,
          action: signal.direction,
          quantity: 1,
          sl: signal.stop_loss,
          tp: signal.take_profit,
          platform: tradingPlatform
        })
      })

      const result = await response.json()

      if (result.status === 'success') {
        showMessage('success', `Orden ${signal.direction} ejecutada en ${tradingPlatform}`)
      } else {
        showMessage('error', `Error al ejecutar orden: ${result.error || 'Desconocido'}`)
      }
    } catch (error) {
      showMessage('error', `Error de conexión: ${error.message}`)
    }
  }

  const toggleAutoTrading = () => {
    setAutoTrading(!autoTrading)
    showMessage('info', `Auto-trading ${!autoTrading ? 'ACTIVADO' : 'DESACTIVADO'}`)
  }

  if (!isConnected) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" />
        <p className="ml-4">Conectando al stream en tiempo real...</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Activity size={28} className="text-accent-gold" />
            Trading en Vivo - {symbol}
          </h1>
          <p className="text-sm text-text-secondary">Scalping Intradía con Señales FFT en Tiempo Real</p>
        </div>

        <div className="flex gap-3 items-center">
          {/* Status Indicator */}
          <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
            isConnected ? 'bg-green-500/20 border border-green-500/30' : 'bg-red-500/20 border border-red-500/30'
          }`}>
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
            <span className={`text-xs font-medium ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
              {isConnected ? 'EN VIVO' : 'DESCONECTADO'}
            </span>
          </div>

          {/* Auto-Trading Toggle */}
          <button
            onClick={toggleAutoTrading}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
              autoTrading 
                ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-500/50' 
                : 'bg-green-500 hover:bg-green-600 text-white'
            }`}
          >
            {autoTrading ? <StopCircle size={18} /> : <PlayCircle size={18} />}
            {autoTrading ? 'DETENER AUTO-TRADING' : 'ACTIVAR AUTO-TRADING'}
          </button>

          {/* Platform Selector */}
          <select
            value={tradingPlatform}
            onChange={(e) => setTradingPlatform(e.target.value)}
            className="bg-primary-bg border border-accent-gold/30 rounded-lg px-4 py-2.5 text-sm text-white font-semibold min-w-[180px] cursor-pointer hover:border-accent-gold transition-colors shadow-lg"
            style={{ color: '#ffffff', backgroundColor: '#1a1f2e' }}
          >
            <option value="ninjatrader" style={{ color: '#ffffff', backgroundColor: '#1a1f2e' }}>
              🎯 NinjaTrader
            </option>
            <option value="mt5" style={{ color: '#ffffff', backgroundColor: '#1a1f2e' }}>
              📊 MetaTrader 5
            </option>
          </select>
        </div>
      </div>

      {/* Message Banner */}
      {message.text && (
        <div className={`p-3 rounded-lg text-sm ${
          message.type === 'success' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
          message.type === 'error' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
          message.type === 'warning' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
          'bg-blue-500/20 text-blue-400 border border-blue-500/30'
        }`}>
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Live Chart */}
        <div className="lg:col-span-2">
          <Card className="p-0 overflow-hidden" style={{ height: '650px' }}>
            <div 
              ref={chartContainerRef} 
              style={{ 
                width: '100%', 
                height: '100%',
                position: 'relative',
                backgroundColor: '#0f1419'
              }} 
            />
          </Card>
        </div>

        {/* Live Data & Signals */}
        <div className="space-y-4">
          {/* Current Market Data */}
          <Card className="p-4">
            <h3 className="text-sm font-bold mb-3 flex items-center gap-2">
              <DollarSign size={16} className="text-accent-gold" />
              Datos en Tiempo Real
            </h3>
            
            {liveData && liveData.data_source === 'yfinance' && (
              <div className="p-3 mb-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-[10px] text-yellow-500 flex items-start gap-2">
                <AlertCircle size={14} className="shrink-0 mt-0.5" />
                <p>
                  <span className="font-bold block mb-0.5">Modo Análisis (yfinance)</span>
                  Los datos de yfinance tienen retraso y son limitados para trading en vivo. Se recomienda MT5 o NinjaTrader.
                </p>
              </div>
            )}

            {liveData && liveData.error && (
              <div className="p-3 mb-3 bg-red-500/20 border border-red-500/50 rounded-lg text-xs text-red-400">
                <p className="font-bold mb-1">Error de Datos:</p>
                {liveData.error}
              </div>
            )}

            {liveData && !liveData.error && (
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-text-secondary">Fuente</span>
                  <span className={`text-xs font-bold uppercase ${
                    liveData.data_source === 'yfinance' ? 'text-yellow-500' : 'text-green-400'
                  }`}>
                    {liveData.data_source}
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-xs text-text-secondary">Precio</span>
                  <span className="text-lg font-mono font-bold text-white">
                    ${liveData.price?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-xs text-text-secondary">Tendencia</span>
                  <div className={`flex items-center gap-1 font-medium ${
                    liveData.trend === 'UP' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {liveData.trend === 'UP' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                    {liveData.trend}
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-xs text-text-secondary">Fuerza</span>
                  <span className="font-mono text-sm">{liveData.trend_strength?.toFixed(2)}</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-xs text-text-secondary">Confianza</span>
                  <span className="font-mono text-sm text-accent-gold">
                    {(liveData.confidence * 100).toFixed(1)}%
                  </span>
                </div>

                {liveData.dominant_cycle && (
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-text-secondary">Ciclo Dominante</span>
                    <span className="font-mono text-sm">{liveData.dominant_cycle.period?.toFixed(1)}d</span>
                  </div>
                )}
              </div>
            )}
          </Card>

          {/* Active Signals */}
          <Card className="p-4 max-h-[500px] overflow-y-auto">
            <h3 className="text-sm font-bold mb-3 flex items-center gap-2">
              <Zap size={16} className="text-yellow-400" />
              Señales Activas ({signals.length})
            </h3>

            <div className="space-y-2">
              {signals.length === 0 ? (
                <p className="text-xs text-text-secondary text-center py-4">
                  Esperando señales de scalping...
                </p>
              ) : (
                signals.map((signal, idx) => (
                  <SignalCard 
                    key={idx} 
                    signal={signal} 
                    onExecute={() => executeSignal(signal)}
                    autoTrading={autoTrading}
                  />
                ))
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}

function SignalCard({ signal, onExecute, autoTrading }) {
  const riskReward = signal.risk_reward?.toFixed(2) || 'N/A'
  const isLong = signal.direction === 'BUY'

  return (
    <div className={`p-3 rounded-lg border ${
      isLong ? 'bg-green-500/10 border-green-500/30' : 'bg-red-500/10 border-red-500/30'
    }`}>
      <div className="flex justify-between items-start mb-2">
        <div className="flex items-center gap-2">
          {isLong ? <TrendingUp size={16} className="text-green-400" /> : <TrendingDown size={16} className="text-red-400" />}
          <span className={`font-bold text-sm ${isLong ? 'text-green-400' : 'text-red-400'}`}>
            {signal.direction}
          </span>
        </div>
        <span className="text-[10px] text-text-secondary">
          {new Date(signal.timestamp).toLocaleTimeString('es-ES')}
        </span>
      </div>

      <div className="space-y-1 text-xs">
        <div className="flex justify-between">
          <span className="text-text-secondary">Entrada:</span>
          <span className="font-mono">${signal.entry_price?.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-secondary">TP:</span>
          <span className="font-mono text-green-400">${signal.take_profit?.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-secondary">SL:</span>
          <span className="font-mono text-red-400">${signal.stop_loss?.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-secondary">R:R:</span>
          <span className="font-mono text-accent-gold">{riskReward}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-text-secondary">Confianza:</span>
          <span className="font-mono">{(signal.confidence * 100).toFixed(1)}%</span>
        </div>
      </div>

      <p className="text-[10px] text-text-secondary mt-2 italic">{signal.reason}</p>

      {!autoTrading && (
        <Button 
          onClick={onExecute}
          className="w-full mt-2 text-xs py-1"
          variant={isLong ? 'primary' : 'secondary'}
        >
          Ejecutar Manualmente
        </Button>
      )}
    </div>
  )
}
