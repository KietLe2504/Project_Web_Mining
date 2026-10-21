import { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react'
import { api } from '../api.js'

/*
 * PLAYER MÔ PHỎNG
 * - Trạng thái phát (queue, tiến độ, auto-next) do app tự điều khiển bằng timer,
 *   không phụ thuộc file audio có load được hay không.
 * - <audio> chỉ là lớp âm thanh bám theo (nếu bài có audio_url).
 * - Nút "x5" tua nhanh thời gian mô phỏng để demo khỏi chờ.
 */
const PlayerCtx = createContext(null)
export const usePlayer = () => useContext(PlayerCtx)

const TICK_MS = 250

export function PlayerProvider({ children }) {
  const [queue, setQueue] = useState([])
  const [index, setIndex] = useState(-1)
  const [playing, setPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [speed, setSpeed] = useState(1)
  const [shuffle, setShuffle] = useState(false)

  const audioRef = useRef(null)
  const loggedRef = useRef(false)
  const song = index >= 0 ? queue[index] : null

  const goTo = useCallback((i) => {
    setIndex(i)
    setProgress(0)
    loggedRef.current = false
  }, [])

  const next = useCallback(() => {
    if (!queue.length) return
    let i = index + 1
    if (shuffle && queue.length > 1) {
      do { i = Math.floor(Math.random() * queue.length) } while (i === index)
    }
    goTo(i % queue.length)
  }, [queue, index, shuffle, goTo])

  const prev = useCallback(() => {
    if (!queue.length) return
    if (progress > 3) { setProgress(0); if (audioRef.current) audioRef.current.currentTime = 0; return }
    goTo((index - 1 + queue.length) % queue.length)
  }, [queue, index, progress, goTo])

  const playList = useCallback((songs, startIndex = 0) => {
    setQueue(songs)
    goTo(startIndex)
    setPlaying(true)
  }, [goTo])

  const togglePlay = useCallback(() => { if (song) setPlaying((p) => !p) }, [song])

  const seek = useCallback((ratio) => {
    if (!song) return
    const t = Math.max(0, Math.min(1, ratio)) * song.duration
    setProgress(t)
    if (audioRef.current && audioRef.current.src) audioRef.current.currentTime = t
  }, [song])

  // Đổi bài -> nạp audio (nếu có)
  useEffect(() => {
    const a = audioRef.current
    if (!a) return
    if (song?.audio_url) {
      a.src = song.audio_url
      a.currentTime = 0
      if (playing) a.play().catch(() => {})
    } else {
      a.pause()
      a.removeAttribute('src')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [song?.id])

  // Play / pause audio theo trạng thái mô phỏng
  useEffect(() => {
    const a = audioRef.current
    if (!a || !a.src) return
    if (playing) a.play().catch(() => {})
    else a.pause()
  }, [playing, song?.id])

  // Tắt tiếng khi tua nhanh
  useEffect(() => { if (audioRef.current) audioRef.current.muted = speed > 1 }, [speed])

  // Timer mô phỏng
  useEffect(() => {
    if (!playing || !song) return
    const id = setInterval(() => setProgress((p) => p + (TICK_MS / 1000) * speed), TICK_MS)
    return () => clearInterval(id)
  }, [playing, song?.id, speed])

  // Hết bài -> bài kế tiếp
  useEffect(() => {
    if (song && progress >= song.duration) next()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [progress, song?.duration])

  // Ghi lịch sử nghe 1 lần mỗi lượt phát (qua 10s hoặc 50% bài)
  useEffect(() => {
    if (!song || loggedRef.current) return
    if (progress >= Math.min(10, song.duration * 0.5)) {
      loggedRef.current = true
      api.addHistory(song.id).catch(() => {})
    }
  }, [progress, song])

  return (
    <PlayerCtx.Provider value={{ queue, index, song, playing, progress, speed, shuffle, playList, togglePlay, next, prev, seek, setSpeed, setShuffle }}>
      {children}
      <audio ref={audioRef} preload="auto" />
    </PlayerCtx.Provider>
  )
}
