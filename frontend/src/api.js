const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

let token = localStorage.getItem('token') || null
export function setToken(t) {
  token = t
  if (t) localStorage.setItem('token', t)
  else localStorage.removeItem('token')
}

async function req(path, { method = 'GET', body } = {}) {
  const res = await fetch(BASE + path, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    let msg = 'Có lỗi xảy ra'
    try { msg = (await res.json()).detail || msg } catch {}
    const err = new Error(msg)
    err.status = res.status
    throw err
  }
  return res.json()
}

export const api = {
  register: (email, password, name) => req('/auth/register', { method: 'POST', body: { email, password, name } }),
  login: (email, password) => req('/auth/login', { method: 'POST', body: { email, password } }),
  me: () => req('/auth/me'),
  songs: ({ q = '', genre = '', limit = 50 } = {}) =>
    req(`/songs?q=${encodeURIComponent(q)}&genre=${encodeURIComponent(genre)}&limit=${limit}`),
  genres: () => req('/genres'),
  favorites: () => req('/favorites'),
  addFavorite: (id) => req(`/favorites/${id}`, { method: 'POST' }),
  removeFavorite: (id) => req(`/favorites/${id}`, { method: 'DELETE' }),
  history: () => req('/history'),
  addHistory: (song_id, completed = false) => req('/history', { method: 'POST', body: { song_id, completed } }),
  recommendations: (k = 20) => req(`/recommendations?k=${k}`),
  similar: (id, k = 10) => req(`/similar/${id}?k=${k}`),
}
