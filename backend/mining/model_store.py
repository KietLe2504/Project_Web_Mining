import joblib

from .config import ARTIFACT_DIR, MODEL_PATH


def save_bundle(bundle):
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, MODEL_PATH)


def load_bundle():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"{MODEL_PATH} not found. Run `python -m mining.train` from the backend directory first."
        )
    return joblib.load(MODEL_PATH)
