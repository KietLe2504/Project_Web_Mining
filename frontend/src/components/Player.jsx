import Cover from './Cover.jsx'
import { usePlayer } from '../store/player.jsx'
import { useAuth } from '../store/auth.jsx'
import { fmt } from '../utils.js'

export default function Player() {
  const { song, playing, progress, speed, shuffle, togglePlay, next, prev, seek, setSpeed, setShuffle } = usePlayer()
  const { favIds, toggleFavorite } = useAuth()

  if (!song) {
    return <footer className="player empty"><span className="muted">Chọn một bài hát để bắt đầu nghe</span></footer>
  }
  const pct = Math.min(100, (progress / song.duration) * 100)

  return (
    <footer className="player">
      <div className="player-left">
        <Cover song={song} size={56} />
        <div className="player-info">
          <div className="row-title">{song.title}</div>
          <div className="muted small">{song.artist}</div>
        </div>
        <button className={'heart' + (favIds.has(song.id) ? ' on' : '')} onClick={() => toggleFavorite(song)} aria-label="Yêu thích">
          {favIds.has(song.id) ? '♥' : '♡'}
        </button>
      </div>

      <div className="player-center">
        <div className="controls">
          <button className={'ctl' + (shuffle ? ' on' : '')} onClick={() => setShuffle(!shuffle)} title="Ngẫu nhiên">⤮</button>
          <button className="ctl" onClick={prev} title="Bài trước">⏮</button>
          <button className="ctl play" onClick={togglePlay}>{playing ? '⏸' : '▶'}</button>
          <button className="ctl" onClick={next} title="Bài kế tiếp">⏭</button>
          <button className={'ctl speed' + (speed > 1 ? ' on' : '')} onClick={() => setSpeed(speed === 1 ? 5 : 1)} title="Tua nhanh thời gian mô phỏng (demo)">
            x{speed}
          </button>
        </div>
        <div className="progress-wrap">
          <span className="muted small">{fmt(progress)}</span>
          <div className="bar" onClick={(e) => { const r = e.currentTarget.getBoundingClientRect(); seek((e.clientX - r.left) / r.width) }}>
            <div className="bar-fill" style={{ width: pct + '%' }} />
          </div>
          <span className="muted small">{fmt(song.duration)}</span>
        </div>
      </div>

      <div className="player-right muted small">{playing ? 'Đang phát (mô phỏng)' : 'Tạm dừng'}</div>
    </footer>
  )
}
