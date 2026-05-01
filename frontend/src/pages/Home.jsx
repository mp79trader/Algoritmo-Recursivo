import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { BarChart3, Zap, TrendingUp, Shield, Code, Play } from 'lucide-react'
import { marketAPI } from '../services/api'
import { LoadingSpinner } from '../components/common/LoadingSpinner'

export function Home() {
  const [selectedMarket, setSelectedMarket] = useState('futures')
  const [symbols, setSymbols] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchSymbols()
  }, [selectedMarket])

  const fetchSymbols = async () => {
    setLoading(true)
    try {
      const data = await marketAPI.getSymbols(selectedMarket)
      setSymbols(data.symbols || [])
    } catch (error) {
      console.error('Error fetching symbols:', error)
      setSymbols([])
    } finally {
      setLoading(false)
    }
  }

  const features = [
    {
      icon: BarChart3,
      title: 'FFT Recursivo Avanzado',
      description: 'Algoritmo Cooley-Tukey con complejidad O(n log n) para análisis espectral de alta precisión'
    },
    {
      icon: Zap,
      title: 'Predicción en Tiempo Real',
      description: 'Análisis de tendencias y ciclos con procesamiento instantáneo de datos de mercado'
    },
    {
      icon: TrendingUp,
      title: 'Multi-Mercado',
      description: 'Futuros, Acciones, Criptomonedas y ETFs en una plataforma unificada'
    },
    {
      icon: Shield,
      title: 'Backtesting Completo',
      description: 'Validación histórica con métricas de performance y gestión de riesgos'
    },
  ]

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-12 px-6 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-accent-gold-light/20 to-transparent"></div>

        <div className="max-w-6xl mx-auto relative z-10">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-40 h-40 mb-6 animate-pulse-glow">
              <img src="/assets/QuantumFFT.png" alt="QuantumFFT Logo" className="w-full h-full object-contain" />
            </div>

            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="text-accent-gold text-glow">QuantuM FFT</span>
            </h1>
            <p className="text-lg md:text-xl text-text-secondary max-w-2xl mx-auto">
              Algoritmo de Predicción de Mercado usando Transformada Rápida de Fourier Recursiva
            </p>
          </div>

          {/* Quick Start */}
          <div className="flex flex-col sm:flex-row gap-3 justify-center items-center mt-6">
            <Link to="/analysis/MNQ=F" className="btn-gold text-base px-6 py-3">
              <div className="flex items-center gap-2">
                <Play size={18} />
                <span>Comenzar Análisis</span>
              </div>
            </Link>
            <Link to="/documentation" className="border-2 border-accent-gold text-accent-gold bg-transparent hover:bg-accent-gold hover:text-primary-bg font-semibold px-6 py-3 rounded-lg transition-all duration-300">
              Documentación
            </Link>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-12 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold text-center mb-10">
            Características Principales
          </h2>

          <div className="responsive-grid gap-4">
            {features.map((feature, index) => (
              <Card key={index} className="glow-effect p-5">
                <feature.icon size={32} className="text-accent-gold mb-4" />
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-text-secondary leading-relaxed">
                  {feature.description}
                </p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Market Types */}
      <section className="py-12 px-6 bg-gradient-to-b from-accent-gold-light/10 to-transparent">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold text-center mb-6">
            Analiza Cualquier Tipo de Mercado
          </h2>

          <div className="flex flex-wrap justify-center gap-3 mb-8">
            {[
              { key: 'futures', label: 'Futuros de Índices' },
              { key: 'stocks', label: 'Acciones' },
              { key: 'crypto', label: 'Criptomonedas' },
              { key: 'etf', label: 'ETFs' },
            ].map((market) => (
              <button
                key={market.key}
                onClick={() => setSelectedMarket(market.key)}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all duration-300 ${selectedMarket === market.key
                    ? 'bg-accent-gold text-primary-bg'
                    : 'bg-secondary-bg border border-accent-gold/30 text-text-secondary hover:border-accent-gold'
                  }`}
              >
                {market.label}
              </button>
            ))}
          </div>

          {loading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner />
            </div>
          ) : (
            <div className="responsive-grid gap-4">
              {symbols.map((symbol, index) => (
                <div key={index} className="glass-card p-4 hover:scale-105 transition-transform duration-300 cursor-pointer">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-8 h-8 rounded-full bg-accent-gold/20 flex items-center justify-center">
                      <Code size={16} className="text-accent-gold" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-sm">{symbol.symbol}</h4>
                      <p className="text-xs text-text-secondary">{symbol.name}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Link
                      to={`/analysis/${encodeURIComponent(symbol.symbol)}`}
                      className="text-accent-gold text-xs font-medium hover:underline flex-1 text-center border border-accent-gold/30 rounded py-1"
                    >
                      Analizar
                    </Link>
                    <Link
                      to={`/live/${encodeURIComponent(symbol.symbol)}`}
                      className="text-green-400 text-xs font-medium hover:underline flex-1 text-center border border-green-400/30 rounded py-1"
                    >
                      En Vivo
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}

          {symbols.length === 0 && !loading && (
            <div className="text-center py-8 text-text-secondary">
              No se encontraron símbolos para este mercado.
            </div>
          )}
        </div>
      </section>

      {/* Technical Info */}
      <section className="py-12 px-6">
        <div className="max-w-4xl mx-auto">
          <Card className="p-8">
            <h2 className="text-2xl font-bold text-center mb-6 text-accent-gold">
              Fundamento Científico
            </h2>

            <div className="space-y-4 text-text-secondary text-sm">
              <div>
                <h3 className="text-lg font-semibold text-text-primary mb-2">
                  Transformada de Fourier Recursiva
                </h3>
                <p className="leading-relaxed">
                  La Transformada Rápida de Fourier (FFT) descompone una señal de mercado en sus componentes de frecuencia fundamentales. Nuestra implementación recursiva del algoritmo Cooley-Tukey permite un análisis espectral con complejidad O(n log n), identificando patrones cíclicos y tendencias ocultas en los datos de precio.
                </p>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-text-primary mb-2">
                  Componentes de Frecuencia
                </h3>
                <ul className="space-y-1">
                  <li className="flex items-start gap-2">
                    <span className="text-accent-gold">●</span>
                    <span><strong>Baja Frecuencia:</strong> Representa tendencias de largo plazo</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-accent-gold">●</span>
                    <span><strong>Media Frecuencia:</strong> Ciclos estacionales y patrones periódicos</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-accent-gold">●</span>
                    <span><strong>Alta Frecuencia:</strong> Volatilidad de corto plazo y ruido</span>
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-text-primary mb-2">
                  Filtrado Adaptativo
                </h3>
                <p className="leading-relaxed">
                  Sistema inteligente que selecciona automáticamente los componentes de frecuencia más relevantes basado en magnitud y significancia estadística, eliminando ruido y enfocándose en patrones predecibles.
                </p>
              </div>

              <div className="mt-6 text-center">
                <Link to="/documentation" className="btn-gold text-sm px-6 py-2">
                  Documentación Completa
                </Link>
              </div>
            </div>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-12 px-6 bg-gradient-to-b from-accent-gold-light/20 to-transparent">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-2xl md:text-3xl font-bold mb-4">
            ¿Listo para Comenzar?
          </h2>
          <p className="text-lg text-text-secondary mb-6">
            Inicia tu análisis ahora y descubre patrones ocultos en los mercados financieros
          </p>
          <Link to="/analysis/MNQ=F" className="btn-gold text-base px-8 py-3">
            Acceder al Dashboard
          </Link>
        </div>
      </section>
    </div>
  )
}

function Card({ children, className = '' }) {
  return (
    <div className={`glass-card ${className}`}>
      {children}
    </div>
  )
}