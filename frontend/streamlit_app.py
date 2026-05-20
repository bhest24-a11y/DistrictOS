import streamlit as st
import requests
import pandas as pd
import time

API = "https://districtos.onrender.com/api"

st.set_page_config(layout="wide")

# -------------------------
# GLOBAL STATE
# -------------------------
if "results" not in st.session_state:
    st.session_state.results = None

if "selected_store" not in st.session_state:
    st.session_state.selected_store = None

# -------------------------
# SIDEBAR (ROLE + NAV)
# -------------------------
role = st.sidebar.selectbox("View", ["Executive", "Operator"])

menu = st.sidebar.radio("", [
    "Command Center",
    "Operations",
    "Intelligence",
    "Alerts",
    "AI Command",
    "Intake"
])

st.sidebar.markdown("## DistrictOS")
st.sidebar.caption("Enterprise Operating System")

# -------------------------
# GLOBAL STYLE (PREMIUM)
# -------------------------
st.markdown("""
<style>
.card {
    background: linear-gradient(145deg, #0F172A, #020617);
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #1E293B;
    margin-bottom: 16px;
}
.kpi {
    font-size: 36px;
    font-weight: 700;
}
.label {
    font-size: 11px;
    color: #94A3B8;
}
.section {
    margin-top: 25px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER (ALWAYS VISIBLE)
# -------------------------
r = st.session_state.results

if r:
    score = r["district_score"]
    color = "green" if score > 80 else "orange" if score > 60 else "red"

    st.markdown(f"### District Score: :{color}[{score}]")

# -------------------------
# COMMAND CENTER (EXEC VIEW)
# -------------------------
if menu == "Command Center":

    st.title("Command Center")

    if not r:
        st.warning("No data loaded")
    else:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Stores", len(r["store_severity"]))
        col2.metric("Priority", len(r["priority_stores"]))
        col3.metric("Patterns", len(r["patterns"]))
        col4.metric("Alerts", len(r["alerts"]))

        st.markdown("### Top Risk Stores")

        for s in r["priority_stores"][:3]:
            sev = r["store_severity"][s]

            st.markdown(f"""
            <div class="card">
                <div class="label">STORE {s}</div>
                <div class="kpi">{sev}</div>
            </div>
            """, unsafe_allow_html=True)

# -------------------------
# OPERATIONS (DECISION LAYER)
# -------------------------
elif menu == "Operations":

    st.title("Operations")

    if r:

        selected = st.selectbox(
            "Select Store",
            r["priority_stores"]
        )

        st.session_state.selected_store = selected

        sev = r["store_severity"][selected]
        metrics = r["store_metrics"][selected]
        impacts = r["impacts"].get(selected, [])

        # SEVERITY BAR 🔥
        st.progress(sev / 100)

        st.markdown(f"## Store {selected} | Severity {sev}")

        # KPI GRID
        cols = st.columns(len(metrics))

        for i, m in enumerate(metrics):
            with cols[i]:
                st.metric(
                    m["metric"],
                    m["actual"],
                    round(m["variance"], 2) if m["variance"] else 0,
                    help=f"Target: {m['target']} | Status: {m['status']}"
                )

        # TREND INLINE
        trend = r.get("trend_memory", {}).get(selected, [])
        if trend:
            df = pd.DataFrame(trend)
            st.line_chart(df["severity"])

        # IMPACT → DECISION LANGUAGE
        st.markdown("### Business Impact")
        for i in impacts:
            st.error(i)

        # ACTIONS → PRIORITIZED
        st.markdown("### Recommended Actions")
        for a in r["actions"]:
            if selected in a:
                st.success(a)

# -------------------------
# INTELLIGENCE (PATTERNS)
# -------------------------
elif menu == "Intelligence":

    st.title("Intelligence")

    if r:
        for p in r["patterns"]:
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <div class="label">{p['metric'].upper()}</div>
                    <div class="kpi">{p['count']} stores</div>
                </div>
                """, unsafe_allow_html=True)

                st.caption(", ".join(map(str, p["stores"])))

# -------------------------
# ALERTS (REAL-TIME FEEL)
# -------------------------
elif menu == "Alerts":

    st.title("Alerts")

    if r:
        if r["alerts"]:
            for a in r["alerts"]:
                st.error(a)
        else:
            st.success("No active alerts")

# -------------------------
# AI COMMAND (REAL PRODUCT FEEL)
# -------------------------
elif menu == "AI Command":

    st.title("AI Command")

    if r:
        st.caption("Ask DistrictOS what to do")

        q = st.text_input("What do you want to know?")

        if q:
            with st.spinner("Analyzing..."):

                if "worst" in q:
                    st.markdown(f"### Focus on Store {r['priority_stores'][0]}")

                elif "fix" in q:
                    st.markdown("### Top Actions")
                    for a in r["actions"][:3]:
                        st.write(a)

                elif "risk" in q:
                    for i in r["risks"]:
                        st.error(i)

                else:
                    st.write("Try: worst store, risks, or what to fix")

# -------------------------
# INTAKE
# -------------------------
elif menu == "Intake":

    st.title("Data Intake")

    f = st.file_uploader("Upload File")
    t = st.text_area("Paste Data")

    if st.button("Run Analysis"):
        if f:
            res = requests.post(
                f"{API}/analyze/upload",
                files={"file": (f.name, f.getvalue())}
            )
        else:
            res = requests.post(
                f"{API}/analyze/text",
                json={"text": t}
            )

        if res.status_code == 200:
            st.session_state.results = res.json()
            st.success("Analysis complete")
