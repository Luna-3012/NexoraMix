import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    }
});

// Request interceptor for logging
// api.interceptors.request.use(
//   (config) => {
//     console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
//     return config
//   },
//   (error) => {
//     console.error('API Request Error:', error)
//     return Promise.reject(error)
//   }
// )

apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', `${config.method.toUpperCase()} ${config.url}`);
    return config;
});

// Response interceptor for error handling
// api.interceptors.response.use(
//   (response) => {
//     console.log(`API Response: ${response.status} ${response.config.url}`)
//     return response
//   },
//   (error) => {
//     console.error('API Response Error:', error.response?.data || error.message)
//     return Promise.reject(error)
//   }
// )

apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Response Error:', {
            message: error.message,
            status: error.response?.status,
            data: error.response?.data
        });
        
        // Customize error message based on error type
        if (error.code === 'ECONNREFUSED') {
            throw new Error('Backend service is not running');
        }
        if (error.response?.status === 404) {
            throw new Error('Requested resource not found');
        }
        throw error;
    }
);


// export const apiService = {
//   // Generate brand combo
//   async generateCombo(product1, product2, mode = 'competitive') {
//     try {
//       const response = await api.post('/generate', {
//         product1: product1.trim(),
//         product2: product2.trim(),
//         mode
//       })
//       return response.data
//     } catch (error) {
//       throw new Error(error.response?.data?.error || 'Failed to generate combo')
//     }
//   },

//   // Get leaderboard
//   async getLeaderboard(limit = 10) {
//     try {
//       const response = await api.get(`/leaderboard?limit=${limit}`)
//       return response.data
//     } catch (error) {
//       throw new Error(error.response?.data?.error || 'Failed to get leaderboard')
//     }
//   },

//   // Vote for combo
//   async voteForCombo(comboId) {
//     try {
//       const response = await api.post('/vote', { combo_id: comboId })
//       return response.data
//     } catch (error) {
//       throw new Error(error.response?.data?.error || 'Failed to vote')
//     }
//   },

//   // Get statistics
//   async getStats() {
//     try {
//       const response = await api.get('/stats')
//       return response.data
//     } catch (error) {
//       console.warn('Failed to get stats:', error)
//       return { totalCombos: 0, totalVotes: 0 }
//     }
//   },

//   // Health check
//   async healthCheck() {
//     try {
//       const response = await api.get('/health')
//       return response.data
//     } catch (error) {
//       throw new Error('Backend is not responding')
//     }
//   },

//   // Get service status
//   async getServiceStatus() {
//     try {
//       const response = await api.get('/health')
//       return response.data
//     } catch (error) {
//       throw new Error('Failed to get service status')
//     }
//   }
// }


// API methods
export const api = {
    async getHealth() {
        try {
            const response = await apiClient.get('/health');
            return response.data;
        } catch (error) {
            throw new Error(`Health check failed: ${error.message}`);
        }
    },
    
    async getStats() {
        try {
            const response = await apiClient.get('/stats');
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get stats: ${error.message}`);
        }
    },
    
    async getServiceStatus() {
      try {
        const response = await apiClient.get('/health')
        return response.data
      } catch (error) {
        throw new Error('Failed to get service status')
      }
    },

    // Generate brand combo
    async generateCombo(product1, product2, mode = 'competitive') {
      try {
        const response = await apiClient.post('/generate', {
          product1: product1.trim(),
          product2: product2.trim(),
          mode
        })
        return response.data
      } catch (error) {
        throw new Error(error.response?.data?.error || 'Failed to generate combo')
      }
    },

    // Get leaderboard
    async getLeaderboard(limit = 10) {
      try {
        const response = await apiClient.get(`/leaderboard?limit=${limit}`)
        return response.data
      } catch (error) {
        throw new Error(error.response?.data?.error || 'Failed to get leaderboard')
      }
    },

    // Vote for combo
    async voteForCombo(comboId) {
      try {
        const response = await apiClient.post('/vote', { combo_id: comboId })
        return response.data
      } catch (error) {
        throw new Error(error.response?.data?.error || 'Failed to vote')
      }
    },
};