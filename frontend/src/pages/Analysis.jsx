import React, { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import Plot from 'react-plotly.js'
import { marketAPI, analysisAPI } from '../services/api'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { Card } from '../components/common/Card'
import { AlertCircle, TrendingUp, Activity, BarChart2, Calendar, DollarSign, Clock, Zap } from 'lucide-react'

// Helper to classify trading strategy
function classifySignal(trend, dominantCycle, period) {
  const cyclePeriod = dominantCycle ? dominantCycle.period : 0
  const isUp = trend.direction === 'UP'
  
  let strategy = 'N/A'
  let timeframe = 'N/A'
  let description = ''

  // Classification logic
  if (cyclePeriod > 0 && cyclePeriod <= 3) {
    strategy = 'SCALPING / CORTO PLAZO'
    timeframe = 'Intradía - 3 Días'
    description = 'Ciclos de muy alta frecuencia detectados. Operativa rápida aprovechando volatilidad.'
  } else if (cyclePeriod > 3 && cyclePeriod <= 10) {
    strategy = 'SWING TRADING (CORTO)'
    timeframe = '3 - 10 Días'
    description = 'Ciclos de corto plazo ideales para capturar movimientos semanales.'
  } else if (cyclePeriod > 10 && cyclePeriod <= 30) {
    strategy = 'SWING TRADING (MEDIO)'
    timeframe = '2 - 4 Semanas'
    description = 'Tendencias sostenidas de medio plazo. Buena relación riesgo/beneficio.'
  } else {
    strategy = 'POSITION TRADING'
    timeframe = '> 1 Mes'
    description = 'Ciclos de largo plazo dominantes. Operativa de seguimiento de tendencia mayor.'
  }

  return { strategy, timeframe, description, isUp }
}

export function Analysis() {
  const { symbol } = useParams()
  const [selectedPeriod, setSelectedPeriod] = useState('2y')
  const [selectedInterval, setSelectedInterval] = useState('1d')

  const { data: analysisData, isLoading, error } = useQuery({
    queryKey: ['analysis', symbol, selectedPeriod, selectedInterval],
    queryFn: async () => {
      await marketAPI.getMarketData(symbol, selectedPeriod, selectedInterval)
      return analysisAPI.executeAnalysis({
        symbol,
        prediction_days: 60,
        fft_components: 48
      })
    },
    retry: 1
  })

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" />
        <p className="mt-4 text-text-secondary animate-pulse">
          Analizando mercado, ciclos y tendencias...
        </p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
        <div className="bg-red-500/10 p-4 rounded-full mb-4">
          <AlertCircle size={48} className="text-red-500" />
        </div>
        <h2 className="text-2xl font-bold mb-2">Error en el Análisis</h2>
        <p className="text-text-secondary max-w-md">
          {error.response?.data?.error || error.message || 'No se pudo completar el análisis.'}
        </p>
        <button onClick={() => window.location.reload()} className="mt-6 btn-gold">
          Intentar Nuevamente
        </button>
      </div>
    )
  }

  // Check if data exists and has analysis property
  if (!analysisData || !analysisData.analysis) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
        <div className="bg-yellow-500/10 p-4 rounded-full mb-4">
          <AlertCircle size={48} className="text-yellow-500" />
        </div>
        <h2 className="text-2xl font-bold mb-2">Datos no disponibles</h2>
        <p className="text-text-secondary max-w-md">
          No se recibieron datos de análisis válidos del servidor.
        </p>
      </div>
    )
  }

  const { analysis } = analysisData
  const { symbol_info, prediction, trend, cycles, spectral, historical } = analysis
  
  // Prepare Data for Classification
  const signalInfo = classifySignal(trend, cycles.dominant, selectedPeriod)
  
  // Prepare Data for Charts
  const historicalY = historical?.prices || spectral.reconstructed
  const historicalX = Array.from({length: historicalY.length}, (_, i) => i)
  
  const predictionY = prediction.predictions
  const predictionX = Array.from({length: predictionY.length}, (_, i) => i + historicalY.length)
  
  const trendY = trend.trend

  return (
    <div className="space-y-4 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            {symbol_info.name}
            <span className="text-xs px-2 py-0.5 rounded-full bg-accent-gold/20 text-accent-gold border border-accent-gold/30">
              {symbol_info.ticker}
            </span>
          </h1>
          <p className="text-text-secondary text-sm mt-0.5">
            {signalInfo.strategy} | {signalInfo.timeframe}
          </p>
        </div>

        <div className="flex gap-1">
          {['1y', '2y', '5y'].map((p) => (
            <button
              key={p}
              onClick={() => setSelectedPeriod(p)}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                selectedPeriod === p
                  ? 'bg-accent-gold text-primary-bg'
                  : 'bg-secondary-bg hover:bg-white/5'
              }`}
            >
              {p.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Signal Card - The "Big Insight" */}
      <Card className="p-4 bg-gradient-to-r from-primary-bg to-secondary-bg/50 border-accent-gold/30">
        <div className="flex flex-col md:flex-row gap-6 items-center">
          <div className="flex-1 text-center md:text-left">
            <h2 className="text-text-secondary uppercase tracking-wider text-xs font-semibold mb-1">Señal Detectada</h2>
            <div className={`text-3xl font-bold mb-1 ${signalInfo.isUp ? 'text-green-400' : 'text-red-500'}`}>
              {signalInfo.isUp ? 'LONG / COMPRA' : 'SHORT / VENTA'}
            </div>
            <p className="text-sm text-white/80 max-w-xl leading-snug">
              {signalInfo.description}
            </p>
          </div>
          
          <div className="flex-1 w-full md:max-w-xs">
             <div className="flex justify-between text-xs mb-1">
                <span className="text-text-secondary">Confianza del Modelo</span>
                <span className="font-bold text-accent-gold">{(prediction.confidence * 100).toFixed(1)}%</span>
             </div>
             <div className="w-full bg-black/30 rounded-full h-2 mb-3">
                <div 
                  className={`h-full rounded-full transition-all duration-1000 ${
                    prediction.confidence > 0.7 ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]' : 
                    prediction.confidence > 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${prediction.confidence * 100}%` }}
                />
             </div>
             <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="bg-white/5 p-2 rounded">
                    <span className="block text-text-secondary text-[10px]">Fuerza Tendencia</span>
                    <span className="font-bold">{trend.strength.toFixed(2)}</span>
                </div>
                <div className="bg-white/5 p-2 rounded">
                    <span className="block text-text-secondary text-[10px]">Ciclo Dominante</span>
                    <span className="font-bold">{cycles.dominant ? cycles.dominant.period.toFixed(1) : '-'}d</span>
                </div>
             </div>
          </div>
        </div>
      </Card>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left Column: Price & Trend */}
        <div className="lg:col-span-2 space-y-4">
            <Card className="p-3 min-h-[350px]">
                <h3 className="text-base font-semibold mb-2 flex items-center gap-2">
                    <TrendingUp size={16} className="text-accent-gold"/>
                    Predicción y Tendencia
                </h3>
                <div className="w-full h-[300px]">
                    <Plot
                        data={[
                            {
                                y: historicalY,
                                x: historicalX,
                                type: 'scatter',
                                mode: 'lines',
                                name: 'Precio',
                                line: { color: '#3B82F6', width: 1.5 }
                            },
                            {
                                y: trendY,
                                x: historicalX,
                                type: 'scatter',
                                mode: 'lines',
                                name: 'Tendencia',
                                line: { color: signalInfo.isUp ? '#22C55E' : '#EF4444', width: 2, dash: 'solid' }
                            },
                            {
                                y: predictionY,
                                x: predictionX,
                                type: 'scatter',
                                mode: 'lines',
                                name: 'Proyección',
                                line: { color: '#EAB308', width: 2, dash: 'dot' }
                            }
                        ]}
                        layout={{
                            autosize: true,
                            paper_bgcolor: 'rgba(0,0,0,0)',
                            plot_bgcolor: 'rgba(0,0,0,0)',
                            font: { color: '#9CA3AF', size: 10 },
                            showlegend: true,
                            legend: { orientation: 'h', y: 1.1 },
                            xaxis: { 
                                title: 'Periodo (Días)',
                                gridcolor: 'rgba(255,255,255,0.05)' 
                            },
                            yaxis: { 
                                title: 'Precio',
                                gridcolor: 'rgba(255,255,255,0.05)'
                            },
                            margin: { l: 40, r: 10, t: 10, b: 30 }
                        }}
                        useResizeHandler={true}
                        style={{ width: '100%', height: '100%' }}
                        config={{ displayModeBar: false }}
                    />
                </div>
            </Card>

            <Card className="p-3 min-h-[250px]">
                <h3 className="text-base font-semibold mb-2 flex items-center gap-2">
                    <Activity size={16} className="text-purple-400"/>
                    Descomposición Espectral
                </h3>
                <div className="w-full h-[200px]">
                    <Plot
                        data={[
                            {
                                y: historical?.prices || [],
                                type: 'scatter',
                                mode: 'lines',
                                name: 'Real',
                                line: { color: 'rgba(255,255,255,0.2)', width: 1 }
                            },
                            {
                                y: spectral.reconstructed,
                                type: 'scatter',
                                mode: 'lines',
                                name: 'Señal FFT',
                                line: { color: '#A855F7', width: 1.5 }
                            },
                            {
                                y: trendY,
                                type: 'scatter',
                                mode: 'lines',
                                name: 'Tendencia',
                                line: { color: '#22C55E', width: 1.5 }
                            }
                        ]}
                        layout={{
                            autosize: true,
                            paper_bgcolor: 'rgba(0,0,0,0)',
                            plot_bgcolor: 'rgba(0,0,0,0)',
                            font: { color: '#9CA3AF', size: 10 },
                            xaxis: { showgrid: false },
                            yaxis: { showgrid: true, gridcolor: 'rgba(255,255,255,0.05)' },
                            margin: { l: 30, r: 10, t: 10, b: 20 },
                            showlegend: true
                        }}
                        useResizeHandler={true}
                        style={{ width: '100%', height: '100%' }}
                        config={{ displayModeBar: false }}
                    />
                </div>
            </Card>
        </div>

        {/* Right Column: Stats & Cycles */}
        <div className="space-y-4">
            {/* Market Data Stats */}
            <Card className="p-3">
                <h3 className="text-base font-semibold mb-2 flex items-center gap-2">
                    <DollarSign size={16} className="text-green-400"/>
                    Datos de Mercado
                </h3>
                <div className="space-y-3">
                    <div className="flex justify-between items-center p-2 bg-white/5 rounded">
                        <span className="text-text-secondary text-sm">Precio Actual</span>
                        <span className="font-mono font-bold text-base text-white">
                            ${analysis.data_info?.price_range?.current.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || 'N/A'}
                        </span>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                        <div className="p-2 bg-white/5 rounded">
                            <span className="text-[10px] text-text-secondary block">Mínimo</span>
                            <span className="font-mono text-sm text-red-400">
                                ${analysis.data_info?.price_range?.min.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || 'N/A'}
                            </span>
                        </div>
                        <div className="p-2 bg-white/5 rounded">
                            <span className="text-[10px] text-text-secondary block">Máximo</span>
                            <span className="font-mono text-sm text-green-400">
                                ${analysis.data_info?.price_range?.max.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || 'N/A'}
                            </span>
                        </div>
                    </div>
                </div>
            </Card>

            {/* Cycles Table */}
            <Card className="p-3 flex-1">
                <h3 className="text-base font-semibold mb-2 flex items-center gap-2">
                    <Zap size={16} className="text-yellow-400"/>
                    Ciclos Top Identificados
                </h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                        <thead className="text-[10px] text-text-secondary uppercase bg-white/5">
                            <tr>
                                <th className="px-2 py-1.5">#</th>
                                <th className="px-2 py-1.5">Periodo</th>
                                <th className="px-2 py-1.5">Mag</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/10">
                            {cycles.top_10.slice(0, 8).map((cycle, i) => (
                                <tr key={i} className="hover:bg-white/5">
                                    <td className="px-2 py-1.5 font-mono text-[10px]">{i + 1}</td>
                                    <td className="px-2 py-1.5 font-bold text-accent-gold">
                                        {cycle.period.toFixed(1)}d
                                    </td>
                                    <td className="px-2 py-1.5 text-white/70">
                                        {cycle.magnitude.toFixed(2)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </Card>

            {/* Frequency Spectrum Mini Chart */}
            <Card className="p-3">
                <h3 className="text-base font-semibold mb-1 text-sm flex items-center gap-2">
                    <BarChart2 size={14} className="text-blue-400"/>
                    Espectro de Frecuencia
                </h3>
                <div className="w-full h-[100px]">
                    <Plot
                        data={[
                            {
                                x: spectral.frequencies.slice(0, 50),
                                y: spectral.magnitude.slice(0, 50),
                                type: 'bar',
                                marker: { color: '#3B82F6' }
                            }
                        ]}
                        layout={{
                            autosize: true,
                            paper_bgcolor: 'rgba(0,0,0,0)',
                            plot_bgcolor: 'rgba(0,0,0,0)',
                            xaxis: { showgrid: false, showticklabels: false },
                            yaxis: { showgrid: false, showticklabels: false },
                            margin: { l: 0, r: 0, t: 0, b: 0 }
                        }}
                        useResizeHandler={true}
                        style={{ width: '100%', height: '100%' }}
                        config={{ displayModeBar: false }}
                    />
                </div>
            </Card>
        </div>
      </div>
    </div>
  )
}
