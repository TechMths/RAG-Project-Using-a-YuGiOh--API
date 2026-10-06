from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

CARDS_FILE = RAW_DATA_DIR / "cards.json"
PROCESSED_CARDS_FILE = PROCESSED_DATA_DIR / "cards.json"

IMAGES_FILES = DATA_DIR / "images"

API_BASE_URL = "https://db.ygoprodeck.com/api/v7"

REQUESTS_PER_SECOND = 5