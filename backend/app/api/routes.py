from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import shutil

# NEW SERVICES
from app.services.parsers import parse_file, parse_text_blob
from app.services.ocr import extract_text_from_image, extract_text_from_images
from app.services.video import extract_video_frames
from app.services.intelligence import generate_insights

# CONFIG
UPLOAD_DIR = Path("data/uploads")
FRAME_DIR = Path("data/frames")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
FRAME_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()


# -------------------------
# FILE UPLOAD ENDPOINT
# -------------------------
@router.post("/analyze/upload")
async def analyze_upload(file: UploadFile = File(...)):

    file_path = UPLOAD_DIR / file.filename

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ext = file_path.suffix.lower()

    records = []
    extracted_text = ""

    # -------------------------
    # CSV / EXCEL
    # -------------------------
    if ext in [".csv", ".xlsx", ".xls"]:
        records = parse_file(file_path)

    # -------------------------
    # IMAGE → OCR
    # -------------------------
    elif ext in [".png", ".jpg", ".jpeg"]:
        ocr_result = extract_text_from_image(file_path)

        extracted_text = ocr_result.get("text", "")
        records = parse_text_blob(extracted_text)

    # -------------------------
    # VIDEO → FRAMES → OCR
    # -------------------------
    elif ext in [".mp4", ".mov", ".avi", ".mkv"]:
        frames = extract_video_frames(file_path, FRAME_DIR)

        ocr_result = extract_text_from_images(frames)

        extracted_text = ocr_result.get("text", "")
        records = parse_text_blob(extracted_text)

    # -------------------------
    # FALLBACK
    # -------------------------
    else:
        return {
            "error": "Unsupported file type"
        }

    # -------------------------
    # INTELLIGENCE
    # -------------------------
    insights = generate_insights(records)

    return {
        "summary": insights["summary"],
        "priority_stores": insights["priority_stores"],
        "risks": insights["risks"],
        "actions": insights["actions"],
        "vp_summary": insights["vp_summary"],
        "huddle": insights["huddle"],
        "records_found": len(records),
        "raw_text_preview": extracted_text[:500] if extracted_text else None
    }


# -------------------------
# TEXT INPUT ENDPOINT
# -------------------------
@router.post("/analyze/text")
async def analyze_text(payload: dict):

    text = payload.get("text", "")

    records = parse_text_blob(text)
    insights = generate_insights(records)

    return {
        "summary": insights["summary"],
        "priority_stores": insights["priority_stores"],
        "risks": insights["risks"],
        "actions": insights["actions"],
        "vp_summary": insights["vp_summary"],
        "huddle": insights["huddle"],
        "records_found": len(records)
    }
