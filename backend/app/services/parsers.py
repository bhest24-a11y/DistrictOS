import re
from typing import List, Dict

# =========================
# PARSE RAW TEXT → RECORDS (ENGINE READY)
# =========================
def parse_text_to_records(text: str) -> List[Dict]:

    records = []
    lines = text.split("\n")

    for line in lines:

        # -------------------------
        # STORE ID
        # -------------------------
        store_match = re.search(r"\b(\d{3})\b", line)
        if not store_match:
            continue

        store_id = int(store_match.group(1))

        # -------------------------
        # EXTRACT KPIs
        # -------------------------
        sales = extract_number(line, "sales")
        labor = extract_number(line, "labor")
        target = extract_number(line, "target")
        execution = extract_number(line, "execution")
        customer = extract_number(line, "customer")

        # -------------------------
        # BUILD ENGINE RECORDS
        # (THIS feeds scoring.py)
        # -------------------------
        if sales is not None:
            records.append({
                "store_id": store_id,
                "kpi": "sales",
                "value": sales,
                "target": target
            })

        if labor is not None:
            records.append({
                "store_id": store_id,
                "kpi": "labor",
                "value": labor,
                "target": target
            })

        if execution is not None:
            records.append({
                "store_id": store_id,
                "kpi": "execution",
                "value": execution,
                "target": 100
            })

        if customer is not None:
            records.append({
                "store_id": store_id,
                "kpi": "customer",
                "value": customer,
                "target": 100
            })

    return records


# =========================
# HELPER: NUMBER EXTRACTION
# =========================
def extract_number(text: str, keyword: str):

    pattern = rf"{keyword}[:=]?\s*(\d+)"
    match = re.search(pattern, text.lower())

    if match:
        return int(match.group(1))

    return None


# =========================
# NORMALIZE + ENRICH (HYBRID)
# =========================
def normalize_records(records: List[Dict]):

    cleaned = []
    store_metrics = {}
    impacts = {}
    actions = set()

    # -------------------------
    # CLEAN + STANDARDIZE
    # -------------------------
    for r in records:
        try:
            cleaned.append({
                "store_id": int(r["store_id"]),
                "kpi": str(r["kpi"]).lower(),
                "value": float(r["value"]),
                "target": float(r.get("target", 100))
            })
        except:
            continue

    # -------------------------
    # BUILD BUSINESS INTELLIGENCE
    # (USED BY UI LATER)
    # -------------------------
    for r in cleaned:

        store = r["store_id"]
        kpi = r["kpi"]
        value = r["value"]
        target = r["target"]

        if store not in store_metrics:
            store_metrics[store] = []
            impacts[store] = []

        variance = value - target

        status = "good"
        if (kpi == "sales" and value < target) or \
           (kpi == "labor" and value > target):
            status = "bad"

        store_metrics[store].append({
            "metric": kpi,
            "actual": value,
            "target": target,
            "variance": variance,
            "status": status
        })

        # -------------------------
        # IMPACTS + ACTIONS
        # -------------------------
        if kpi == "sales" and value < target:
            impacts[store].append("Sales below target → revenue risk")
            actions.add(f"Increase sales performance at store {store}")

        if kpi == "labor" and value > target:
            impacts[store].append("Labor above target → margin pressure")
            actions.add(f"Reduce labor cost at store {store}")

        if kpi == "execution" and value < 80:
            impacts[store].append("Execution gap → operational inconsistency")
            actions.add(f"Improve execution at store {store}")

        if kpi == "customer" and value < 85:
            impacts[store].append("Customer experience risk")
            actions.add(f"Improve customer experience at store {store}")

    # -------------------------
    # RETURN STRUCTURE
    # -------------------------
    return {
        "records": cleaned,  # 🔥 feeds scoring engine
        "store_metrics": store_metrics,
        "impacts": impacts,
        "actions": list(actions),
        "trend_memory": {},
        "risks": ["Multi-store performance variability detected"]
    }