import axios from 'axios'
import { supabaseOperations } from './supabase'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const apiService = {
  // Generate brand combo
  async generateCombo(product1, product2, mode = 'competitive') {
    try {
      const response = await api.post('/generate', {
        product1: product1.trim(),
        product2: product2.trim(),
        mode
      })
      
      // Save to Supabase if available
      try {
        const combo = response.data.combo
        await supabaseOperations.createCombo({
          name: combo.name,
          slogan: combo.slogan,
          description: combo.flavor_description,
          product1: combo.components.a,
          product2: combo.components.b,
          mode: combo.mode,
          votes: 0,
          host_reaction: combo.host_reaction
        })
      } catch (supabaseError) {
        console.warn('Failed to save to Supabase:', supabaseError)
      }
      
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Failed to generate combo')
    }
  },

  // Get leaderboard
  async getLeaderboard(limit = 10) {
    try {
      // Try Supabase first
      const supabaseData = await supabaseOperations.getCombos(limit)
      return { combos: supabaseData }
    } catch (supabaseError) {
      console.warn('Supabase unavailable, using backend:', supabaseError)
      
      // Fallback to backend
      const response = await api.get(`/leaderboard?limit=${limit}`)
      return response.data
    }
  },

  // Vote for combo
  async voteForCombo(comboId) {
    try {
      // Try Supabase first
      await supabaseOperations.voteForCombo(comboId)
      return { status: 'voted' }
    } catch (supabaseError) {
      console.warn('Supabase unavailable, using backend:', supabaseError)
      
      // Fallback to backend
      const response = await api.post('/vote', { combo_id: comboId })
      return response.data
    }
  },

  // Get statistics
  async getStats() {
    try {
      return await supabaseOperations.getStats()
    } catch (supabaseError) {
      console.warn('Supabase unavailable for stats:', supabaseError)
      return { totalCombos: 0, totalVotes: 0 }
    }
  },

  // Health check
  async healthCheck() {
    try {
      const response = await api.get('/health')
      return response.data
    } catch (error) {
      throw new Error('Backend is not responding')
    }
  }
}