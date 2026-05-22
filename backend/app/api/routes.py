from fastapi import APIRouter
from typing import Dict
import random

from app.services.parsers import parse_text_to_records, normalize_records
from app.services.ai import generate_ai_insights, chat_with_context, analyze_store

from app.db import SessionLocal
from app.models import Analysis

router = APIRouter()

# =========================
# ANALYZE TEXT + SAVE (UPGRADED ENGINE)
# =========================
@router.post("/analyze/text")
async def analyze_text(data: Dict):

    text = data.get("text", "")

    # Parse + normalize
    records = parse_text_to_records(text)
    records = normalize_records(records)

    # AI SUMMARY (REAL)
    ai_summary = generate_ai_insights(text)

    # -------------------------
    # 🔥 SIMULATED ENGINE (NEXT = REAL DATA MODEL)
    # -------------------------
    stores = [101, 102, 103, 104, 105]

    store_severity = {s: random.randint(40, 95) for s in stores}

    district_score = sum(store_severity.values()) // len(store_severity)

    priority_stores = sorted(store_severity, key=store_severity.get, reverse=True)

    alerts = [
        f"Critical issue at store {priority_stores[0]}",
        f"Warning: staffing gap at store {priority_stores[1]}"
    ]

    patterns = [
        "Labor shortages increasing",
        "Execution inconsistency across region"
    ]

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
    # 📤 RESPONSE (FRONTEND ENGINE)
    # -------------------------
    return {
        "district_score": district_score,
        "summary": ai_summary,
        "store_severity": store_severity,
        "priority_stores": priority_stores,
        "alerts": alerts,
        "patterns": patterns,
        "raw_text": text  # 🔥 CRITICAL FOR STORE AI
    }


# =========================
# 🏪 STORE AI ANALYSIS (NEW)
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