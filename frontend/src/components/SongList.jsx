import Cover from './Cover.jsx'
import { usePlayer } from '../store/player.jsx'
import { useAuth } from '../store/auth.jsx'
import { fmt } from '../utils.js'

export default function SongList({ songs, empty = 'Không có bài hát nào.' }) {
  const { playList, song: current } = usePlayer()
  const { favIds, toggleFavorite } = useAuth()
  if (!songs.length) return <p className="muted">{empty}</p>
  return (
    <div className="list">
      {songs.map((s, i) => (
        <div key={s.id} className={'row' + (current?.id === s.id ? ' active' : '')} onClick={() => playList(songs, i)}>
          <span className="row-idx">{i + 1}</span>
          <Cover song={s} size={40} radius={4} />
          <div className="row-main">
            <div className="row-title">{s.title}</div>
            <div className="muted small">{s.artist}</div>
          </div>
          <span className="row-album muted small">{s.album}</span>
          <span className="tag">{s.genre}</span>
          <button className={'heart' + (favIds.has(s.id) ? ' on' : '')} onClick={(e) => { e.stopPropagation(); toggleFavorite(s) }} aria-label="Yêu thích">
            {favIds.has(s.id) ? '♥' : '♡'}
          </button>
          <span className="muted small row-dur">{fmt(s.duration)}</span>
        </div>
      ))}
    </div>
  )
}
