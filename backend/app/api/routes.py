from fastapi import APIRouter, UploadFile
from typing import Dict

# 🔥 Core services
from app.services.parsers import parse_text_to_records, normalize_records
from app.services.ai import generate_ai_insights

router = APIRouter()

# -------------------------
# ANALYZE TEXT
# -------------------------
@router.post("/analyze/text")
async def analyze_text(data: Dict):
    text = data.get("text", "")

    # 🔹 Parse + normalize
    records = parse_text_to_records(text)
    results = normalize_records(records)

    # 🔥 REAL AI INTEGRATION
    ai_summary = generate_ai_insights(text)
    results["summary"] = ai_summary

    return results


# -------------------------
# ANALYZE UPLOAD
# -------------------------
@router.post("/analyze/upload")
async def analyze_upload(file: UploadFile):
    contents = await file.read()

    try:
        text = contents.decode("utf-8")
    except:
        return {"error": "File must be text-readable (UTF-8)"}

    # 🔹 Parse + normalize
    records = parse_text_to_records(text)
    results = normalize_records(records)

    # 🔥 ADD AI HERE TOO (IMPORTANT)
    ai_summary = generate_ai_insights(text)
    results["summary"] = ai_summary

    return results


# -------------------------
# SIMPLE Q&A (KEEP FOR NOW)
# -------------------------
@router.post("/ask")
async def ask(data: Dict):
    q = data.get("question", "").lower()

    if "worst" in q:
        return {"response": "Highest severity store is your top priority."}
    if "fix" in q:
        return {"response": "Focus on reducing labor and improving sales performance."}
    if "risk" in q:
        return {"response": "Primary risk is underperformance and margin pressure."}

    return {"response": "Ask about risks, worst stores, or actions."}
