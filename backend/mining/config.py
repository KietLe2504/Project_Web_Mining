import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent
DATA_DIR = Path(os.environ.get("KKBOX_DATA_DIR", ROOT_DIR / "data"))
ARTIFACT_DIR = Path(os.environ.get("ARTIFACT_DIR", BACKEND_DIR / "artifacts"))
MODEL_PATH = ARTIFACT_DIR / "model.joblib"
RESULTS_PATH = ARTIFACT_DIR / "model_comparison.csv"
SUBMISSION_PATH = ARTIFACT_DIR / "submission.csv"

TARGET = "target"
ID_COLUMNS = ["msno", "song_id"]
DATE_COLUMNS = ["registration_init_time", "expiration_date"]
DROP_COLUMNS = DATE_COLUMNS + ID_COLUMNS
SONG_FIELDS = ["song_length", "genre_ids", "artist_name", "composer", "lyricist", "language"]
UNKNOWN = "UnKnown"
RANDOM_STATE = 42
TEST_SIZE = 0.3
