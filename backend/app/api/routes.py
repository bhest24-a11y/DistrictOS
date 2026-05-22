from fastapi import APIRouter
from typing import Dict

from app.services.parsers import parse_text_to_records, normalize_records
from app.services.ai import generate_ai_insights, chat_with_context, analyze_store
from app.services.scoring import score_stores, build_district_metrics

from app.db import SessionLocal
from app.models import Analysis

router = APIRouter()

# =========================
# ANALYZE TEXT + SAVE (REAL ENGINE)
# =========================
@router.post("/analyze/text")
async def analyze_text(data: Dict):

    text = data.get("text", "")

    # -------------------------
    # PARSE + NORMALIZE
    # -------------------------
    records = parse_text_to_records(text)
    normalized = normalize_records(records)
    records = normalized["records"]

    # -------------------------
    # 🔥 REAL SCORING ENGINE
    # -------------------------
    store_scores, store_flags = score_stores(records)
    metrics = build_district_metrics(store_scores, store_flags)

    # -------------------------
    # 🧠 AI SUMMARY
    # -------------------------
    ai_summary = generate_ai_insights(text)

    # -------------------------
    # 💾 SAVE TO DB
    # -------------------------
    db = SessionLocal()
    new_analysis = Analysis(
        raw_text=text,
        summary=ai_summary
    )
    db.add(new_analysis)
    db.commit()
    db.close()

    # -------------------------
    # 📤 FINAL RESPONSE
    # -------------------------
    return {
        **metrics,
        "summary": ai_summary,
        "raw_text": text
    }


# =========================
# 🏪 STORE AI ANALYSIS
# =========================
@router.post("/store/analyze")
async def analyze_store_route(data: Dict):

    store_id = data.get("store_id")
    context = data.get("context", "")

    result = analyze_store(store_id, context)

    return {"insight": result}


# =========================
# 📊 HISTORY
# =========================
@router.get("/history")
def get_history():

    db = SessionLocal()
    results = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(10).all()
    db.close()

    return [
        {
            "id": r.id,
            "summary": r.summary,
            "created_at": str(r.created_at)
        }
        for r in results
    ]


# =========================
# 💬 AI CHAT
# =========================
@router.post("/chat")
async def chat(data: Dict):

    question = data.get("question", "")
    history = data.get("context", "")

    response = chat_with_context(question, history)

    return {"response": response}