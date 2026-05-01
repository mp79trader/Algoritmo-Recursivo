import React, { useState, useEffect } from 'react'
import { Card } from '../components/common/Card'
import { Button } from '../components/common/Button'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { Settings as SettingsIcon, Database, MapPin, FolderOpen, Globe, Plus, Edit, Trash2 } from 'lucide-react'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

export function Settings() {
  const [loading, setLoading] = useState(false)
  const [config, setConfig] = useState(null)
  const [mappings, setMappings] = useState(null)
  const [ninjaConfig, setNinjaConfig] = useState(null)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [editingMapping, setEditingMapping] = useState(null)
  const [showAddMapping, setShowAddMapping] = useState(false)

  useEffect(() => {
    fetchConfiguration()
  }, [])

  const fetchConfiguration = async () => {
    setLoading(true)
    try {
      const [sourcesRes, mappingsRes, ninjaRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/config/datasources`),
        axios.get(`${API_BASE_URL}/api/config/symbols/mappings`),
        axios.get(`${API_BASE_URL}/api/config/ninja`)
      ])

      setConfig(sourcesRes.data)
      setMappings(mappingsRes.data.mappings)
      setNinjaConfig(ninjaRes.data)
    } catch (error) {
      showMessage('error', 'Error al cargar la configuración')
    } finally {
      setLoading(false)
    }
  }

  const showMessage = (type, text) => {
    setMessage({ type, text })
    setTimeout(() => setMessage({ type: '', text: '' }), 3000)
  }

  const handleSourceChange = async (sourceType, source) => {
    setLoading(true)
    try {
      await axios.post(`${API_BASE_URL}/api/config/datasource`, {
        type: sourceType,
        source: source
      })
      
      showMessage('success', `Fuente ${sourceType === 'realtime' ? 'en tiempo real' : 'histórica'} actualizada a ${source}`)
      fetchConfiguration()
    } catch (error) {
      showMessage('error', `Error al actualizar fuente ${sourceType}`)
    } finally {
      setLoading(false)
    }
  }

  const handleNinjaDirChange = async () => {
    const newDir = prompt('Ingrese el directorio de intercambio de NinjaTrader:', ninjaConfig?.exchange_dir || '')
    
    if (!newDir) return

    setLoading(true)
    try {
      await axios.post(`${API_BASE_URL}/api/config/ninja`, {
        exchange_dir: newDir
      })
      
      showMessage('success', 'Directorio de NinjaTrader actualizado')
      fetchConfiguration()
    } catch (error) {
      showMessage('error', 'Error al actualizar directorio de NinjaTrader')
    } finally {
      setLoading(false)
    }
  }

  const handleAddMapping = async (internalSymbol, yfinance, ninjatrader, mt5) => {
    setLoading(true)
    try {
      await Promise.all([
        yfinance && axios.post(`${API_BASE_URL}/api/config/symbols/mapping`, {
          internal_symbol: internalSymbol,
          source: 'yfinance',
          external_symbol: yfinance
        }),
        ninjatrader && axios.post(`${API_BASE_URL}/api/config/symbols/mapping`, {
          internal_symbol: internalSymbol,
          source: 'ninjatrader',
          external_symbol: ninjatrader
        }),
        mt5 && axios.post(`${API_BASE_URL}/api/config/symbols/mapping`, {
          internal_symbol: internalSymbol,
          source: 'mt5',
          external_symbol: mt5
        })
      ].filter(Boolean))

      showMessage('success', 'Mapeo de símbolos actualizado')
      setShowAddMapping(false)
      setEditingMapping(null)
      fetchConfiguration()
    } catch (error) {
      showMessage('error', 'Error al actualizar mapeo de símbolos')
    } finally {
      setLoading(false)
    }
  }

  if (loading && !config) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-[1200px] mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3 mb-2">
          <SettingsIcon size={32} className="text-accent-gold" />
          Configuración
        </h1>
        <p className="text-text-secondary">
          Configura fuentes de datos, mapeo de símbolos y conexiones de plataformas
        </p>
      </div>

      {/* Message */}
      {message.text && (
        <div className={`p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-500/20 border border-green-500/30' : 
          'bg-red-500/20 border border-red-500/30'
        }`}>
          <p className={message.type === 'success' ? 'text-green-400' : 'text-red-400'}>
            {message.text}
          </p>
        </div>
      )}

      {/* Data Sources Configuration */}
      <Card className="p-6">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Database size={20} className="text-blue-400" />
          Fuentes de Datos
        </h2>

        <div className="space-y-6">
          {/* Real-time Source */}
          <div>
            <label className="block text-sm font-medium mb-2 text-text-secondary">
              Fuente de Datos en Tiempo Real
            </label>
            <p className="text-xs text-text-secondary mb-3">
              Usada para señales en vivo y datos de mercado al instante
            </p>
            <div className="flex gap-3">
              <Button
                variant={config?.current.realtime_source === 'yfinance' ? 'primary' : 'secondary'}
                onClick={() => handleSourceChange('realtime', 'yfinance')}
                disabled={loading}
              >
                Yahoo Finance
              </Button>
              <Button
                variant={config?.current.realtime_source === 'ninjatrader' ? 'primary' : 'secondary'}
                onClick={() => handleSourceChange('realtime', 'ninjatrader')}
                disabled={loading}
              >
                NinjaTrader
              </Button>
              <Button
                variant={config?.current.realtime_source === 'mt5' ? 'primary' : 'secondary'}
                onClick={() => handleSourceChange('realtime', 'mt5')}
                disabled={loading}
              >
                MetaTrader 5
              </Button>
            </div>
          </div>

          {/* Historical Source */}
          <div>
            <label className="block text-sm font-medium mb-2 text-text-secondary">
              Fuente de Datos Históricos
            </label>
            <p className="text-xs text-text-secondary mb-3">
              Usada para análisis de largo plazo y backtesting
            </p>
            <div className="flex gap-3">
              <Button
                variant={config?.current.historical_source === 'yfinance' ? 'primary' : 'secondary'}
                onClick={() => handleSourceChange('historical', 'yfinance')}
                disabled={loading}
              >
                Yahoo Finance
              </Button>
              <Button
                variant={config?.current.historical_source === 'ninjatrader' ? 'primary' : 'secondary'}
                onClick={() => handleSourceChange('historical', 'ninjatrader')}
                disabled={loading}
              >
                NinjaTrader
              </Button>
              <Button
                variant={config?.current.historical_source === 'mt5' ? 'primary' : 'secondary'}
                onClick={() => handleSourceChange('historical', 'mt5')}
                disabled={loading}
              >
                MetaTrader 5
              </Button>
            </div>
          </div>
        </div>
      </Card>

      {/* Symbol Mappings */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-xl font-bold flex items-center gap-2">
              <MapPin size={20} className="text-purple-400" />
              Mapeo de Símbolos
            </h2>
            <p className="text-sm text-text-secondary mt-1">
              Mapea símbolos internos a nombres específicos de cada plataforma
            </p>
          </div>
          <Button onClick={() => setShowAddMapping(true)} className="flex items-center gap-2">
            <Plus size={16} />
            Agregar Mapeo
          </Button>
        </div>

        {/* Add/Edit Mapping Form */}
        {(showAddMapping || editingMapping) && (
          <MappingForm
            initialData={editingMapping}
            onSave={handleAddMapping}
            onCancel={() => {
              setShowAddMapping(false)
              setEditingMapping(null)
            }}
          />
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-xs uppercase bg-white/5 border-b border-white/10">
              <tr>
                <th className="px-4 py-3 text-left">Símbolo Interno</th>
                <th className="px-4 py-3 text-left">Yahoo Finance</th>
                <th className="px-4 py-3 text-left">NinjaTrader</th>
                <th className="px-4 py-3 text-left">MetaTrader 5</th>
                <th className="px-4 py-3 text-center">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {mappings && Object.entries(mappings).map(([internal, sources]) => (
                <tr key={internal} className="hover:bg-white/5">
                  <td className="px-4 py-3 font-mono font-bold text-accent-gold">{internal}</td>
                  <td className="px-4 py-3 text-white/70">{sources.yfinance || '-'}</td>
                  <td className="px-4 py-3 text-white/70">{sources.ninjatrader || '-'}</td>
                  <td className="px-4 py-3 text-white/70">{sources.mt5 || '-'}</td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => setEditingMapping({ internal, ...sources })}
                      className="text-blue-400 hover:text-blue-300 p-1"
                      title="Editar"
                    >
                      <Edit size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Platform Configurations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* NinjaTrader Config */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
            <FolderOpen size={18} className="text-orange-400" />
            NinjaTrader
          </h2>
          
          <div className="space-y-3">
            <div>
              <label className="block text-xs text-text-secondary mb-1">Directorio de Intercambio</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={ninjaConfig?.exchange_dir || ''}
                  disabled
                  className="flex-1 bg-white/5 border border-white/10 rounded px-3 py-2 text-sm"
                />
                <Button onClick={handleNinjaDirChange} disabled={loading}>
                  Cambiar
                </Button>
              </div>
            </div>
            <p className="text-xs text-text-secondary">
              Directorio donde ConnectorFFT.cs intercambia archivos de datos
            </p>
          </div>
        </Card>

        {/* MT5 Config */}
        <Card className="p-6">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
            <Globe size={18} className="text-green-400" />
            MetaTrader 5
          </h2>
          
          <div className="space-y-3">
            <p className="text-sm text-text-secondary">
              Configuración de MT5 próximamente. Instala el paquete Python de MetaTrader5 para habilitar.
            </p>
            <code className="block bg-black/30 p-2 rounded text-xs">
              pip install MetaTrader5
            </code>
          </div>
        </Card>
      </div>

      {/* Information Panel */}
      <Card className="p-6 bg-blue-500/10 border-blue-500/30">
        <h3 className="font-bold mb-2 text-blue-400">¿Cómo Funciona?</h3>
        <ul className="text-sm text-white/80 space-y-2">
          <li>• <strong>Fuentes en tiempo real</strong> proveen datos en vivo para señales inmediatas (recomendado: NinjaTrader o MT5)</li>
          <li>• <strong>Fuentes históricas</strong> proveen datos de largo plazo para análisis y backtesting</li>
          <li>• <strong>Mapeo de símbolos</strong> asegura la traducción correcta entre plataformas</li>
          <li>• El conector de NinjaTrader usa intercambio de archivos via <code className="bg-black/30 px-1">ConnectorFFT.cs</code></li>
          <li>• El conector de MT5 usa conexión directa por API (requiere paquete MetaTrader5)</li>
        </ul>
      </Card>
    </div>
  )
}

function MappingForm({ initialData, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    internal: initialData?.internal || '',
    yfinance: initialData?.yfinance || '',
    ninjatrader: initialData?.ninjatrader || '',
    mt5: initialData?.mt5 || ''
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSave(formData.internal, formData.yfinance, formData.ninjatrader, formData.mt5)
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white/5 p-4 rounded-lg mb-4 space-y-3">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <label className="block text-xs text-text-secondary mb-1">Símbolo Interno</label>
          <input
            type="text"
            value={formData.internal}
            onChange={(e) => setFormData({ ...formData, internal: e.target.value })}
            className="w-full bg-white/5 border border-white/10 rounded px-3 py-2 text-sm"
            placeholder="MNQ"
            required
            disabled={!!initialData}
          />
        </div>
        <div>
          <label className="block text-xs text-text-secondary mb-1">Yahoo Finance</label>
          <input
            type="text"
            value={formData.yfinance}
            onChange={(e) => setFormData({ ...formData, yfinance: e.target.value })}
            className="w-full bg-white/5 border border-white/10 rounded px-3 py-2 text-sm"
            placeholder="MNQ=F"
          />
        </div>
        <div>
          <label className="block text-xs text-text-secondary mb-1">NinjaTrader</label>
          <input
            type="text"
            value={formData.ninjatrader}
            onChange={(e) => setFormData({ ...formData, ninjatrader: e.target.value })}
            className="w-full bg-white/5 border border-white/10 rounded px-3 py-2 text-sm"
            placeholder="MNQ"
          />
        </div>
        <div>
          <label className="block text-xs text-text-secondary mb-1">MetaTrader 5</label>
          <input
            type="text"
            value={formData.mt5}
            onChange={(e) => setFormData({ ...formData, mt5: e.target.value })}
            className="w-full bg-white/5 border border-white/10 rounded px-3 py-2 text-sm"
            placeholder="NQ-MAR26"
          />
        </div>
      </div>
      <div className="flex gap-2 justify-end">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit">
          Guardar
        </Button>
      </div>
    </form>
  )
}
