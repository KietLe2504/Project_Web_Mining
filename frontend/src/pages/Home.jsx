import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { useAuth } from '../store/auth.jsx'
import { usePlayer } from '../store/player.jsx'
import { Shelf } from '../components/SongCard.jsx'
import SongList from '../components/SongList.jsx'

export default function Home() {
  const { user, openAuth } = useAuth()
  const { song } = usePlayer()
  const [rec, setRec] = useState(null)
  const [all, setAll] = useState([])
  const [similar, setSimilar] = useState([])
  const [error, setError] = useState('')

  // Gợi ý: personalized nếu đã đăng nhập, trending nếu là guest
  useEffect(() => {
    setRec(null)
    api.recommendations(20).then(setRec).catch(() => setError('Không kết nối được backend (http://localhost:8000). Đã chạy uvicorn chưa?'))
  }, [user?.id])

  useEffect(() => { api.songs({ limit: 60 }).then(setAll).catch(() => {}) }, [])

  // "Bài tương tự" bám theo bài đang phát
  useEffect(() => {
    if (!song) { setSimilar([]); return }
    api.similar(song.id, 10).then(setSimilar).catch(() => setSimilar([]))
  }, [song?.id])

  const personalized = rec?.mode === 'personalized'

  return (
    <div>
      {error && <div className="error banner">{error}</div>}

      {!user && (
        <div className="banner">
          <span>Bạn đang nghe với tư cách khách. Đăng nhập để có gợi ý riêng, lưu yêu thích và lịch sử nghe.</span>
          <button className="btn primary" onClick={openAuth}>Đăng nhập</button>
        </div>
      )}

      {rec && (
        <Shelf
          title={personalized ? '★ Gợi ý cho bạn' : '🔥 Đang thịnh hành'}
          subtitle={rec.mock ? 'Đang dùng recommender giả (mock)' : personalized ? 'Dựa trên những gì bạn đã nghe và yêu thích' : undefined}
          songs={rec.items}
        />
      )}

      {song && <Shelf title={`Giống "${song.title}"`} subtitle="Bài tương tự với bài đang phát" songs={similar} />}

      <section className="shelf">
        <h2>Tất cả bài hát</h2>
        <SongList songs={all} />
      </section>
    </div>
  )
}
