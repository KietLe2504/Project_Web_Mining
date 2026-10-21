from pydantic import BaseModel


class RegisterIn(BaseModel):
    email: str
    password: str
    name: str = ""


class LoginIn(BaseModel):
    email: str
    password: str


class HistoryIn(BaseModel):
    song_id: int
    completed: bool = False


def song_out(s, **extra) -> dict:
    return {
        "id": s.id, "title": s.title, "artist": s.artist, "album": s.album,
        "genre": s.genre, "duration": s.duration,
        "audio_url": s.audio_url, "cover_url": s.cover_url, **extra,
    }
