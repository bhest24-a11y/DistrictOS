import re
from typing import List, Dict


# -------------------------
# CORE PARSER
# -------------------------
def parse_text_to_records(text: str) -> List[Dict]:

    lines = text.split("\n")
    records = []

    for line in lines:

        # Example formats we handle:
        # Store 101 Sales: 80 Target: 100 Labor: 120
        # 102 | sales=90 | labor=110

        store_match = re.search(r"\b(\d{3})\b", line)
        if not store_match:
            continue

        store_id = store_match.group(1)

        sales = extract_number(line, "sales")
        labor = extract_number(line, "labor")
        target = extract_number(line, "target")

        record = {
            "store": store_id,
            "sales": sales,
            "labor": labor,
            "target": target
        }

        records.append(record)

    return records


# -------------------------
# HELPER: NUMBER EXTRACTION
# -------------------------
def extract_number(text: str, keyword: str):

    pattern = rf"{keyword}[:=]?\s*(\d+)"
    match = re.search(pattern, text.lower())

    if match:
        return int(match.group(1))

    return None


# -------------------------
# STRUCTURE FOR ENGINE
# -------------------------
def normalize_records(records: List[Dict]) -> Dict:

    store_severity = {}
    store_metrics = {}
    impacts = {}
    actions = []

    for r in records:

        store = r["store"]

        sales = r.get("sales") or 0
        labor = r.get("labor") or 0
        target = r.get("target") or 100

        # -------------------------
        # SEVERITY LOGIC 🔥
        # -------------------------
        severity = 0

        if sales < target:
            severity += (target - sales)

        if labor > target:
            severity += (labor - target)

        severity = min(100, severity)

        store_severity[store] = severity

        # -------------------------
        # METRICS
        # -------------------------
        store_metrics[store] = [
            {
                "metric": "Sales",
                "actual": sales,
                "target": target,
                "variance": sales - target,
                "status": "bad" if sales < target else "good"
            },
            {
                "metric": "Labor",
                "actual": labor,
                "target": target,
                "variance": labor - target,
                "status": "bad" if labor > target else "good"
            }
        ]

        # -------------------------
        # IMPACTS
        # -------------------------
        store_impacts = []

        if sales < target:
            store_impacts.append("Sales below target → revenue risk")

        if labor > target:
            store_impacts.append("Labor above target → margin pressure")

        impacts[store] = store_impacts

        # -------------------------
        # ACTIONS
        # -------------------------
        if sales < target:
            actions.append(f"Increase sales performance at store {store}")

        if labor > target:
            actions.append(f"Reduce labor cost at store {store}")

    # -------------------------
    # PRIORITIZATION
    # -------------------------
    priority_stores = sorted(
        store_severity,
        key=store_severity.get,
        reverse=True
    )

    # -------------------------
    # DISTRICT SCORE
    # -------------------------
    if store_severity:
        avg_severity = sum(store_severity.values()) / len(store_severity)
        district_score = int(100 - avg_severity)
    else:
        district_score = 100

    # -------------------------
    # PATTERNS
    # -------------------------
    patterns = []

    low_sales = [s for s, v in store_severity.items() if v > 50]
    if low_sales:
        patterns.append({
            "metric": "performance",
            "count": len(low_sales),
            "stores": low_sales
        })

    # -------------------------
    # ALERTS
    # -------------------------
    alerts = []

    for s, sev in store_severity.items():
        if sev > 80:
            alerts.append(f"Store {s} critical performance issue")

    # -------------------------
    # FINAL STRUCTURE
    # -------------------------
    return {
        "district_score": district_score,
        "summary": "Automated analysis of store performance completed.",

        "store_severity": store_severity,
        "priority_stores": priority_stores[:5],

        "patterns": patterns,
        "alerts": alerts,

        "impacts": impacts,
        "actions": list(set(actions)),  # remove duplicates

        "store_metrics": store_metrics,

        "trend_memory": {},  # will be filled later
        "risks": [
            "Underperformance detected across multiple stores"
        ]
    }
