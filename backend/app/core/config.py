from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "uploads" / "raw"
FRAME_DIR = DATA_DIR / "uploads" / "frames"
PROCESSED_DIR = DATA_DIR / "processed"

for d in [RAW_DIR, FRAME_DIR, PROCESSED_DIR]:
    d.mkdir(parents=True, exist_ok=True)

DELETE_RAW_RECORDINGS_AFTER_EXTRACTION = True
FRAME_SAMPLE_EVERY_SECONDS = 3
