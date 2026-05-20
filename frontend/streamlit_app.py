import streamlit as st
import requests
import pandas as pd
import time

API = "https://districtos.onrender.com/api"

st.set_page_config(layout="wide")

# -------------------------
# ROLE-BASED VIEW 🔥
# -------------------------
role = st.sidebar.selectbox("View Mode", ["Executive", "Operator"])

menu = st.sidebar.radio("", [
    "Command Center",
    "Intake",
    "Operations",
    "Intelligence",
    "Alerts",
    "Ask AI"
])

st.sidebar.markdown("## DistrictOS")
st.sidebar.caption("Enterprise Intelligence Platform")

if "results" not in st.session_state:
    st.session_state.results = None

if "selected_store" not in st.session_state:
    st.session_state.selected_store = None

# -------------------------
# GLOBAL STYLE
# -------------------------
st.markdown("""
<style>
.card {
    background: #111827;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #1F2937;
    margin-bottom: 15px;
}
.kpi {
    font-size: 32px;
    font-weight: bold;
}
.label {
    font-size: 12px;
    color: #9CA3AF;
}
</style>
""", unsafe_allow_html=True)


# -------------------------
# COMMAND CENTER
# -------------------------
if menu == "Command Center":

    st.title("Command Center")
    r = st.session_state.results

    if not r:
        st.warning("No data")
    else:
        score = r["district_score"]

        color = "green" if score > 80 else "orange" if score > 60 else "red"

        # 🔥 Animated feel
        display = st.empty()
        for i in range(0, score + 1, max(1, score // 20)):
            display.markdown(f"## {i}")
            time.sleep(0.01)
        display.markdown(f"## :{color}[{score}]")

        col1, col2, col3 = st.columns(3)

        col1.metric("Stores", len(r["store_severity"]),
                    help="Total stores analyzed")

        col2.metric("Patterns", len(r["patterns"]),
                    help="Cross-store issues detected")

        col3.metric("Alerts", len(r["alerts"]),
                    help="Stores worsening over time")

        st.caption(r["summary"])


# -------------------------
# INTAKE
# -------------------------
elif menu == "Intake":

    f = st.file_uploader("Upload")
    t = st.text_area("Paste")

    if st.button("Analyze"):
        if f:
            res = requests.post(f"{API}/analyze/upload",
                                files={"file": (f.name, f.getvalue())})
        else:
            res = requests.post(f"{API}/analyze/text",
                                json={"text": t})

        if res.status_code == 200:
            st.session_state.results = res.json()


# -------------------------
# OPERATIONS (DRILLDOWN)
# -------------------------
elif menu == "Operations":

    r = st.session_state.results

    if r:

        # STORE SELECTOR 🔥
        selected = st.selectbox(
            "Select Store",
            r["priority_stores"],
            index=0 if not st.session_state.selected_store else
            r["priority_stores"].index(st.session_state.selected_store)
        )

        st.session_state.selected_store = selected

        sev = r["store_severity"][selected]
        impacts = r["impacts"].get(selected, [])
        metrics = r["store_metrics"].get(selected, [])

        st.markdown(f"## Store {selected} | Severity: {sev}")

        # 🔥 KPI TOOLTIPS
        cols = st.columns(len(metrics)) if metrics else [st]

        for i, m in enumerate(metrics):
            with cols[i]:
                st.metric(
                    m["metric"],
                    m["actual"],
                    round(m["variance"], 2) if m["variance"] else 0,
                    help=f"Target: {m['target']} | Status: {m['status']}"
                )

        # Trend chart
        trend = r.get("trend_memory", {}).get(selected, [])
        if trend:
            df = pd.DataFrame(trend)
            st.line_chart(df["severity"])

        # Impact
        st.markdown("### Impact")
        for i in impacts:
            st.warning(i)

        # Actions
        st.markdown("### Actions")
        for a in r["actions"]:
            if selected in a:
                st.success(a)


# -------------------------
# INTELLIGENCE
# -------------------------
elif menu == "Intelligence":

    r = st.session_state.results

    if r:
        for p in r["patterns"]:
            with st.expander(f"{p['metric']} ({p['count']} stores)"):
                st.write(", ".join(map(str, p["stores"])))


# -------------------------
# ALERTS
# -------------------------
elif menu == "Alerts":

    r = st.session_state.results

    if r:
        if r["alerts"]:
            for a in r["alerts"]:
                st.error(a)
        else:
            st.success("No alerts")


# -------------------------
# ASK AI
# -------------------------
elif menu == "Ask AI":

    r = st.session_state.results

    if r:
        q = st.text_input("Ask DistrictOS")

        if q:
            with st.spinner("Thinking..."):
                if "worst" in q:
                    st.write(f"Focus on store {r['priority_stores'][0]}")
                elif "fix" in q:
                    st.write(r["actions"][:3])
                elif "trend" in q:
                    st.write("Some stores are worsening over time")
                else:
                    st.write("Try asking about risks, trends, or priorities")
