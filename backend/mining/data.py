import numpy as np
import pandas as pd

from .config import (
    DATA_DIR,
    DATE_COLUMNS,
    DROP_COLUMNS,
    ID_COLUMNS,
    TARGET,
    UNKNOWN,
)


def load_table(name, nrows=None):
    path = DATA_DIR / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Extract the KKBox .csv files into {DATA_DIR} "
            "or set KKBOX_DATA_DIR."
        )
    return pd.read_csv(path, nrows=nrows)


def merge_tables(interactions, songs, members):
    merged = interactions.merge(songs, on="song_id", how="left")
    return merged.merge(members, on="msno", how="left")


def load_training_frame(nrows=None):
    train = load_table("train", nrows)
    songs = load_table("songs")
    members = load_table("members")
    return merge_tables(train, songs, members)


def fill_missing(df):
    frame = df.copy()
    for col in frame.select_dtypes(include="O").columns:
        frame[col] = frame[col].fillna(UNKNOWN)
    numeric = frame.select_dtypes(include=np.number).columns
    frame[numeric] = frame[numeric].interpolate(method="linear", limit_direction="both")
    return frame


def compute_defaults(df):
    defaults = {}
    for col in df.columns:
        if col in ID_COLUMNS or col == TARGET:
            continue
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            defaults[col] = float(series.median())
        else:
            defaults[col] = str(series.mode().iloc[0])
    return defaults


def fill_with_defaults(df, defaults):
    frame = df.copy()
    for col, default in defaults.items():
        if col not in frame.columns:
            frame[col] = default
        elif isinstance(default, str):
            frame[col] = frame[col].fillna(UNKNOWN)
        else:
            frame[col] = frame[col].fillna(default)
    return frame


def expand_dates(df):
    frame = df.copy()
    for col in DATE_COLUMNS:
        text = frame[col].round().astype("int64").astype(str)
        parsed = pd.to_datetime(text, format="%Y%m%d", errors="coerce")
        frame[f"{col}_day"] = parsed.dt.day.fillna(0).astype("int64")
        frame[f"{col}_month"] = parsed.dt.month.fillna(0).astype("int64")
        frame[f"{col}_year"] = parsed.dt.year.fillna(0).astype("int64")
    return frame


def select_feature_columns(df):
    return [c for c in df.columns if c not in DROP_COLUMNS and c != TARGET]


def fit_encoders(df, columns):
    encoders = {}
    for col in columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            classes = sorted(df[col].astype(str).unique())
            encoders[col] = {value: index for index, value in enumerate(classes)}
    return encoders


def apply_encoders(df, encoders):
    frame = df.copy()
    for col, mapping in encoders.items():
        frame[col] = frame[col].astype(str).map(mapping).fillna(-1).astype("int64")
    return frame


def prepare_features(df, bundle):
    frame = fill_with_defaults(df, bundle["defaults"])
    frame = expand_dates(frame)
    frame = frame[bundle["feature_columns"]]
    return apply_encoders(frame, bundle["encoders"])
