from collections import defaultdict


def generate_insights(records):

    if not records:
        return empty_response()

    store_scores = defaultdict(float)
    store_metrics = defaultdict(list)
    risks = []
    actions = []

    total_off_track = 0

    # -------------------------
    # SCORE + GROUP METRICS
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

            impact = abs(r.variance or 0)

            if r.metric == "sales":
                score = impact * 2
            elif r.metric == "labor":
                score = impact * 1.5
            else:
                score = impact

            store_scores[r.store] += score

    # -------------------------
    # PRIORITY STORES
    # -------------------------
    sorted_stores = sorted(
        store_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    priority_stores = [s[0] for s in sorted_stores if s[0]][:5]

    # -------------------------
    # RISKS
    # -------------------------
    metric_counts = defaultdict(int)

    for r in records:
        if r.status == "off_track":
            metric_counts[r.metric] += 1

    for metric, count in metric_counts.items():
        if count >= 3:
            risks.append(f"{metric.upper()} issues across {count} records")

    # -------------------------
    # ACTIONS
    # -------------------------
    for store in priority_stores:
        for r in store_metrics[store]:
            if r["status"] != "off_track":
                continue

            if r["metric"] == "labor":
                actions.append(
                    f"Reduce labor in store {store} (variance {round(r['variance'],2)})"
                )

            elif r["metric"] == "sales":
                actions.append(
                    f"Drive sales recovery in store {store} (gap {round(r['variance'],2)})"
                )

    actions = list(set(actions))[:6]

    # -------------------------
    # SUMMARY
    # -------------------------
    summary = f"{total_off_track} metrics off track across {len(records)} records."

    # -------------------------
    # RETURN (NEW STRUCTURE)
    # -------------------------
    return {
        "summary": summary,
        "priority_stores": priority_stores,
        "store_metrics": dict(store_metrics),  # 🔥 NEW
        "risks": risks,
        "actions": actions,
        "records_found": len(records)
    }


def empty_response():
    return {
        "summary": "No valid data detected.",
        "priority_stores": [],
        "store_metrics": {},
        "risks": [],
        "actions": [],
        "records_found": 0
    }
