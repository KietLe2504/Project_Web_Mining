import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { api, setToken } from '../api.js'

const AuthCtx = createContext(null)
export const useAuth = () => useContext(AuthCtx)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [favIds, setFavIds] = useState(new Set())
  const [authOpen, setAuthOpen] = useState(false)

  // Khôi phục phiên đăng nhập
  useEffect(() => {
    if (!localStorage.getItem('token')) return
    api.me().then(setUser).catch(() => setToken(null))
  }, [])

  // Nạp danh sách yêu thích khi đăng nhập
  useEffect(() => {
    if (!user) { setFavIds(new Set()); return }
    api.favorites().then((list) => setFavIds(new Set(list.map((s) => s.id)))).catch(() => {})
  }, [user])

  const handleAuth = useCallback(async (mode, { email, password, name }) => {
    const res = mode === 'login' ? await api.login(email, password) : await api.register(email, password, name)
    setToken(res.token)
    setUser(res.user)
    setAuthOpen(false)
  }, [])

  const logout = useCallback(() => { setToken(null); setUser(null) }, [])

  const toggleFavorite = useCallback(async (song) => {
    if (!user) { setAuthOpen(true); return }
    const isFav = favIds.has(song.id)
    setFavIds((prev) => {
      const next = new Set(prev)
      isFav ? next.delete(song.id) : next.add(song.id)
      return next
    })
    try {
      isFav ? await api.removeFavorite(song.id) : await api.addFavorite(song.id)
    } catch {
      setFavIds((prev) => {  // hoàn tác nếu lỗi
        const next = new Set(prev)
        isFav ? next.add(song.id) : next.delete(song.id)
        return next
      })
    }
  }, [user, favIds])

  return (
    <AuthCtx.Provider value={{ user, favIds, toggleFavorite, handleAuth, logout, authOpen, openAuth: () => setAuthOpen(true), closeAuth: () => setAuthOpen(false) }}>
      {children}
    </AuthCtx.Provider>
  )
}
