from collections import defaultdict


def generate_insights(records):

    if not records:
        return empty_response()

    store_scores = defaultdict(float)
    store_metrics = defaultdict(list)
    store_severity = {}

    risks = []
    actions = []
    patterns = []
    impacts = defaultdict(list)

    total_off_track = 0

    # -------------------------
    # BUILD METRICS + SCORING + IMPACT
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

            if r.target and r.target != 0:
                pct_diff = abs((r.actual - r.target) / r.target)
            else:
                pct_diff = abs(r.variance or 0)

            if r.metric == "sales":
                weight = 2.5
            elif r.metric == "labor":
                weight = 2.0
            else:
                weight = 1.2

            score = pct_diff * 100 * weight
            store_scores[r.store] += score

            # IMPACT LAYER
            if r.metric == "sales":
                impacts[r.store].append(
                    f"Revenue risk: down {round(r.variance,2)} vs plan"
                )
            elif r.metric == "labor":
                impacts[r.store].append(
                    f"Margin risk: labor over by {round(r.variance,2)}"
                )
            elif r.metric == "shrink":
                impacts[r.store].append(
                    "Profit risk: shrink impacting inventory"
                )
            else:
                impacts[r.store].append(
                    f"Operational risk in {r.metric}"
                )

    # -------------------------
    # STORE SEVERITY (0–100)
    # -------------------------
    max_score = max(store_scores.values()) if store_scores else 1

    for store, score in store_scores.items():
        store_severity[store] = min(100, round((score / max_score) * 100))

    # -------------------------
    # DISTRICT SCORE 🔥
    # -------------------------
    if store_severity:
        avg_severity = sum(store_severity.values()) / len(store_severity)

        # Penalize worst stores more heavily
        worst_stores = sorted(store_severity.values(), reverse=True)[:3]
        worst_avg = sum(worst_stores) / len(worst_stores) if worst_stores else 0

        district_score = max(
            0,
            round(100 - (avg_severity * 0.6 + worst_avg * 0.4))
        )
    else:
        district_score = 100

    # -------------------------
    # PRIORITY STORES
    # -------------------------
    sorted_stores = sorted(
        store_severity.items(),
        key=lambda x: x[1],
        reverse=True
    )

    priority_stores = [s[0] for s in sorted_stores][:5]

    # -------------------------
    # PATTERNS
    # -------------------------
    metric_store_map = defaultdict(set)

    for r in records:
        if r.status == "off_track":
            metric_store_map[r.metric].add(r.store)

    for metric, stores in metric_store_map.items():
        if len(stores) >= 3:
            patterns.append({
                "metric": metric,
                "stores": list(stores),
                "count": len(stores)
            })

            risks.append(
                f"{metric.upper()} trending across {len(stores)} stores"
            )

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
                actions.append(f"Drive sales recovery in store {store}")
            elif m["metric"] == "shrink":
                actions.append(f"Investigate shrink in store {store}")

    actions = list(set(actions))[:6]

    # -------------------------
    # SUMMARY
    # -------------------------
    summary = (
        f"{total_off_track} metrics off track across {len(records)} records. "
        f"District Score: {district_score}"
    )

    return {
        "summary": summary,
        "district_score": district_score,  # 🔥 NEW
        "priority_stores": priority_stores,
        "store_metrics": dict(store_metrics),
        "store_severity": store_severity,
        "patterns": patterns,
        "impacts": dict(impacts),
        "risks": risks,
        "actions": actions,
        "records_found": len(records)
    }


def empty_response():
    return {
        "summary": "No valid data detected.",
        "district_score": 100,
        "priority_stores": [],
        "store_metrics": {},
        "store_severity": {},
        "patterns": [],
        "impacts": {},
        "risks": [],
        "actions": [],
        "records_found": 0
    }
