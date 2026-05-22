from collections import defaultdict

# =========================
# STORE SCORING ENGINE
# =========================
def score_stores(records):

    store_scores = defaultdict(int)
    store_flags = defaultdict(list)

    for r in records:

        store = r.get("store_id")
        kpi = r.get("kpi")
        value = r.get("value")

        if not store:
            continue

        # -------------------------
        # RULES ENGINE
        # -------------------------

        # SALES
        if kpi == "sales":
            if value < 80:
                store_scores[store] += 20
                store_flags[store].append("Low sales")

        # LABOR
        if kpi == "labor":
            if value < 70:
                store_scores[store] += 15
                store_flags[store].append("Labor shortage")

        # EXECUTION
        if kpi == "execution":
            if value < 75:
                store_scores[store] += 25
                store_flags[store].append("Execution gap")

        # CUSTOMER
        if kpi == "customer":
            if value < 85:
                store_scores[store] += 10
                store_flags[store].append("Customer risk")

    return dict(store_scores), dict(store_flags)


# =========================
# DISTRICT AGGREGATION
# =========================
def build_district_metrics(store_scores, store_flags):

    if not store_scores:
        return {}

    # Normalize to 0–100 severity
    max_score = max(store_scores.values()) or 1

    normalized = {
        s: int((score / max_score) * 100)
        for s, score in store_scores.items()
    }

    # Priority stores
    priority = sorted(normalized, key=normalized.get, reverse=True)

    # District score (inverse of severity)
    avg_severity = sum(normalized.values()) / len(normalized)
    district_score = int(100 - avg_severity)

    # Alerts
    alerts = []
    for s, flags in store_flags.items():
        for f in flags:
            if "gap" in f.lower() or "shortage" in f.lower():
                alerts.append(f"Critical: {f} at store {s}")
            else:
                alerts.append(f"Warning: {f} at store {s}")

    # Patterns (simple aggregation)
    pattern_counts = defaultdict(int)
    for flags in store_flags.values():
        for f in flags:
            pattern_counts[f] += 1

    patterns = [
        f"{k} occurring in {v} stores"
        for k, v in pattern_counts.items()
        if v > 1
    ]

    return {
        "store_severity": normalized,
        "priority_stores": priority,
        "district_score": district_score,
        "alerts": alerts,
        "patterns": patterns
    }