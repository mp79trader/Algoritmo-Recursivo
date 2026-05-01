import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const marketAPI = {
  getMarketTypes: async () => {
    const response = await api.get('/api/markets/types')
    return response.data
  },

  getSymbols: async (marketType) => {
    const response = await api.get(`/api/markets/symbols/${marketType}`)
    return response.data
  },

  getMarketData: async (symbol, period = '2y', interval = '1d') => {
    const response = await api.get(`/api/markets/data/${symbol}`, {
      params: { period, interval }
    })
    return response.data
  },
}

export const analysisAPI = {
  executeAnalysis: async (params) => {
    const response = await api.post('/api/analysis/execute', params)
    return response.data
  },

  getAnalysis: async (id) => {
    const response = await api.get(`/api/analysis/${id}`)
    return response.data
  },

  getHistory: async (filters = {}) => {
    const response = await api.get('/api/analysis/history', { params: filters })
    return response.data
  },
}

export const comparisonAPI = {
  executeComparison: async (params) => {
    const response = await api.post('/api/compare/execute', params)
    return response.data
  },

  getResults: async (id) => {
    const response = await api.get(`/api/compare/results/${id}`)
    return response.data
  },
}

export const documentationAPI = {
  getAlgorithms: async () => {
    const response = await api.get('/api/docs/algorithms')
    return response.data
  },

  getMath: async () => {
    const response = await api.get('/api/docs/math')
    return response.data
  },
}

export default api