import { useState } from 'react'
import { useAuth } from '../store/auth.jsx'

export default function AuthModal() {
  const { handleAuth, closeAuth } = useAuth()
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setError(''); setBusy(true)
    try { await handleAuth(mode, { email, password, name }) }
    catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }

  return (
    <div className="modal-bg" onClick={closeAuth}>
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={submit}>
        <h2>{mode === 'login' ? 'Đăng nhập' : 'Tạo tài khoản'}</h2>
        <p className="muted small">Đăng nhập để lưu yêu thích, lịch sử nghe và nhận gợi ý riêng cho bạn.</p>
        {mode === 'register' && <input placeholder="Tên hiển thị" value={name} onChange={(e) => setName(e.target.value)} />}
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input type="password" placeholder="Mật khẩu" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={4} />
        {error && <div className="error">{error}</div>}
        <button className="btn primary" disabled={busy}>{busy ? '...' : mode === 'login' ? 'Đăng nhập' : 'Đăng ký'}</button>
        <button type="button" className="link" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}>
          {mode === 'login' ? 'Chưa có tài khoản? Đăng ký' : 'Đã có tài khoản? Đăng nhập'}
        </button>
      </form>
    </div>
  )
}
