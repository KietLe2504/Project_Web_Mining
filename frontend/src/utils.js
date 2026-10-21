export function fmt(sec) {
  sec = Math.max(0, Math.floor(sec || 0))
  return `${Math.floor(sec / 60)}:${String(sec % 60).padStart(2, '0')}`
}
