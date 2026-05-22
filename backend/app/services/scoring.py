from collections import defaultdict

# =========================
# DEFAULT KPI WEIGHTS (CONFIGURABLE)
# =========================
DEFAULT_WEIGHTS = {
    "sales": 0.4,
    "labor": 0.25,
    "execution": 0.2,
    "customer": 0.15
}

# =========================
# KPI SCORING LOGIC
# =========================
def score_kpi(kpi, value, target):

    if target is None or target == 0:
        return 50  # neutral if unknown

    if kpi == "sales":
        if value >= target:
            return 100
        return max(0, 100 - ((target - value) / target * 100))

    elif kpi == "labor":
        if value <= target:
            return 100
        return max(0, 100 - ((value - target) / target * 100))

    elif kpi in ["execution", "customer"]:
        return max(0, min(100, value))  # clamp

    return 50


# =========================
# STORE SCORING ENGINE
# =========================
def score_stores(records, weights=None):

    if not weights:
        weights = DEFAULT_WEIGHTS

    store_scores = {}
    store_flags = defaultdict(list)
    store_kpi_scores = defaultdict(dict)
    store_kpi_coverage = defaultdict(set)

    for r in records:
        store = r["store_id"]
        kpi = r["kpi"]
        value = r["value"]
        target = r.get("target", 100)

        score = score_kpi(kpi, value, target)

        store_kpi_scores[store][kpi] = score
        store_kpi_coverage[store].add(kpi)

        # FLAGGING
        if score < 60:
            store_flags[store].append(f"{kpi} underperforming ({int(score)})")

    # =========================
    # WEIGHTED FINAL SCORE
    # =========================
    for store, kpis in store_kpi_scores.items():

        weighted_score = 0
        total_weight = 0

        for kpi, score in kpis.items():
            weight = weights.get(kpi, 0)
            weighted_score += score * weight
            total_weight += weight

        if total_weight == 0:
            final_score = 0
        else:
            final_score = int(weighted_score / total_weight)

        store_scores[store] = final_score

        # Coverage warning
        if len(store_kpi_coverage[store]) < 2:
            store_flags[store].append("Low data coverage")

    return store_scores, dict(store_flags)


# =========================
# DISTRICT METRICS BUILDER
# =========================
def build_district_metrics(store_scores, store_flags):

    if not store_scores:
        return {}

    # Severity = inverse of score
    store_severity = {
        s: 100 - score for s, score in store_scores.items()
    }

    priority_stores = sorted(
        store_severity,
        key=store_severity.get,
        reverse=True
    )

    district_score = sum(store_scores.values()) // len(store_scores)

    # =========================
    # ALERTS
    # =========================
    alerts = []

    for s, sev in store_severity.items():
        if sev > 50:
            alerts.append(f"Critical: Store {s} severe risk")
        elif sev > 30:
            alerts.append(f"Warning: Store {s} declining")

    # =========================
    # PATTERNS
    # =========================
    patterns = []

    high_risk = [s for s, v in store_severity.items() if v > 40]

    if len(high_risk) >= 3:
        patterns.append("Systemic multi-store degradation trend")

    if district_score < 70:
        patterns.append("District-wide performance below standard")

    return {
        "district_score": district_score,
        "store_severity": store_severity,
        "priority_stores": priority_stores[:5],
        "alerts": alerts,
        "patterns": patterns,
        "store_flags": store_flags
    }