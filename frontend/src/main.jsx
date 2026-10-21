import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import { AuthProvider } from './store/auth.jsx'
import { PlayerProvider } from './store/player.jsx'
import './styles.css'

createRoot(document.getElementById('root')).render(
  <AuthProvider>
    <PlayerProvider>
      <App />
    </PlayerProvider>
  </AuthProvider>
)
