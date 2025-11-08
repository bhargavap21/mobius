import { StrictMode, useState, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import EmailConfirmation from './components/EmailConfirmation.jsx'
import CommunityPage from './pages/CommunityPage.jsx'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'
import { API_URL } from './config'

function CommunityPageWrapper() {
  const { user, isAuthenticated, getAuthHeaders } = useAuth()
  const [userAgents, setUserAgents] = useState([])
  const [loadingBots, setLoadingBots] = useState(false)

  useEffect(() => {
    const loadUserBots = async () => {
      if (!isAuthenticated) {
        setUserAgents([])
        return
      }

      setLoadingBots(true)
      try {
        const response = await fetch(`${API_URL}/bots?page=1&page_size=50`, {
          headers: getAuthHeaders()
        })

        if (response.ok) {
          const data = await response.json()
          const botList = data.items || []
          
          // Transform bot data to match what ShareAgentForm expects
          const transformedBots = botList.map(bot => ({
            id: bot.id,
            name: bot.name,
            description: bot.description,
            strategy: bot.strategy_config,
            backtest_results: bot.backtest_results,
            totalReturn: bot.backtest_results?.summary?.total_return ?? null,
            winRate: bot.backtest_results?.summary?.win_rate || 0,
            totalTrades: bot.backtest_results?.summary?.total_trades || 0,
            symbol: bot.strategy_config?.asset || 'Unknown'
          }))


          setUserAgents(transformedBots)
          console.log('Loaded user bots for community sharing:', transformedBots.length)
        } else {
          console.error('Failed to load user bots:', response.status)
          setUserAgents([])
        }
      } catch (error) {
        console.error('Error loading user bots:', error)
        setUserAgents([])
      } finally {
        setLoadingBots(false)
      }
    }

    loadUserBots()
  }, [isAuthenticated, getAuthHeaders])

  return <CommunityPage userAgents={userAgents} isAuthenticated={isAuthenticated} loadingBots={loadingBots} />
}

createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <AuthProvider>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/community" element={<CommunityPageWrapper />} />
        <Route path="/auth/confirm" element={<EmailConfirmation />} />
      </Routes>
    </AuthProvider>
  </BrowserRouter>,
)
