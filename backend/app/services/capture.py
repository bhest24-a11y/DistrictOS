import os
import uuid
import cv2
import shutil
from pathlib import Path
from app.core.config import RAW_DIR, FRAME_DIR, FRAME_SAMPLE_EVERY_SECONDS, DELETE_RAW_RECORDINGS_AFTER_EXTRACTION

def save_upload(file_obj, filename: str) -> Path:
    safe_name = f"{uuid.uuid4().hex}_{filename}"
    path = RAW_DIR / safe_name
    with open(path, "wb") as f:
        shutil.copyfileobj(file_obj, f)
    return path

def extract_frames_from_video(video_path: Path) -> list[Path]:
    capture_id = video_path.stem
    out_dir = FRAME_DIR / capture_id
    out_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_interval = int(fps * FRAME_SAMPLE_EVERY_SECONDS)

    frames = []
    frame_idx = 0
    saved_idx = 0

    while True:
        success, frame = cap.read()
        if not success:
            break
        if frame_idx % frame_interval == 0:
            out_path = out_dir / f"frame_{saved_idx:04d}.png"
            cv2.imwrite(str(out_path), frame)
            frames.append(out_path)
            saved_idx += 1
        frame_idx += 1

    cap.release()

    if DELETE_RAW_RECORDINGS_AFTER_EXTRACTION:
        try:
            os.remove(video_path)
        except OSError:
            pass

    return frames
