from fastapi import APIRouter, UploadFile
from typing import Dict
from app.services.parsers import parse_text_to_records, normalize_records
from app.services.ai import generate_ai_insights, chat_with_context

from app.db import SessionLocal
from app.models import Analysis

router = APIRouter()

# =========================
# ANALYZE TEXT + SAVE
# =========================
@router.post("/analyze/text")
async def analyze_text(data: Dict):
    text = data.get("text", "")

    records = parse_text_to_records(text)
    records = normalize_records(records)

    ai_summary = generate_ai_insights(text)

    # SAVE TO DB
    db = SessionLocal()
    new_analysis = Analysis(
        raw_text=text,
        summary=ai_summary
    )
    db.add(new_analysis)
    db.commit()
    db.close()

    records["summary"] = ai_summary
    return records

# =========================
# GET HISTORY
# =========================
@router.get("/history")
def get_history():
    db = SessionLocal()
    results = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(10).all()
    db.close()

    return [
        {"id": r.id, "summary": r.summary, "created_at": str(r.created_at)}
        for r in results
    ]

# =========================
# AI CHAT OVER DATA
# =========================
@router.post("/chat")
async def chat(data: Dict):
    question = data.get("question", "")
    history = data.get("context", "")

    response = chat_with_context(question, history)
    return {"response": response}