"""Seed DB.

  python -m scripts.seed_db --spotify dataset.csv            # Spotify Tracks Dataset (Kaggle)
  python -m scripts.seed_db --spotify dataset.csv --per-genre 60
  python -m scripts.seed_db --csv songs.csv                  # CSV tự chuẩn bị: title,artist,album,genre,duration,audio_url,cover_url
  python -m scripts.seed_db                                  # ~240 bài giả để thử nhanh

Spotify CSV: tự dò tên cột (track_id, track_name/name, artists, album_name, track_genre, duration_ms,
popularity, danceability, energy, valence, ...). Mỗi thể loại lấy top --per-genre bài theo popularity,
loại trùng theo track_id. Dataset này không có audio/cover -> player mô phỏng + ảnh bìa gradient.
Đổi schema/đổi nguồn dữ liệu: xóa file music.db rồi seed lại.
"""
import argparse, csv, json, random
from collections import defaultdict
from app.db import Base, engine, SessionLocal
from app.models import Song

FEATURE_KEYS = ["danceability", "energy", "valence", "acousticness", "instrumentalness",
                "speechiness", "liveness", "tempo", "loudness"]


def first(row, *keys, default=""):
    for k in keys:
        v = row.get(k)
        if v not in (None, ""):
            return v
    return default


def spotify_rows(path, per_genre):
    seen, by_genre = set(), defaultdict(list)
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            tid = first(r, "track_id", "id", "uri")
            if tid and tid in seen:
                continue
            seen.add(tid)
            title = first(r, "track_name", "name", "title")
            if not title:
                continue
            feats = {}
            for k in FEATURE_KEYS:
                try:
                    feats[k] = float(r[k])
                except (KeyError, ValueError, TypeError):
                    pass
            genre = str(first(r, "track_genre", "genre", "playlist_genre", default="unknown")).title()
            try:
                dur = int(float(first(r, "duration_ms", default=0)) / 1000) or 180
            except ValueError:
                dur = 180
            try:
                pop = int(float(first(r, "popularity", default=0)))
            except ValueError:
                pop = 0
            by_genre[genre].append(dict(
                spotify_id=tid or None, title=title,
                artist=str(first(r, "artists", "artist", "artist_name")).replace(";", ", "),
                album=first(r, "album_name", "album", "track_album_name"),
                genre=genre, duration=dur, audio_url=None, cover_url=None,
                play_count=pop, features=json.dumps(feats) if feats else None,
            ))
    for genre, rows in by_genre.items():
        rows.sort(key=lambda x: x["play_count"], reverse=True)
        yield from rows[:per_genre]


def csv_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            yield dict(title=r["title"], artist=r.get("artist", ""), album=r.get("album", ""),
                       genre=r.get("genre", ""), duration=int(float(r.get("duration") or 180)),
                       audio_url=r.get("audio_url") or None, cover_url=r.get("cover_url") or None,
                       play_count=random.randint(0, 500))


GENRES = ["Pop", "Rock", "Hip-Hop", "Electronic", "Jazz", "Classical", "Folk", "R&B"]
ADJ = ["Midnight", "Golden", "Lonely", "Electric", "Silent", "Neon", "Broken", "Summer", "Paper", "Velvet"]
NOUN = ["Dreams", "City", "Heart", "Rain", "Road", "Fire", "Ocean", "Echo", "Garden", "Skyline"]
ARTISTS = [f"Artist {c}" for c in "ABCDEFGHIJKLMNOP"]


def fake_rows(n=240):
    for i in range(n):
        a = random.choice(ARTISTS)
        yield dict(title=f"{random.choice(ADJ)} {random.choice(NOUN)} #{i+1}", artist=a,
                   album=f"{a} - Vol.{random.randint(1,4)}", genre=GENRES[i % len(GENRES)],
                   duration=random.randint(150, 300), audio_url=None, cover_url=None,
                   play_count=random.randint(0, 500))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--spotify", help="đường dẫn Spotify Tracks CSV")
    ap.add_argument("--per-genre", type=int, default=40, help="số bài tối đa mỗi thể loại (Spotify)")
    ap.add_argument("--csv", help="CSV tự chuẩn bị")
    args = ap.parse_args()

    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.query(Song).count():
            print("DB đã có bài hát, bỏ qua seed. (Muốn seed lại: xóa music.db)")
            raise SystemExit
        if args.spotify:
            rows = spotify_rows(args.spotify, args.per_genre)
        elif args.csv:
            rows = csv_rows(args.csv)
        else:
            rows = fake_rows()
        db.add_all(Song(**r) for r in rows)
        db.commit()
        print("Đã seed:", db.query(Song).count(), "bài")
