import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Zap, Loader, AlertCircle, Sparkles, Star, RefreshCw, Heart, Target, Swords, HeartHandshake as Handshake, Merge } from 'lucide-react'
import { apiService } from '../lib/api'

const BrandMixer = () => {
  const [product1, setProduct1] = useState('')
  const [product2, setProduct2] = useState('')
  const [mode, setMode] = useState('competitive')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [serviceStatus, setServiceStatus] = useState(null)

  const modes = [
    {
      id: 'competitive',
      label: 'Competitive',
      description: 'Brands battle for supremacy',
      icon: Swords,
      color: '#ff6b6b'
    },
    {
      id: 'collaborative',
      label: 'Collaborative', 
      description: 'Strategic partnership approach',
      icon: Handshake,
      color: '#4ecdc4'
    },
    {
      id: 'fusion',
      label: 'Fusion',
      description: 'Complete brand merger',
      icon: Merge,
      color: '#00d4ff'
    }
  ]

  const popularBrands = [
    'Nike', 'Adidas', 'Coca-Cola', 'Pepsi', 'McDonald\'s', 'KFC', 
    'Starbucks', 'Pizza Hut', 'Ben & Jerry\'s', 'Kit Kat',
    'Minecraft', 'Fortnite', 'Pokémon', 'LEGO', 'Red Bull'
  ]

  useEffect(() => {
    checkServiceStatus()
  }, [])

  const checkServiceStatus = async () => {
    try {
      const status = await apiService.getServiceStatus()
      setServiceStatus(status)
    } catch (err) {
      console.warn('Could not check service status:', err)
      setServiceStatus({ 
        status: 'unknown',
        services: {
          llama_index: false,
          claude: false,
          image_generation: false,
          supabase: false
        }
      })
    }
  }

  const handleGenerate = async () => {
    if (!product1.trim() || !product2.trim()) {
      setError('Please enter both brand names')
      return
    }

    if (product1.trim().toLowerCase() === product2.trim().toLowerCase()) {
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
      console.error('Generation error:', err)
      setError(err.message || 'Failed to generate combo. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleVote = async () => {
    if (!result?.id) return

    try {
      await apiService.voteForCombo(result.id)
      setResult(prev => ({
        ...prev,
        votes: (prev.votes || 0) + 1
      }))
    } catch (err) {
      console.error('Vote error:', err)
    }
  }

  const fillRandomBrands = () => {
    const shuffled = [...popularBrands].sort(() => Math.random() - 0.5)
    setProduct1(shuffled[0])
    setProduct2(shuffled[1])
  }

  const resetForm = () => {
    setProduct1('')
    setProduct2('')
    setMode('competitive')
    setResult(null)
    setError('')
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
          Brand Mixer
        </h2>
        <p className="section-subtitle">
          Create revolutionary brand combinations with AI-powered fusion technology
        </p>
      </motion.div>

      {serviceStatus && (
        <motion.div
          className="service-status"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h4>Service Status</h4>
          <div className="status-grid">
            <div className={`status-item ${serviceStatus.services?.claude ? 'active' : 'inactive'}`}>
              <span>Claude AI</span>
              <span className="status-indicator">
                {serviceStatus.services?.claude ? '✓' : '✗'}
              </span>
            </div>
            <div className={`status-item ${serviceStatus.services?.image_generation ? 'active' : 'inactive'}`}>
              <span>Image Gen</span>
              <span className="status-indicator">
                {serviceStatus.services?.image_generation ? '✓' : '✗'}
              </span>
            </div>
            <div className={`status-item ${serviceStatus.services?.supabase ? 'active' : 'inactive'}`}>
              <span>Database</span>
              <span className="status-indicator">
                {serviceStatus.services?.supabase ? '✓' : '✗'}
              </span>
            </div>
            <div className={`status-item ${serviceStatus.services?.llama_index ? 'active' : 'inactive'}`}>
              <span>Knowledge</span>
              <span className="status-indicator">
                {serviceStatus.services?.llama_index ? '✓' : '✗'}
              </span>
            </div>
          </div>
        </motion.div>
      )}

      <motion.div
        className="mixer-container"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="mixer-inputs">
          <div className="input-group">
            <label className="input-label">First Brand</label>
            <input
              type="text"
              className="brand-input"
              placeholder="e.g., Nike"
              value={product1}
              onChange={(e) => setProduct1(e.target.value)}
              maxLength={50}
            />
          </div>

          <div className="mixer-vs">
            <Sparkles className="vs-icon" size={32} />
          </div>

          <div className="input-group">
            <label className="input-label">Second Brand</label>
            <input
              type="text"
              className="brand-input"
              placeholder="e.g., Adidas"
              value={product2}
              onChange={(e) => setProduct2(e.target.value)}
              maxLength={50}
            />
          </div>
        </div>

        <div className="mixer-modes">
          <label className="input-label">Fusion Mode</label>
          <div className="mode-selector">
            {modes.map((modeOption) => {
              const IconComponent = modeOption.icon
              return (
                <motion.div
                  key={modeOption.id}
                  className={`mode-option ${mode === modeOption.id ? 'active' : ''}`}
                  onClick={() => setMode(modeOption.id)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="mode-label">
                    <IconComponent 
                      className="mode-icon" 
                      size={20} 
                      style={{ color: modeOption.color }}
                    />
                    {modeOption.label}
                  </div>
                  <div className="mode-description">{modeOption.description}</div>
                </motion.div>
              )
            })}
          </div>
        </div>

        <div className="mixer-actions">
          <button
            className="btn-outline"
            onClick={fillRandomBrands}
            disabled={loading}
          >
            <Target size={16} />
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

          <button
            className="btn-outline"
            onClick={resetForm}
            disabled={loading}
          >
            <RefreshCw size={16} />
            Reset
          </button>
        </div>

        {error && (
          <motion.div
            className="error-message"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <AlertCircle size={20} />
            <span>{error}</span>
          </motion.div>
        )}

        {result && (
          <motion.div
            className="result-card"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="result-header">
              <h3 className="result-title">{result.name}</h3>
              <div className="result-components">
                {result.components?.a || result.product1} × {result.components?.b || result.product2}
              </div>
              {result.compatibility_score && (
                <div className="result-score">
                  <Star size={16} />
                  {result.compatibility_score}% compatibility
                </div>
              )}
            </div>

            {result.image_url && result.image_url !== 'src/frontend/static/placeholder.png' && (
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

            <div className="result-content">
              {result.slogan && (
                <div className="result-slogan">"{result.slogan}"</div>
              )}
              
              <div className="result-description">
                {result.flavor_description || result.description}
              </div>

              {result.host_reaction && (
                <div className="result-reaction">
                  {result.host_reaction}
                </div>
              )}

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
            </div>

            <div className="result-meta">
              <span>Mode: {result.mode}</span>
              {result.target_audience && (
                <span>Target: {result.target_audience}</span>
              )}
              {result.created_at && (
                <span>Created: {new Date(result.created_at).toLocaleDateString()}</span>
              )}
            </div>

            <div className="result-actions">
              <button
                className="btn-outline"
                onClick={handleVote}
              >
                <Heart size={16} />
                Vote ({result.votes || 0})
              </button>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  )
}

export default BrandMixer