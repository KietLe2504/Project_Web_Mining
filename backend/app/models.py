from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, default="")
    password_hash: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Song(Base):
    __tablename__ = "songs"
    id: Mapped[int] = mapped_column(primary_key=True)
    spotify_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    artist: Mapped[str] = mapped_column(String, index=True)
    album: Mapped[str] = mapped_column(String, default="")
    genre: Mapped[str] = mapped_column(String, index=True, default="")
    duration: Mapped[int] = mapped_column(Integer, default=180)  # giây
    audio_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cover_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    play_count: Mapped[int] = mapped_column(Integer, default=0)  # với Spotify: = popularity (0-100)
    features: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # JSON: danceability, energy, valence, tempo...


class Favorite(Base):
    __tablename__ = "favorites"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class History(Base):
    __tablename__ = "listen_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"))
    played_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
