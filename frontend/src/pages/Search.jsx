import { useEffect, useState } from 'react'
import { api } from '../api.js'
import SongList from '../components/SongList.jsx'

export default function Search() {
  const [q, setQ] = useState('')
  const [genre, setGenre] = useState('')
  const [genres, setGenres] = useState([])
  const [songs, setSongs] = useState([])

  useEffect(() => { api.genres().then(setGenres).catch(() => {}) }, [])

  // debounce 300ms
  useEffect(() => {
    const t = setTimeout(() => { api.songs({ q, genre, limit: 100 }).then(setSongs).catch(() => setSongs([])) }, 300)
    return () => clearTimeout(t)
  }, [q, genre])

  return (
    <div>
      <input className="search-input" placeholder="Tìm bài hát, nghệ sĩ, album..." value={q} onChange={(e) => setQ(e.target.value)} autoFocus />
      <div className="chips">
        <button className={'chip' + (genre === '' ? ' on' : '')} onClick={() => setGenre('')}>Tất cả</button>
        {genres.map((g) => (
          <button key={g} className={'chip' + (genre === g ? ' on' : '')} onClick={() => setGenre(g)}>{g}</button>
        ))}
      </div>
      <SongList songs={songs} empty="Không tìm thấy kết quả." />
    </div>
  )
}
