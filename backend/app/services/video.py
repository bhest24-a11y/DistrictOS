from pathlib import Path
import cv2


def extract_video_frames(video_path: Path, output_dir: Path, every_seconds: int = 3) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    frames = []
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        return frames

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * every_seconds) if fps else 90

    frame_count = 0
    saved_count = 0

    while True:
        success, frame = cap.read()
        if not success:
            break

        if frame_count % frame_interval == 0:
            frame_path = output_dir / f"frame_{saved_count}.jpg"
            cv2.imwrite(str(frame_path), frame)
            frames.append(frame_path)
            saved_count += 1

        frame_count += 1

    cap.release()
    return frames
