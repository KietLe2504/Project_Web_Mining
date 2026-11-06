import json
from collections import Counter
from typing import Dict, List

import pandas as pd
from sqlalchemy import func, select

from app.db import SessionLocal
from app.mock_recommender import recommend as mock_recommend
from app.mock_recommender import similar as mock_similar
from app.mock_recommender import trending
from app.models import Favorite, History, Song
from mining.config import SONG_FIELDS
from mining.data import prepare_features
from mining.model_store import load_bundle

try:
    BUNDLE = load_bundle()
except FileNotFoundError as exc:
    raise ImportError(str(exc)) from exc

MODEL_WEIGHT = 0.35
AFFINITY_WEIGHT = 0.65
CACHE = {"key": None, "items": {}, "base": {}}


def genres_of(features):
    return {g for g in str(features.get("genre_ids") or "").split("|") if g}


def load_items():
    with SessionLocal() as db:
        key = db.execute(select(func.count(Song.id), func.max(Song.id))).one()
        if CACHE["key"] == tuple(key):
            return CACHE["items"], CACHE["base"]
        items = {}
        for song_id, raw in db.execute(select(Song.id, Song.features)):
            if not raw:
                continue
            try:
                features = json.loads(raw)
            except ValueError:
                continue
            if "kkbox_song_id" in features:
                items[song_id] = features
    base = score_with_model(items)
    CACHE.update(key=tuple(key), items=items, base=base)
    return items, base


def score_with_model(items):
    if not items:
        return {}
    ids = list(items)
    frame = pd.DataFrame({field: [items[i].get(field) for i in ids] for field in SONG_FIELDS})
    frame["song_length"] = pd.to_numeric(frame["song_length"], errors="coerce")
    frame["language"] = pd.to_numeric(frame["language"], errors="coerce")
    features = prepare_features(frame, BUNDLE)
    probabilities = BUNDLE["model"].predict_proba(features)[:, 1]
    low, high = float(probabilities.min()), float(probabilities.max())
    spread = high - low
    return {
        song_id: (float(p) - low) / spread if spread else 0.5
        for song_id, p in zip(ids, probabilities)
    }


def build_profile(items, liked, heard):
    artists, genres, languages = Counter(), Counter(), Counter()
    weighted = [(song_id, 2) for song_id in liked] + [(song_id, 1) for song_id in heard]
    for song_id, weight in weighted:
        features = items.get(song_id)
        if not features:
            continue
        if features.get("artist_name"):
            artists[features["artist_name"]] += weight
        for genre in genres_of(features):
            genres[genre] += weight
        if features.get("language") is not None:
            languages[features["language"]] += weight
    return artists, genres, languages


def share(counter, value):
    if not counter or value is None:
        return 0.0
    return counter.get(value, 0) / max(counter.values())


def affinity(features, profile):
    artists, genres, languages = profile
    artist_share = share(artists, features.get("artist_name"))
    genre_share = max((share(genres, g) for g in genres_of(features)), default=0.0)
    language_share = share(languages, features.get("language"))
    score = 0.5 * artist_share + 0.35 * genre_share + 0.15 * language_share
    return score, artist_share, genre_share


def recommend(user_id: int, k: int = 20) -> List[Dict]:
    with SessionLocal() as db:
        liked = list(db.scalars(select(Favorite.song_id).where(Favorite.user_id == user_id)))
        heard = list(db.scalars(select(History.song_id).where(History.user_id == user_id)))
    seen = set(liked) | set(heard)
    if not seen:
        return trending(k)

    items, base = load_items()
    if not items:
        return mock_recommend(user_id, k)

    profile = build_profile(items, liked, heard)
    ranked = []
    for song_id, features in items.items():
        if song_id in seen:
            continue
        match, artist_share, genre_share = affinity(features, profile)
        score = MODEL_WEIGHT * base[song_id] + AFFINITY_WEIGHT * match
        if artist_share > 0:
            reason = f"Vì bạn hay nghe {features.get('artist_name')}"
        elif genre_share > 0:
            reason = "Cùng thể loại bạn hay nghe"
        else:
            reason = "Mô hình dự đoán bạn sẽ nghe lại"
        ranked.append((score, song_id, reason))
    ranked.sort(key=lambda row: (-row[0], row[1]))
    return [{"song_id": sid, "score": round(score, 3), "reason": reason} for score, sid, reason in ranked[:k]]


def similar(song_id: int, k: int = 10) -> List[Dict]:
    items, _ = load_items()
    target = items.get(song_id)
    if target is None:
        return mock_similar(song_id, k)

    target_genres = genres_of(target)
    target_length = pd.to_numeric(target.get("song_length"), errors="coerce")
    ranked = []
    for other_id, features in items.items():
        if other_id == song_id:
            continue
        same_artist = bool(target.get("artist_name")) and features.get("artist_name") == target.get("artist_name")
        other_genres = genres_of(features)
        union = target_genres | other_genres
        genre_overlap = len(target_genres & other_genres) / len(union) if union else 0.0
        same_language = target.get("language") is not None and features.get("language") == target.get("language")
        other_length = pd.to_numeric(features.get("song_length"), errors="coerce")
        if pd.isna(target_length) or pd.isna(other_length):
            length_closeness = 0.0
        else:
            length_closeness = 1 - abs(target_length - other_length) / max(target_length, other_length)
        score = 0.45 * same_artist + 0.30 * genre_overlap + 0.15 * same_language + 0.10 * length_closeness
        if same_artist:
            reason = "Cùng nghệ sĩ"
        elif genre_overlap > 0:
            reason = "Cùng thể loại"
        else:
            reason = "Có nét tương đồng"
        ranked.append((score, other_id, reason))
    ranked.sort(key=lambda row: (-row[0], row[1]))
    return [{"song_id": sid, "score": round(score, 3), "reason": reason} for score, sid, reason in ranked[:k]]
