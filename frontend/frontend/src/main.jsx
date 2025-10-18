import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import EmailConfirmation from './components/EmailConfirmation.jsx'
import CommunityPage from './pages/CommunityPage.jsx'
import { AuthProvider, useAuth } from './context/AuthContext.jsx'

function CommunityPageWrapper() {
  const { user, isAuthenticated } = useAuth()
  return <CommunityPage userAgents={[]} isAuthenticated={isAuthenticated} />
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/community" element={<CommunityPageWrapper />} />
          <Route path="/auth/confirm" element={<EmailConfirmation />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
