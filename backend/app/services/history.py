from app.db import SessionLocal
from app.models import Analysis


# =========================
# SAVE ANALYSIS
# =========================
def save_analysis(raw_text: str, summary: str):

    db = SessionLocal()

    try:
        new_analysis = Analysis(
            raw_text=raw_text,
            summary=summary
        )

        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)

        return new_analysis

    finally:
        db.close()


# =========================
# GET HISTORY
# =========================
def get_recent_analyses(limit: int = 10):

    db = SessionLocal()

    try:
        results = (
            db.query(Analysis)
            .order_by(Analysis.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": r.id,
                "summary": r.summary,
                "created_at": str(r.created_at)
            }
            for r in results
        ]

    finally:
        db.close()