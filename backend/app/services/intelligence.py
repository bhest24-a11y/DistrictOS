from collections import defaultdict
from datetime import datetime

# simple in-memory trend store (can replace with DB later)
TREND_MEMORY = {}


def generate_insights(records):

    if not records:
        return empty_response()

    store_scores = defaultdict(float)
    store_metrics = defaultdict(list)
    store_severity = {}
    impacts = defaultdict(list)

    risks = []
    actions = []
    patterns = []

    total_off_track = 0

    # -------------------------
    # METRICS + SCORING + IMPACT
    # -------------------------
    for r in records:

        store_metrics[r.store].append({
            "metric": r.metric,
            "actual": r.actual,
            "target": r.target,
            "variance": r.variance,
            "status": r.status
        })

        if r.status == "off_track":
            total_off_track += 1

            pct_diff = (
                abs((r.actual - r.target) / r.target)
                if r.target else abs(r.variance or 0)
            )

            weight = 2.5 if r.metric == "sales" else 2.0 if r.metric == "labor" else 1.2

            store_scores[r.store] += pct_diff * 100 * weight

            # IMPACT
            if r.metric == "sales":
                impacts[r.store].append(f"Revenue risk: down {round(r.variance,2)}")
            elif r.metric == "labor":
                impacts[r.store].append(f"Margin risk: labor over {round(r.variance,2)}")
            elif r.metric == "shrink":
                impacts[r.store].append("Profit risk: shrink detected")
            else:
                impacts[r.store].append(f"Operational risk in {r.metric}")

    # -------------------------
    # STORE SEVERITY
    # -------------------------
    max_score = max(store_scores.values()) if store_scores else 1

    for store, score in store_scores.items():
        store_severity[store] = min(100, round((score / max_score) * 100))

    # -------------------------
    # DISTRICT SCORE
    # -------------------------
    if store_severity:
        avg = sum(store_severity.values()) / len(store_severity)
        worst = sorted(store_severity.values(), reverse=True)[:3]
        worst_avg = sum(worst) / len(worst)

        district_score = max(0, round(100 - (avg * 0.6 + worst_avg * 0.4)))
    else:
        district_score = 100

    # -------------------------
    # TREND MEMORY 🔥
    # -------------------------
    timestamp = datetime.utcnow().isoformat()

    for store, severity in store_severity.items():
        if store not in TREND_MEMORY:
            TREND_MEMORY[store] = []

        TREND_MEMORY[store].append({
            "time": timestamp,
            "severity": severity
        })

        # keep last 5
        TREND_MEMORY[store] = TREND_MEMORY[store][-5:]

    # -------------------------
    # ALERT ENGINE 🔥
    # -------------------------
    alerts = []

    for store, history in TREND_MEMORY.items():
        if len(history) >= 3:
            last3 = [h["severity"] for h in history[-3:]]

            if last3[2] > last3[1] > last3[0]:
                alerts.append(f"Store {store} worsening trend")

    # -------------------------
    # PATTERNS
    # -------------------------
    metric_map = defaultdict(set)

    for r in records:
        if r.status == "off_track":
            metric_map[r.metric].add(r.store)

    for metric, stores in metric_map.items():
        if len(stores) >= 3:
            patterns.append({
                "metric": metric,
                "stores": list(stores),
                "count": len(stores)
            })
            risks.append(f"{metric} trending across {len(stores)} stores")

    # -------------------------
    # PRIORITIES
    # -------------------------
    priority_stores = sorted(
        store_severity,
        key=store_severity.get,
        reverse=True
    )[:5]

    # -------------------------
    # ACTIONS
    # -------------------------
    for store in priority_stores:
        for m in store_metrics[store]:
            if m["status"] != "off_track":
                continue

            if m["metric"] == "labor":
                actions.append(f"Reduce labor in store {store}")
            elif m["metric"] == "sales":
                actions.append(f"Drive sales in store {store}")
            elif m["metric"] == "shrink":
                actions.append(f"Investigate shrink in store {store}")

    actions = list(set(actions))[:6]

    # -------------------------
    # AI RESPONSE (ASK DISTRICTOS)
    # -------------------------
    def ask_ai(question: str):
        if "worst" in question.lower():
            return f"Focus on store {priority_stores[0]}"
        elif "fix" in question.lower():
            return actions[:3]
        return "Ask about priorities, risks, or actions."

    # -------------------------
    # SUMMARY
    # -------------------------
    summary = f"{total_off_track} issues | District Score: {district_score}"

    return {
        "summary": summary,
        "district_score": district_score,
        "priority_stores": priority_stores,
        "store_metrics": dict(store_metrics),
        "store_severity": store_severity,
        "patterns": patterns,
        "impacts": dict(impacts),
        "risks": risks,
        "actions": actions,
        "alerts": alerts,
        "trend_memory": TREND_MEMORY,
        "ask_ai": "enabled",
        "records_found": len(records)
    }


def empty_response():
    return {
        "summary": "No data",
        "district_score": 100,
        "priority_stores": [],
        "store_metrics": {},
        "store_severity": {},
        "patterns": [],
        "impacts": {},
        "risks": [],
        "actions": [],
        "alerts": [],
        "trend_memory": {},
        "ask_ai": "enabled",
        "records_found": 0
    }
