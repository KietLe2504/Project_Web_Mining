"""Seed DB.

  python -m scripts.seed_db --spotify dataset.csv            # Spotify Tracks Dataset (Kaggle)
  python -m scripts.seed_db --spotify dataset.csv --per-genre 60
  python -m scripts.seed_db --csv songs.csv                  # CSV tự chuẩn bị: title,artist,album,genre,duration,audio_url,cover_url
  python -m scripts.seed_db --kkbox ../data                  # KKBox (songs.csv, song_extra_info.csv, train.csv)
  python -m scripts.seed_db                                  # ~240 bài giả để thử nhanh

Spotify CSV: tự dò tên cột (track_id, track_name/name, artists, album_name, track_genre, duration_ms,
popularity, danceability, energy, valence, ...). Mỗi thể loại lấy top --per-genre bài theo popularity,
loại trùng theo track_id. Dataset này không có audio/cover -> player mô phỏng + ảnh bìa gradient.
Đổi schema/đổi nguồn dữ liệu: xóa file music.db rồi seed lại.
"""
import argparse, csv, json, random
from collections import defaultdict
from pathlib import Path
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


def clean(value):
    if value is None:
        return None
    try:
        if value != value:
            return None
    except (TypeError, ValueError):
        return None
    if hasattr(value, "item"):
        value = value.item()
    return value


def kkbox_rows(data_dir, n_songs, nrows):
    import pandas as pd

    base = Path(data_dir)
    train = pd.read_csv(base / "train.csv", usecols=["song_id"], nrows=nrows)
    counts = train["song_id"].value_counts().head(n_songs)
    songs = pd.read_csv(base / "songs.csv")
    songs = songs[songs["song_id"].isin(counts.index)].set_index("song_id").to_dict("index")
    names = {}
    extra_path = base / "song_extra_info.csv"
    if extra_path.exists():
        extra = pd.read_csv(extra_path)
        extra = extra[extra["song_id"].isin(counts.index)]
        names = dict(zip(extra["song_id"], extra["name"]))
    for song_id, plays in counts.items():
        info = songs.get(song_id)
        if info is None:
            continue
        genre_ids = clean(info.get("genre_ids"))
        first_genre = str(genre_ids).split("|")[0] if genre_ids else ""
        length_ms = clean(info.get("song_length"))
        language = clean(info.get("language"))
        features = {
            "kkbox_song_id": song_id,
            "song_length": length_ms,
            "genre_ids": genre_ids,
            "artist_name": clean(info.get("artist_name")),
            "composer": clean(info.get("composer")),
            "lyricist": clean(info.get("lyricist")),
            "language": int(language) if language is not None else None,
        }
        yield dict(
            spotify_id=song_id,
            title=clean(names.get(song_id)) or f"Song {song_id[:6]}",
            artist=features["artist_name"] or "Unknown",
            album="",
            genre=f"Genre {first_genre}" if first_genre else "Unknown",
            duration=int(length_ms / 1000) if length_ms else 180,
            audio_url=None, cover_url=None,
            play_count=int(plays), features=json.dumps(features),
        )


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
    ap.add_argument("--kkbox", help="thư mục chứa dữ liệu KKBox (songs.csv, train.csv, ...)")
    ap.add_argument("--kkbox-songs", type=int, default=3000, help="số bài KKBox được nghe nhiều nhất để nạp")
    ap.add_argument("--kkbox-nrows", type=int, default=2000000, help="số dòng train.csv dùng để đếm lượt nghe (0 = tất cả)")
    args = ap.parse_args()

    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.query(Song).count():
            print("DB đã có bài hát, bỏ qua seed. (Muốn seed lại: xóa music.db)")
            raise SystemExit
        if args.kkbox:
            rows = kkbox_rows(args.kkbox, args.kkbox_songs, args.kkbox_nrows or None)
        elif args.spotify:
            rows = spotify_rows(args.spotify, args.per_genre)
        elif args.csv:
            rows = csv_rows(args.csv)
        else:
            rows = fake_rows()
        db.add_all(Song(**r) for r in rows)
        db.commit()
        print("Đã seed:", db.query(Song).count(), "bài")
