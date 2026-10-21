import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../store/auth.jsx'
import SongList from '../components/SongList.jsx'
import { LoginPrompt } from './Favorites.jsx'

export default function History() {
  const { user } = useAuth()
  const [songs, setSongs] = useState([])

  useEffect(() => {
    if (user) api.history().then(setSongs).catch(() => {})
  }, [user])

  if (!user) return <LoginPrompt text="Đăng nhập để xem lịch sử nghe của bạn." />
  return (
    <div>
      <h1>Lịch sử nghe</h1>
      <SongList songs={songs} empty="Chưa có lịch sử. Nghe một bài quá 10 giây (hoặc bấm x5) để được ghi lại." />
    </div>
  )
}
