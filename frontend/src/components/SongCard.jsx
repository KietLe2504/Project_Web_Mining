import Cover from './Cover.jsx'
import { usePlayer } from '../store/player.jsx'

export function Shelf({ title, subtitle, songs }) {
  const { playList, song: current } = usePlayer()
  if (!songs?.length) return null
  return (
    <section className="shelf">
      <h2>{title}</h2>
      {subtitle && <p className="muted">{subtitle}</p>}
      <div className="shelf-row">
        {songs.map((s, i) => (
          <button key={s.id} className={'card' + (current?.id === s.id ? ' active' : '')} onClick={() => playList(songs, i)} title={s.reason || ''}>
            <Cover song={s} size={150} radius={8} />
            <div className="card-title">{s.title}</div>
            <div className="card-sub">{s.reason || s.artist}</div>
          </button>
        ))}
      </div>
    </section>
  )
}
