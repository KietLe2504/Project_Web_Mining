export default function Cover({ song, size = 48, radius = 6 }) {
  const style = { width: size, height: size, borderRadius: radius, flexShrink: 0 }
  if (song?.cover_url) return <img src={song.cover_url} alt="" style={{ ...style, objectFit: 'cover' }} />
  const h = ((song?.id || 0) * 47) % 360
  return (
    <div
      style={{ ...style, background: `linear-gradient(135deg, hsl(${h} 65% 45%), hsl(${(h + 60) % 360} 70% 30%))`, display: 'grid', placeItems: 'center', color: 'rgba(255,255,255,.85)', fontWeight: 700, fontSize: size * 0.4 }}
    >
      {(song?.title || '?')[0]}
    </div>
  )
}
