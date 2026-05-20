from collections import defaultdict


# -------------------------
# MAIN ENTRY
# -------------------------

def generate_insights(records):

    if not records:
        return empty_response()

    store_scores = defaultdict(float)
    store_metrics = defaultdict(list)
    risks = []
    actions = []

    total_off_track = 0

    # -------------------------
    # SCORE STORES
    # -------------------------
    for r in records:
        if r.status == "off_track":
            total_off_track += 1

            impact = abs(r.variance or 0)

            # Weight metrics differently
            if r.metric == "sales":
                score = impact * 2
            elif r.metric == "labor":
                score = impact * 1.5
            else:
                score = impact

            store_scores[r.store] += score
            store_metrics[r.store].append(r)

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
    # RISK DETECTION
    # -------------------------
    metric_counts = defaultdict(int)

    for r in records:
        if r.status == "off_track":
            metric_counts[r.metric] += 1

    for metric, count in metric_counts.items():
        if count >= 3:
            risks.append(
                f"{metric.upper()} issues detected across {count} records"
            )

    # -------------------------
    # ACTION GENERATION
    # -------------------------
    for store in priority_stores:
        metrics = store_metrics[store]

        for m in metrics:
            if m.metric == "labor":
                actions.append(
                    f"Reduce labor in store {store} (variance {round(m.variance,2)})"
                )
            elif m.metric == "sales":
                actions.append(
                    f"Drive sales recovery in store {store} (gap {round(m.variance,2)})"
                )
            elif m.metric == "shrink":
                actions.append(
                    f"Investigate shrink in store {store}"
                )

    # Deduplicate actions
    actions = list(set(actions))[:5]

    # -------------------------
    # SUMMARY
    # -------------------------
    summary = (
        f"{total_off_track} metrics off track across {len(records)} total records."
    )

    # -------------------------
    # VP SUMMARY
    # -------------------------
    vp_summary = f"""
District Operational Readout:

- {len(records)} KPI records analyzed
- {total_off_track} metrics off track

Top priority stores:
{', '.join(priority_stores) if priority_stores else 'None'}

Primary risks:
{', '.join(risks) if risks else 'No major risks'}

Action Plan:
{chr(10).join(['- ' + a for a in actions]) if actions else '- Maintain execution'}
"""

    # -------------------------
    # HUDDLE
    # -------------------------
    if total_off_track == 0:
        huddle = "Team, great job — all metrics are on track. Stay consistent."
    else:
        huddle = f"""
Team, quick focus:

We have {total_off_track} metrics off track.

Priority stores: {', '.join(priority_stores)}

Focus on execution, especially in key problem areas.
"""

    return {
        "summary": summary,
        "priority_stores": priority_stores,
        "risks": risks,
        "actions": actions,
        "vp_summary": vp_summary.strip(),
        "huddle": huddle.strip()
    }


# -------------------------
# EMPTY RESPONSE
# -------------------------

def empty_response():
    return {
        "summary": "No valid data detected.",
        "priority_stores": [],
        "risks": [],
        "actions": [],
        "vp_summary": "No data available.",
        "huddle": "No data available."
    }
