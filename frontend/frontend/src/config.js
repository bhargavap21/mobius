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
export const WS_URL = API_URL.replace(/^http/, 'ws')

console.log('API Configuration:', { API_URL, WS_URL })
