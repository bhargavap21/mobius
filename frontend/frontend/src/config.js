// Environment configuration
const getApiUrl = () => {
  // Use environment variable if set, otherwise default to localhost
  const envUrl = import.meta.env.VITE_API_URL

  if (envUrl) {
    return envUrl
  }

  // Default for local development
  return 'http://localhost:8000'
}

export const API_URL = getApiUrl()

// WebSocket URL (derived from API URL)
// Properly handles both http→ws and https→wss conversions
const getWsUrl = () => {
  const apiUrl = getApiUrl()
  if (apiUrl.startsWith('https')) {
    return apiUrl.replace(/^https/, 'wss')
  }
  return apiUrl.replace(/^http/, 'ws')
}

export const WS_URL = getWsUrl()

console.log('API Configuration:', { API_URL, WS_URL })
