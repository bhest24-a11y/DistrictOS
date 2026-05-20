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
    impacts = defaultdict(list)  # 🔥 NEW

    total_off_track = 0

    # -------------------------
    # BUILD METRICS + SCORING
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

            # % deviation
            if r.target and r.target != 0:
                pct_diff = abs((r.actual - r.target) / r.target)
            else:
                pct_diff = abs(r.variance or 0)

            # weighting
            if r.metric == "sales":
                weight = 2.5
            elif r.metric == "labor":
                weight = 2.0
            else:
                weight = 1.2

            score = pct_diff * 100 * weight
            store_scores[r.store] += score

            # -------------------------
            # 🔥 WHY THIS MATTERS (IMPACT)
            # -------------------------
            if r.metric == "sales":
                impacts[r.store].append(
                    f"Revenue risk: sales below target by {round(r.variance,2)}"
                )

            elif r.metric == "labor":
                impacts[r.store].append(
                    f"Margin risk: labor above plan by {round(r.variance,2)}"
                )

            elif r.metric == "shrink":
                impacts[r.store].append(
                    f"Profit risk: shrink impacting inventory control"
                )

            else:
                impacts[r.store].append(
                    f"Operational risk in {r.metric}"
                )

    # -------------------------
    # NORMALIZE SEVERITY
    # -------------------------
    max_score = max(store_scores.values()) if store_scores else 1

    for store, score in store_scores.items():
        store_severity[store] = min(100, round((score / max_score) * 100))

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
    # PATTERN DETECTION
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
                actions.append(
                    f"Reduce labor in store {store}"
                )

            elif m["metric"] == "sales":
                actions.append(
                    f"Drive sales recovery in store {store}"
                )

            elif m["metric"] == "shrink":
                actions.append(
                    f"Investigate shrink in store {store}"
                )

    actions = list(set(actions))[:6]

    # -------------------------
    # SUMMARY
    # -------------------------
    summary = (
        f"{total_off_track} metrics off track across {len(records)} records."
    )

    return {
        "summary": summary,
        "priority_stores": priority_stores,
        "store_metrics": dict(store_metrics),
        "store_severity": store_severity,
        "patterns": patterns,
        "impacts": dict(impacts),  # 🔥 NEW
        "risks": risks,
        "actions": actions,
        "records_found": len(records)
    }


def empty_response():
    return {
        "summary": "No valid data detected.",
        "priority_stores": [],
        "store_metrics": {},
        "store_severity": {},
        "patterns": [],
        "impacts": {},
        "risks": [],
        "actions": [],
        "records_found": 0
    }
