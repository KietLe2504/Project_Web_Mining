const ITEMS = [
  { id: 'home', label: 'Trang chủ', icon: '⌂' },
  { id: 'search', label: 'Tìm kiếm', icon: '⌕' },
  { id: 'favorites', label: 'Yêu thích', icon: '♥', auth: true },
  { id: 'history', label: 'Lịch sử nghe', icon: '↺', auth: true },
]

export default function Sidebar({ page, setPage, user }) {
  return (
    <aside className="sidebar">
      <div className="logo">♫ MusicDemo</div>
      <nav>
        {ITEMS.map((it) => (
          <button key={it.id} className={'nav' + (page === it.id ? ' active' : '')} onClick={() => setPage(it.id)}>
            <span className="nav-icon">{it.icon}</span>
            {it.label}
            {it.auth && !user && <span className="lock">🔒</span>}
          </button>
        ))}
      </nav>
    </aside>
  )
}
