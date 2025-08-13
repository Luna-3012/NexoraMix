import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Zap, 
  Trophy, 
  Sparkles, 
  Play, 
  Users, 
  Target,
  ChevronDown,
  Star,
  Gamepad2,
  Cpu,
  Shield
} from 'lucide-react'
import BrandMixer from './components/BrandMixer'
import Leaderboard from './components/Leaderboard'
import ParticleBackground from './components/ParticleBackground'

function App() {
  const [activeSection, setActiveSection] = useState('home')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 2000)
    return () => clearTimeout(timer)
  }, [])

  const sections = [
    { id: 'home', label: 'Home', icon: Shield },
    { id: 'mixer', label: 'Brand Mixer', icon: Zap },
    { id: 'leaderboard', label: 'Leaderboard', icon: Trophy },
    { id: 'about', label: 'About', icon: Cpu }
  ]

  if (isLoading) {
    return (
      <div className="loading-screen">
        <ParticleBackground />
        <div className="loading-content">
          <motion.div
            className="loading-logo"
            animate={{ 
              scale: [1, 1.2, 1],
              rotate: [0, 360]
            }}
            transition={{ 
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            <Gamepad2 size={80} />
          </motion.div>
          <motion.h1
            className="loading-title"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            NEXORA
          </motion.h1>
          <div className="loading-bar">
            <motion.div
              className="loading-progress"
              animate={{ width: "100%" }}
              transition={{ duration: 2, ease: "easeOut" }}
            />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <ParticleBackground />
      
      <nav className="nav-bar">
        <div className="nav-brand">
          <Gamepad2 className="nav-logo" />
          <span className="nav-title">NEXORA</span>
        </div>
        
        <div className="nav-links">
          {sections.map(({ id, label, icon: Icon }) => (
            <motion.button
              key={id}
              className={`nav-link ${activeSection === id ? 'active' : ''}`}
              onClick={() => setActiveSection(id)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Icon size={18} />
              <span>{label}</span>
            </motion.button>
          ))}
        </div>
      </nav>

      <main className="main-content">
        <AnimatePresence mode="wait">
          {activeSection === 'home' && (
            <motion.section
              key="home"
              className="hero-section"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -50 }}
              transition={{ duration: 0.6 }}
            >
              <div className="hero-content">
                <motion.div
                  className="hero-badge"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  <Sparkles size={16} />
                  <span>AI-Powered Brand Fusion</span>
                </motion.div>

                <motion.h1
                  className="hero-title"
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  BRAND
                  <span className="hero-title-accent">MIXOLOGIST</span>
                </motion.h1>

                <motion.p
                  className="hero-description"
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  Unleash the power of AI to create revolutionary brand combinations. 
                  Mix, match, and discover the next big fusion in the digital arena.
                </motion.p>

                <motion.div
                  className="hero-actions"
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                >
                  <button
                    className="btn-primary"
                    onClick={() => setActiveSection('mixer')}
                  >
                    <Play size={20} />
                    Start Mixing
                  </button>
                  <button
                    className="btn-secondary"
                    onClick={() => setActiveSection('leaderboard')}
                  >
                    <Trophy size={20} />
                    View Leaderboard
                  </button>
                </motion.div>
              </div>
            </motion.section>
          )}

          {activeSection === 'mixer' && (
            <motion.section
              key="mixer"
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -100 }}
              transition={{ duration: 0.6 }}
            >
              <BrandMixer />
            </motion.section>
          )}

          {activeSection === 'leaderboard' && (
            <motion.section
              key="leaderboard"
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -100 }}
              transition={{ duration: 0.6 }}
            >
              <Leaderboard />
            </motion.section>
          )}

          {activeSection === 'about' && (
            <motion.section
              key="about"
              className="about-section"
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -100 }}
              transition={{ duration: 0.6 }}
            >
              <div className="about-content">
                <h2 className="section-title">About Nexora</h2>
                <p className="about-text">
                  Nexora represents the cutting edge of AI-powered brand fusion technology. 
                  Our advanced algorithms create innovative combinations that push the 
                  boundaries of creative marketing.
                </p>
              </div>
            </motion.section>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}

export default App