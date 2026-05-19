from fastapi import APIRouter, UploadFile, File, Form
from pathlib import Path
import shutil
from app.services.capture import save_upload, extract_frames_from_video
from app.services.redaction import redact_image_text_regions
from app.services.parsers import parse_excel_or_csv, parse_image, parse_text_blob
from app.services.intelligence import generate_intelligence
from app.services.storage import save_records, save_summary
from app.core.config import RAW_DIR, FRAME_DIR

router = APIRouter()

@router.post("/analyze/upload")
async def analyze_upload(files: list[UploadFile] = File(...)):
    all_records = []

    for f in files:
        saved = save_upload(f.file, f.filename)
        ext = saved.suffix.lower()

        if ext in [".xlsx", ".xls", ".csv"]:
            all_records.extend(parse_excel_or_csv(saved))

        elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
            redacted = FRAME_DIR / f"redacted_{saved.name}.png"
            redact_image_text_regions(str(saved), str(redacted))
            all_records.extend(parse_image(redacted))

        elif ext in [".mp4", ".mov", ".avi", ".mkv"]:
            frames = extract_frames_from_video(saved)
            for frame in frames:
                redacted = FRAME_DIR / f"redacted_{frame.name}"
                redact_image_text_regions(str(frame), str(redacted))
                all_records.extend(parse_image(redacted))

        else:
            all_records.append(parse_text_blob(f"Unsupported file type: {saved.name}", source=saved.name)[0])

    output = generate_intelligence(all_records)
    save_records(output.cleaned_records)
    save_summary(output)
    return output

@router.post("/analyze/text")
async def analyze_text(text: str = Form(...)):
    records = parse_text_blob(text)
    output = generate_intelligence(records)
    save_records(output.cleaned_records)
    save_summary(output)
    return output
