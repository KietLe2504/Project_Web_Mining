import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../store/auth.jsx'
import SongList from '../components/SongList.jsx'

export function LoginPrompt({ text }) {
  const { openAuth } = useAuth()
  return (
    <div className="banner">
      <span>{text}</span>
      <button className="btn primary" onClick={openAuth}>Đăng nhập</button>
    </div>
  )
}

export default function Favorites() {
  const { user, favIds } = useAuth()
  const [songs, setSongs] = useState([])

  // nạp lại khi bỏ/thêm yêu thích (favIds đổi)
  useEffect(() => {
    if (user) api.favorites().then(setSongs).catch(() => {})
  }, [user, favIds.size])

  if (!user) return <LoginPrompt text="Đăng nhập để xem danh sách yêu thích của bạn." />
  return (
    <div>
      <h1>Bài hát yêu thích</h1>
      <SongList songs={songs} empty="Bạn chưa thích bài nào. Bấm ♡ ở bất kỳ bài hát nào để thêm." />
    </div>
  )
}
