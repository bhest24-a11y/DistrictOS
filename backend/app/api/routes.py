from fastapi import APIRouter, UploadFile
from typing import Dict

router = APIRouter()

# -------------------------
# MOCK INTELLIGENCE (SAFE)
# -------------------------
def generate_insights(records):

    # Fake structure so UI works fully
    return {
        "district_score": 72,
        "summary": "Multiple stores showing operational inconsistency. Focus required on top performers declining.",

        "store_severity": {
            "101": 85,
            "102": 64,
            "103": 42
        },

        "priority_stores": ["101", "102"],

        "patterns": [
            {"metric": "labor", "count": 2, "stores": ["101", "102"]},
            {"metric": "sales", "count": 1, "stores": ["101"]}
        ],

        "alerts": [
            "Store 101 trending downward",
            "Labor cost spike detected"
        ],

        "impacts": {
            "101": ["High labor cost reducing margin", "Sales declining week-over-week"],
            "102": ["Understaffing impacting service"]
        },

        "actions": [
            "Adjust labor schedule at store 101",
            "Investigate sales drop at store 101",
            "Increase staffing at store 102"
        ],

        "store_metrics": {
            "101": [
                {"metric": "Sales", "actual": 80, "target": 100, "variance": -20, "status": "bad"},
                {"metric": "Labor", "actual": 120, "target": 100, "variance": 20, "status": "bad"}
            ],
            "102": [
                {"metric": "Sales", "actual": 90, "target": 100, "variance": -10, "status": "warning"}
            ]
        },

        "trend_memory": {
            "101": [{"severity": 60}, {"severity": 70}, {"severity": 85}],
            "102": [{"severity": 50}, {"severity": 55}, {"severity": 64}]
        },

        "risks": [
            "Margin compression across multiple stores",
            "Operational inconsistency increasing"
        ]
    }


# -------------------------
# ROUTES
# -------------------------

@router.post("/analyze/text")
async def analyze_text(data: Dict):
    records = []  # plug parser later
    return generate_insights(records)


@router.post("/analyze/upload")
async def analyze_upload(file: UploadFile):
    contents = await file.read()
    records = []  # plug parser later
    return generate_insights(records)


# -------------------------
# AI (SAFE FALLBACK)
# -------------------------

@router.post("/ask")
async def ask(data: Dict):

    q = data.get("question", "").lower()

    if "worst" in q:
        return {"response": "Store 101 is the highest risk."}

    if "fix" in q:
        return {"response": "Focus on labor optimization and sales recovery."}

    if "risk" in q:
        return {"response": "Primary risk is margin compression and declining sales."}

    return {"response": "Ask about risks, worst stores, or actions."}
