import streamlit as st
import requests

API = "https://districtos.onrender.com/api"

st.set_page_config(
    layout="wide",
    page_title="DistrictOS",
    initial_sidebar_state="expanded"
)

# -------------------------
# GLOBAL STYLING 🔥
# -------------------------
st.markdown("""
<style>
body {
    background-color: #0E1117;
    color: white;
}

[data-testid="stSidebar"] {
    background-color: #0B0D12;
}

h1, h2, h3 {
    font-weight: 600;
}

.metric-card {
    background: #151922;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #222;
}

.store-card {
    background: #151922;
    padding: 18px;
    border-radius: 12px;
    margin-bottom: 15px;
    border: 1px solid #222;
}

.impact {
    color: #FFB020;
    font-size: 14px;
}

.action {
    color: #22C55E;
    font-size: 14px;
}

.alert {
    color: #EF4444;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# SIDEBAR (CONTROL PANEL)
# -------------------------
menu = st.sidebar.radio("", [
    "Command Center",
    "Intake",
    "Operations",
    "Intelligence",
    "Alerts",
    "Ask AI"
])

st.sidebar.markdown("### DistrictOS")
st.sidebar.caption("Enterprise Intelligence System")

if "results" not in st.session_state:
    st.session_state.results = None


# -------------------------
# COMMAND CENTER 🔥
# -------------------------
if menu == "Command Center":

    r = st.session_state.results

    st.markdown("# Command Center")

    if not r:
        st.warning("No data loaded")
    else:
        score = r["district_score"]

        color = "#22C55E" if score > 80 else "#FACC15" if score > 60 else "#EF4444"

        st.markdown(f"""
        <div class="metric-card">
            <h1 style="color:{color}; font-size:48px;">{score}</h1>
            <p>District Health Score</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        col1.metric("Stores", len(r["store_severity"]))
        col2.metric("Patterns", len(r["patterns"]))
        col3.metric("Alerts", len(r["alerts"]))

        st.markdown("---")
        st.caption(r["summary"])


# -------------------------
# INTAKE
# -------------------------
elif menu == "Intake":

    st.markdown("# Data Intake")

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


# -------------------------
# OPERATIONS (PRIORITIES) 🔥
# -------------------------
elif menu == "Operations":

    st.markdown("# Operations")

    r = st.session_state.results

    if r:
        for s in r["priority_stores"]:

            sev = r["store_severity"][s]
            impacts = r["impacts"].get(s, [])

            color = "#EF4444" if sev > 75 else "#FACC15" if sev > 40 else "#22C55E"

            st.markdown(f"""
            <div class="store-card">
                <h3>Store {s}</h3>
                <h2 style="color:{color}">{sev}</h2>
            """, unsafe_allow_html=True)

            # IMPACTS
            for i in impacts:
                st.markdown(f"<p class='impact'>⚠ {i}</p>", unsafe_allow_html=True)

            # ACTIONS
            for a in r["actions"]:
                if s in a:
                    st.markdown(f"<p class='action'>✔ {a}</p>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)


# -------------------------
# INTELLIGENCE (PATTERNS)
# -------------------------
elif menu == "Intelligence":

    st.markdown("# Intelligence")

    r = st.session_state.results

    if r:
        for p in r["patterns"]:
            st.markdown(f"""
            <div class="store-card">
                <h3>{p['metric'].upper()}</h3>
                <p>{p['count']} stores affected</p>
                <p>{", ".join(map(str, p['stores']))}</p>
            </div>
            """, unsafe_allow_html=True)


# -------------------------
# ALERTS 🔥
# -------------------------
elif menu == "Alerts":

    st.markdown("# Alerts")

    r = st.session_state.results

    if r:
        if r["alerts"]:
            for a in r["alerts"]:
                st.markdown(f"<p class='alert'>⚠ {a}</p>", unsafe_allow_html=True)
        else:
            st.success("No active alerts")


# -------------------------
# ASK AI 🔥
# -------------------------
elif menu == "Ask AI":

    st.markdown("# Ask DistrictOS")

    r = st.session_state.results

    if r:
        q = st.text_input("Ask a question")

        if q:
            if "worst" in q:
                st.markdown(f"Focus on Store {r['priority_stores'][0]}")
            elif "fix" in q:
                st.write(r["actions"][:3])
            else:
                st.write("Ask about priorities, risks, or performance")
