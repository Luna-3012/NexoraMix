import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Zap, Shuffle, Sparkles, Loader, AlertCircle, Star, TrendingUp } from 'lucide-react'
import { apiService } from '../lib/api'

const BrandMixer = () => {
  const [product1, setProduct1] = useState('')
  const [product2, setProduct2] = useState('')
  const [mode, setMode] = useState('competitive')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [availableBrands, setAvailableBrands] = useState([])
  const [backendStatus, setBackendStatus] = useState('checking')
  const [serviceStatus, setServiceStatus] = useState({})

  useEffect(() => {
    checkBackendHealth()
    loadAvailableBrands()
  }, [])

  const checkBackendHealth = async () => {
    try {
      const status = await apiService.getServiceStatus()
      setBackendStatus('healthy')
      setServiceStatus(status.services || {})
    } catch (err) {
      setBackendStatus('error')
      setError('Backend is not responding. Please start the backend server.')
    }
  }

  const loadAvailableBrands = async () => {
    try {
      const response = await apiService.healthCheck()
      // For now, use a predefined list since brands endpoint might not be available
      const brands = [
        'Coca-Cola', 'Pepsi', 'McDonald\'s', 'Burger King', 'KFC',
        'Nike', 'Adidas', 'Apple', 'Samsung', 'Google', 'Microsoft',
        'Netflix', 'Disney', 'Spotify', 'YouTube', 'TikTok',
        'Tesla', 'BMW', 'Mercedes', 'Toyota', 'Ferrari'
      ]
      setAvailableBrands(brands)
    } catch (err) {
      console.warn('Could not load brands:', err)
    }
  }

  const modes = [
    { 
      id: 'competitive', 
      label: 'Competitive Battle', 
      description: 'Brands compete for market dominance',
      icon: '⚔️'
    },
    { 
      id: 'collaborative', 
      label: 'Strategic Alliance', 
      description: 'Brands unite for mutual success',
      icon: '🤝'
    },
    { 
      id: 'fusion', 
      label: 'Complete Fusion', 
      description: 'Brands merge into something new',
      icon: '🔬'
    }
  ]

  const handleGenerate = async () => {
    if (!product1.trim() || !product2.trim()) {
      setError('Please enter both brand names')
      return
    }

    if (product1.toLowerCase() === product2.toLowerCase()) {
      setError('Please select two different brands')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await apiService.generateCombo(product1, product2, mode)
      setResult(response.combo)
    } catch (err) {
      setError(err.message || 'Failed to generate combo')
    } finally {
      setLoading(false)
    }
  }

  const handleRandomize = () => {
    if (availableBrands.length >= 2) {
      const shuffled = [...availableBrands].sort(() => Math.random() - 0.5)
      setProduct1(shuffled[0])
      setProduct2(shuffled[1])
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading && product1.trim() && product2.trim()) {
      handleGenerate()
    }
  }

  if (backendStatus === 'error') {
    return (
      <div className="brand-mixer">
        <div className="mixer-container">
          {result.unique_features && result.unique_features.length > 0 && (
            <div className="result-features">
              <h4>Unique Features:</h4>
              <ul>
                {result.unique_features.map((feature, index) => (
                  <li key={index}>{feature}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="error-message">
            <AlertCircle size={20} />
            {result.target_audience && (
              <span className="result-audience">Target: {result.target_audience}</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="brand-mixer">
      <motion.div
        className="mixer-header"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 className="section-title">
          <Zap className="title-icon" />
          Brand Mixologist
        </h2>
        <p className="section-subtitle">
          Combine two brands and unleash the power of AI fusion
        </p>
      </motion.div>

      {Object.keys(serviceStatus).length > 0 && (
        <motion.div
          className="service-status"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <h4>Service Status</h4>
          <div className="status-grid">
            <div className={`status-item ${serviceStatus.llama_index ? 'active' : 'inactive'}`}>
              <span>LlamaIndex</span>
              <span className="status-indicator">{serviceStatus.llama_index ? '✓' : '✗'}</span>
            </div>
            <div className={`status-item ${serviceStatus.claude ? 'active' : 'inactive'}`}>
              <span>Claude AI</span>
              <span className="status-indicator">{serviceStatus.claude ? '✓' : '✗'}</span>
            </div>
            <div className={`status-item ${serviceStatus.image_generation ? 'active' : 'inactive'}`}>
              <span>Image Gen</span>
              <span className="status-indicator">{serviceStatus.image_generation ? '✓' : '✗'}</span>
            </div>
            <div className={`status-item ${serviceStatus.supabase ? 'active' : 'inactive'}`}>
              <span>Supabase</span>
              <span className="status-indicator">{serviceStatus.supabase ? '✓' : '✗'}</span>
            </div>
          </div>
        </motion.div>
      )}

      <div className="mixer-container">
        <motion.div
          className="mixer-inputs"
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="input-group">
            <label className="input-label">First Brand</label>
            <input
              type="text"
              className="brand-input"
              value={product1}
              onChange={(e) => setProduct1(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter brand name..."
              list="brands1"
              maxLength={50}
            />
            <datalist id="brands1">
              {availableBrands.map(brand => (
                <option key={brand} value={brand} />
              ))}
            </datalist>
          </div>

          <div className="mixer-vs">
            <motion.div
              className="vs-icon"
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles size={24} />
            </motion.div>
          </div>

          <div className="input-group">
            <label className="input-label">Second Brand</label>
            <input
              type="text"
              className="brand-input"
              value={product2}
              onChange={(e) => setProduct2(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter brand name..."
              list="brands2"
              maxLength={50}
            />
            <datalist id="brands2">
              {availableBrands.map(brand => (
                <option key={brand} value={brand} />
              ))}
            </datalist>
          </div>
        </motion.div>

        <motion.div
          className="mixer-modes"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <label className="input-label">Fusion Mode</label>
          <div className="mode-selector">
            {modes.map(({ id, label, description, icon }) => (
              <motion.button
                key={id}
                className={`mode-option ${mode === id ? 'active' : ''}`}
                onClick={() => setMode(id)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="mode-label">
                  <span className="mode-icon">{icon}</span>
                  {label}
                </div>
                <div className="mode-description">{description}</div>
              </motion.button>
            ))}
          </div>
        </motion.div>

        <motion.div
          className="mixer-actions"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <button
            className="btn-secondary"
            onClick={handleRandomize}
            disabled={loading}
          >
            <Shuffle size={20} />
            Random Brands
          </button>
          
          <button
            className="btn-primary mixer-generate"
            onClick={handleGenerate}
            disabled={loading || !product1.trim() || !product2.trim()}
          >
            {loading ? (
              <>
                <Loader className="spinning" size={20} />
                Generating...
              </>
            ) : (
              <>
                <Zap size={20} />
                Generate Fusion
              </>
            )}
          </button>
        </motion.div>

            {result.image_url && (
              <div className="result-image">
                <img 
                  src={result.image_url} 
                  alt={result.name}
                  onError={(e) => {
                    e.target.style.display = 'none'
                  }}
                />
              </div>
            )}
            
        {error && (
          <motion.div
            className="error-message"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <AlertCircle size={20} />
            {error}
          </motion.div>
        )}

        {result && (
          <motion.div
            className="result-card"
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ type: "spring", damping: 20 }}
          >
            <div className="result-header">
              <h3 className="result-title">{result.name}</h3>
              <div className="result-components">
                {result.components.a} × {result.components.b}
              </div>
              {result.compatibility_score && (
                <div className="result-score">
                  <Star size={16} />
                  Compatibility: {result.compatibility_score}%
                </div>
              )}
            </div>
            
            <div className="result-content">
              <div className="result-slogan">
                "{result.slogan}"
              </div>
              
              <div className="result-description">
                {result.flavor_description}
              </div>
              
              {result.host_reaction && (
                <div className="result-reaction">
                  {result.host_reaction}
                </div>
              )}

              <div className="result-meta">
                <span className="result-mode">Mode: {result.mode}</span>
                {result.categories && (
                  <span className="result-categories">
                    Categories: {result.categories.a} + {result.categories.b}
                  </span>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}

export default BrandMixer