def generate_insights(records):
    # -------------------------
    # NO DATA CASE (IMPORTANT FIX)
    # -------------------------
    if not records:
        return {
            "summary": "No usable KPI data detected.",
            "priority_stores": [],
            "risks": [],
            "actions": [],
            "huddle": "No data available. Ensure reports are uploaded clearly.",
            "vp_summary": "No KPI data was detected from the latest intake."
        }

    # -------------------------
    # CORE CALCULATIONS
    # -------------------------
    off_track = [r for r in records if r.status == "off_track"]

    store_map = {}
    for r in off_track:
        if not r.store:
            continue
        store_map.setdefault(r.store, []).append(r)

    # -------------------------
    # PRIORITY STORES (SORTED)
    # -------------------------
    priority_stores = sorted(
        store_map.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    top_stores = [s[0] for s in priority_stores[:5]]

    # -------------------------
    # RISKS
    # -------------------------
    risks = []
    for store, recs in priority_stores[:5]:
        for r in recs:
            if r.variance is not None:
                risks.append(
                    f"{store} - {r.metric} above target by {round(r.variance, 2)}"
                )

    # -------------------------
    # ACTIONS
    # -------------------------
    actions = []

    if off_track:
        actions.append("Focus on highest variance stores first")
        actions.append("Assign metric ownership at store level")
        actions.append("Execute 24-hour corrective action plans")
        actions.append("Follow up within same business day")
    else:
        actions.append("All metrics currently on track — maintain execution discipline")

    # -------------------------
    # SUMMARY
    # -------------------------
    summary = f"{len(off_track)} metrics off track across {len(records)} total records."

    # -------------------------
    # HUDDLE SCRIPT
    # -------------------------
    if off_track:
        huddle = f"""
Team, today we are focusing on execution gaps.

We have {len(off_track)} metrics off track.

Priority stores:
{', '.join(top_stores) if top_stores else "None identified"}

Focus:
- Close gaps on highest variance metrics
- Assign ownership
- Same-day follow-up
"""
    else:
        huddle = "Great job team — all metrics are currently on track. Stay consistent."

    # -------------------------
    # VP SUMMARY
    # -------------------------
    vp_summary = f"""
District Operational Readout:

- {len(records)} KPI records analyzed
- {len(off_track)} metrics off track

Top priority stores:
{', '.join(top_stores) if top_stores else "None"}

Primary risk:
Execution inconsistency across identified locations

Next steps:
- Target highest variance stores
- Deploy corrective actions within 24 hours
"""

    # -------------------------
    # FINAL OUTPUT
    # -------------------------
    return {
        "summary": summary,
        "priority_stores": top_stores,
        "risks": risks,
        "actions": actions,
        "huddle": huddle.strip(),
        "vp_summary": vp_summary.strip()
    }
