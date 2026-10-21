import { useState } from 'react'
import { useAuth } from './store/auth.jsx'
import Sidebar from './components/Sidebar.jsx'
import Player from './components/Player.jsx'
import AuthModal from './components/AuthModal.jsx'
import Home from './pages/Home.jsx'
import Search from './pages/Search.jsx'
import Favorites from './pages/Favorites.jsx'
import History from './pages/History.jsx'

const PAGES = { home: Home, search: Search, favorites: Favorites, history: History }

export default function App() {
  const [page, setPage] = useState('home')
  const { user, logout, openAuth, authOpen } = useAuth()
  const Page = PAGES[page]

  return (
    <div className="app">
      <Sidebar page={page} setPage={setPage} user={user} />
      <main className="main">
        <div className="topbar">
          {user ? (
            <>
              <span className="avatar">{(user.name || user.email)[0].toUpperCase()}</span>
              <span className="small">{user.name || user.email}</span>
              <button className="btn" onClick={logout}>Đăng xuất</button>
            </>
          ) : (
            <button className="btn primary" onClick={openAuth}>Đăng nhập</button>
          )}
        </div>
        <Page />
      </main>
      <Player />
      {authOpen && <AuthModal />}
    </div>
  )
}
