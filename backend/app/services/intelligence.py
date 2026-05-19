from collections import defaultdict
from app.models.schemas import KPIRecord, IntelligenceOutput

def generate_intelligence(records: list[KPIRecord]) -> IntelligenceOutput:
    off_track = [r for r in records if r.status == "off_track"]
    needs_review = [r for r in records if r.status == "needs_review"]
    by_store = defaultdict(list)

    for r in records:
        if r.store:
            by_store[r.store].append(r)

    store_risk = sorted(
        by_store.items(),
        key=lambda kv: sum(1 for r in kv[1] if r.status in ["off_track", "needs_review"]),
        reverse=True
    )

    priority_stores = [s for s, _ in store_risk[:5]]

    summary = [
        f"{len(records)} cleaned KPI records created from messy intake.",
        f"{len(off_track)} metrics are off track.",
        f"{len(needs_review)} records need user review due to low confidence or missing target/actual.",
    ]

    risks = []
    if off_track:
        risks.append("Execution risk: multiple KPIs are below target or trending unfavorable.")
    if needs_review:
        risks.append("Data quality risk: some extracted records need confirmation before being used for decisions.")
    if priority_stores:
        risks.append(f"Concentration risk: priority appears clustered in stores {', '.join(priority_stores)}.")

    root_causes = [
        "Potential inconsistent process execution.",
        "Possible labor deployment mismatch against operational workload.",
        "Potential reporting fragmentation causing delayed response.",
    ]

    actions = [
        "Validate low-confidence records before saving to history.",
        "Focus first on the stores with the highest count of off-track metrics.",
        "Create a 24-hour action plan for each priority store.",
        "Use huddles to assign metric ownership and same-day follow-up.",
    ]

    vp_email = build_vp_email(summary, priority_stores, risks, actions)
    huddle = build_huddle(priority_stores, actions)

    return IntelligenceOutput(
        district_health_summary=summary,
        highest_priority_stores=priority_stores,
        risks=risks,
        likely_root_causes=root_causes,
        suggested_actions=actions,
        vp_email_draft=vp_email,
        huddle_script=huddle,
        cleaned_records=records
    )

def build_vp_email(summary, priority_stores, risks, actions):
    return f"""Subject: DistrictOS Operational Readout

High-level summary:
- {summary[0]}
- {summary[1]}
- {summary[2]}

Priority stores:
- {', '.join(priority_stores) if priority_stores else 'No store-level concentration detected yet'}

Primary risks:
- {'; '.join(risks) if risks else 'No major risks detected'}

Next actions:
- {actions[0]}
- {actions[1]}
- {actions[2]}

I will validate low-confidence data points and focus follow-up on the highest-risk stores first.
"""

def build_huddle(priority_stores, actions):
    return f"""Team Huddle Script

Today’s focus:
We are going to use the data to identify where execution needs immediate support.

Priority stores:
{chr(10).join('- ' + s for s in priority_stores) if priority_stores else '- No specific store priority yet'}

Leader actions:
- {actions[1]}
- {actions[2]}
- {actions[3]}

Close:
Each leader owns one metric, one action, and one same-day follow-up.
"""
