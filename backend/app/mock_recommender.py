"""Recommender GIẢ để app chạy trước. Khi có lõi thật, chỉ cần giữ nguyên chữ ký 2 hàm:
    recommend(user_id, k) -> [{"song_id", "score", "reason"}]
    similar(song_id, k)   -> [{"song_id", "score", "reason"}]

Nếu bài hát có audio features (seed từ Spotify) -> gợi ý theo khoảng cách đặc trưng âm thanh;
nếu không có -> gợi ý theo thể loại.
"""
import json, math, random
from typing import Dict, List, Optional
from sqlalchemy import select, func
from .db import SessionLocal
from .models import Song, Favorite, History

FEATURE_KEYS = ["danceability", "energy", "valence", "acousticness", "instrumentalness", "speechiness", "liveness"]


def _vec(features_json: Optional[str]) -> Optional[List[float]]:
    if not features_json:
        return None
    try:
        f = json.loads(features_json)
    except ValueError:
        return None
    v = [float(f.get(k) or 0) for k in FEATURE_KEYS]
    v.append(float(f.get("tempo") or 120) / 250)  # chuẩn hóa tempo về ~[0,1]
    return v


def _dist(a: List[float], b: List[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _vectors(db, exclude=()) -> Dict[int, List[float]]:
    out = {}
    for sid, feat in db.execute(select(Song.id, Song.features).where(Song.features.is_not(None))):
        if sid not in exclude:
            v = _vec(feat)
            if v:
                out[sid] = v
    return out


def trending(k: int = 20) -> List[Dict]:
    with SessionLocal() as db:
        songs = db.scalars(select(Song).order_by(Song.play_count.desc()).limit(k)).all()
        return [{"song_id": s.id, "score": float(s.play_count), "reason": "Đang thịnh hành"} for s in songs]


def recommend(user_id: int, k: int = 20) -> List[Dict]:
    with SessionLocal() as db:
        liked = list(db.scalars(select(Favorite.song_id).where(Favorite.user_id == user_id)))
        heard = list(db.scalars(select(History.song_id).where(History.user_id == user_id)))
        seen = set(liked) | set(heard)
        if not seen:
            return trending(k)

        # 1) Có audio features: so khoảng cách tới "gu" trung bình (bài đã yêu thích tính gấp đôi)
        taste_src = {sid: v for sid, v in _vectors(db).items() if sid in seen}
        if taste_src:
            weights = [(taste_src[s], 2 if s in liked else 1) for s in taste_src]
            total = sum(w for _, w in weights)
            taste = [sum(v[i] * w for v, w in weights) / total for i in range(len(FEATURE_KEYS) + 1)]
            ranked = sorted(((_dist(v, taste), sid) for sid, v in _vectors(db, exclude=seen).items()))
            top = ranked[: k * 3]
            picked = random.sample(top, min(k, len(top)))  # xáo nhẹ để mỗi lần tải không y hệt
            picked.sort()
            return [{"song_id": sid, "score": round(1 / (1 + d), 3), "reason": "Hợp với gu nghe của bạn"} for d, sid in picked]

        # 2) Không có features: theo thể loại
        genres = db.execute(
            select(Song.genre, func.count()).where(Song.id.in_(seen)).group_by(Song.genre).order_by(func.count().desc())
        ).all()
        top_genres = [g for g, _ in genres[:3]]
        pool = db.scalars(select(Song).where(Song.genre.in_(top_genres), Song.id.not_in(seen))).all()
        random.shuffle(pool)
        return [
            {"song_id": s.id, "score": round(random.uniform(0.6, 0.99), 2), "reason": f"Vì bạn hay nghe {s.genre}"}
            for s in pool[:k]
        ]


def similar(song_id: int, k: int = 10) -> List[Dict]:
    with SessionLocal() as db:
        base = db.get(Song, song_id)
        if not base:
            return []
        base_vec = _vec(base.features)
        if base_vec:
            ranked = sorted((_dist(v, base_vec), sid) for sid, v in _vectors(db, exclude={song_id}).items())
            return [{"song_id": sid, "score": round(1 / (1 + d), 3), "reason": f"Âm thanh gần giống {base.title}"} for d, sid in ranked[:k]]
        pool = db.scalars(select(Song).where(Song.genre == base.genre, Song.id != song_id)).all()
        random.shuffle(pool)
        return [
            {"song_id": s.id, "score": round(random.uniform(0.6, 0.99), 2), "reason": f"Cùng thể loại với {base.title}"}
            for s in pool[:k]
        ]
