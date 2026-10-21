from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, or_, distinct
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import User, Song, Favorite, History
from .schemas import RegisterIn, LoginIn, HistoryIn, song_out
from .auth import hash_password, verify_password, create_token, get_current_user, get_optional_user
from . import recommender_adapter as rec

Base.metadata.create_all(engine)
app = FastAPI(title="Music Demo API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"], allow_headers=["*"],
)


# ---------- Auth ----------
@app.post("/auth/register")
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == body.email)):
        raise HTTPException(400, "Email đã tồn tại")
    u = User(email=body.email, name=body.name or body.email.split("@")[0], password_hash=hash_password(body.password))
    db.add(u); db.commit(); db.refresh(u)
    return {"token": create_token(u.id), "user": {"id": u.id, "email": u.email, "name": u.name}}


@app.post("/auth/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    u = db.scalar(select(User).where(User.email == body.email))
    if not u or not verify_password(body.password, u.password_hash):
        raise HTTPException(401, "Sai email hoặc mật khẩu")
    return {"token": create_token(u.id), "user": {"id": u.id, "email": u.email, "name": u.name}}


@app.get("/auth/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "name": user.name}


# ---------- Songs (guest dùng được) ----------
@app.get("/songs")
def list_songs(q: str = "", genre: str = "", limit: int = Query(50, le=200), offset: int = 0, db: Session = Depends(get_db)):
    stmt = select(Song)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Song.title.ilike(like), Song.artist.ilike(like), Song.album.ilike(like)))
    if genre:
        stmt = stmt.where(Song.genre == genre)
    return [song_out(s) for s in db.scalars(stmt.order_by(Song.id).limit(limit).offset(offset))]


@app.get("/genres")
def genres(db: Session = Depends(get_db)):
    return sorted(g for g in db.scalars(select(distinct(Song.genre))) if g)


@app.get("/songs/{song_id}")
def get_song(song_id: int, db: Session = Depends(get_db)):
    s = db.get(Song, song_id)
    if not s:
        raise HTTPException(404, "Không có bài này")
    return song_out(s)


# ---------- Favorites (cần đăng nhập) ----------
@app.get("/favorites")
def get_favorites(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    songs = db.scalars(
        select(Song).join(Favorite, Favorite.song_id == Song.id)
        .where(Favorite.user_id == user.id).order_by(Favorite.created_at.desc())
    )
    return [song_out(s) for s in songs]


@app.post("/favorites/{song_id}")
def add_favorite(song_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.get(Song, song_id):
        raise HTTPException(404, "Không có bài này")
    if not db.get(Favorite, (user.id, song_id)):
        db.add(Favorite(user_id=user.id, song_id=song_id)); db.commit()
    return {"ok": True}


@app.delete("/favorites/{song_id}")
def remove_favorite(song_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    f = db.get(Favorite, (user.id, song_id))
    if f:
        db.delete(f); db.commit()
    return {"ok": True}


# ---------- History ----------
@app.post("/history")
def add_history(body: HistoryIn, user: User | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    s = db.get(Song, body.song_id)
    if not s:
        raise HTTPException(404, "Không có bài này")
    s.play_count += 1  # guest cũng góp vào độ thịnh hành
    if user:
        db.add(History(user_id=user.id, song_id=body.song_id, completed=body.completed))
    db.commit()
    return {"ok": True}


@app.get("/history")
def get_history(limit: int = 50, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(
        select(Song, History.played_at).join(History, History.song_id == Song.id)
        .where(History.user_id == user.id).order_by(History.played_at.desc()).limit(limit)
    ).all()
    return [song_out(s, played_at=t.isoformat()) for s, t in rows]


# ---------- Recommendation ----------
def _hydrate(items: list[dict], db: Session) -> list[dict]:
    out = []
    for it in items:
        s = db.get(Song, it["song_id"])
        if s:
            out.append(song_out(s, score=it.get("score"), reason=it.get("reason", "")))
    return out


@app.get("/recommendations")
def recommendations(k: int = 20, user: User | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    if user:
        return {"mode": "personalized", "mock": rec.USING_MOCK, "items": _hydrate(rec.recommend(user.id, k), db)}
    return {"mode": "trending", "mock": rec.USING_MOCK, "items": _hydrate(rec.trending(k), db)}


@app.get("/similar/{song_id}")
def similar(song_id: int, k: int = 10, db: Session = Depends(get_db)):
    return _hydrate(rec.similar(song_id, k), db)
