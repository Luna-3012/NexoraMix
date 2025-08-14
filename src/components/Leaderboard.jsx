import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Trophy, Star, TrendingUp, Users, Heart, Loader, RefreshCw } from 'lucide-react'
import { api } from '../lib/api'

const Leaderboard = () => {
  const [combos, setCombos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [stats, setStats] = useState({ totalCombos: 0, totalVotes: 0 })
  const [votingLoading, setVotingLoading] = useState({})

  useEffect(() => {
    fetchLeaderboard()
    fetchStats()
  }, [])

  const fetchLeaderboard = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await api.getLeaderboard(10)
      setCombos(response.combos || [])
    } catch (err) {
      setError(err.message || 'Failed to load leaderboard')
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const statsData = await api.getStats()
      setStats(statsData)
    } catch (err) {
      console.warn('Failed to load stats:', err)
    }
  }

  const handleVote = async (comboId) => {
    if (votingLoading[comboId]) return

    try {
      setVotingLoading(prev => ({ ...prev, [comboId]: true }))
      await api.voteForCombo(comboId)
      
      // Update local state optimistically
      setCombos(prev => prev.map(combo => 
        combo.id === comboId 
          ? { ...combo, votes: (combo.votes || 0) + 1 }
          : combo
      ))
      
      // Refresh stats
      fetchStats()
    } catch (err) {
      console.error('Failed to vote:', err)
      // Optionally show error message
    } finally {
      setVotingLoading(prev => ({ ...prev, [comboId]: false }))
    }
  }

  const getRankIcon = (index) => {
    switch (index) {
      case 0: return <Trophy className="rank-icon gold" size={24} />
      case 1: return <Trophy className="rank-icon silver" size={24} />
      case 2: return <Trophy className="rank-icon bronze" size={24} />
      default: return <span className="rank-number">#{index + 1}</span>
    }
  }

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString()
    } catch {
      return 'Unknown'
    }
  }

  if (loading) {
    return (
      <div className="leaderboard">
        <div className="loading-state">
          <Loader className="spinning" size={40} />
          <p>Loading leaderboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="leaderboard">
      <motion.div
        className="leaderboard-header"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 className="section-title">
          <Trophy className="title-icon" />
          Hall of Fame
        </h2>
        <p className="section-subtitle">
          The most popular brand fusions created by our community
        </p>
        
        <button 
          className="btn-outline refresh-btn"
          onClick={fetchLeaderboard}
          disabled={loading}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </motion.div>

      <div className="leaderboard-stats">
        <motion.div 
          className="stat-card"
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <TrendingUp className="stat-icon" />
          <div className="stat-content">
            <div className="stat-number">{stats.totalCombos}</div>
            <div className="stat-label">Total Combos</div>
          </div>
        </motion.div>
        
        <motion.div 
          className="stat-card"
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Users className="stat-icon" />
          <div className="stat-content">
            <div className="stat-number">{stats.totalVotes}</div>
            <div className="stat-label">Total Votes</div>
          </div>
        </motion.div>
        
        <motion.div 
          className="stat-card"
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Star className="stat-icon" />
          <div className="stat-content">
            <div className="stat-number">
              {combos.length > 0 ? Math.round(stats.totalVotes / stats.totalCombos) : 0}
            </div>
            <div className="stat-label">Avg Votes</div>
          </div>
        </motion.div>
      </div>

      {error && (
        <div className="error-message">
          <span>{error}</span>
          <button onClick={fetchLeaderboard} className="btn-outline">
            Try Again
          </button>
        </div>
      )}

      <div className="leaderboard-list">
        {combos.map((combo, index) => (
          <motion.div
            key={combo.id || index}
            className={`leaderboard-item ${index < 3 ? 'podium' : ''}`}
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
          >
            <div className="item-rank">
              {getRankIcon(index)}
            </div>

            <div className="item-content">
              <div className="item-header">
                <h3 className="item-title">{combo.name || 'Unnamed Combo'}</h3>
                <div className="item-components">
                  {combo.components ? 
                    `${combo.components.a} × ${combo.components.b}` : 
                    combo.product1 && combo.product2 ?
                    `${combo.product1} × ${combo.product2}` :
                    'Unknown Components'
                  }
                </div>
                {combo.compatibility_score && (
                  <div className="item-score">
                    <Star size={14} />
                    {combo.compatibility_score}% compatibility
                  </div>
                )}
              </div>

              <div className="item-description">
                {combo.slogan || combo.description || combo.flavor_description || 'No description available'}
              </div>

              <div className="item-meta">
                <span className="item-mode">Mode: {combo.mode || 'Unknown'}</span>
                {combo.created_at && (
                  <span className="item-date">Created: {formatDate(combo.created_at)}</span>
                )}
              </div>
            </div>

            <div className="item-actions">
              <div className="vote-count">
                <Star size={16} />
                {combo.votes || 0}
              </div>
              <motion.button
                className="vote-btn"
                onClick={() => handleVote(combo.id)}
                disabled={votingLoading[combo.id]}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                {votingLoading[combo.id] ? (
                  <Loader className="spinning" size={16} />
                ) : (
                  <Heart size={16} />
                )}
              </motion.button>
            </div>
          </motion.div>
        ))}
      </div>

      {combos.length === 0 && !loading && !error && (
        <div className="empty-state">
          <Trophy size={60} className="empty-icon" />
          <h3>No combos yet!</h3>
          <p>Be the first to create a brand fusion and claim the top spot!</p>
        </div>
      )}
    </div>
  )
}

export default Leaderboard