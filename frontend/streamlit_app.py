import streamlit as st
import requests
import pandas as pd

API = "https://districtos.onrender.com/api"

st.set_page_config(
    layout="wide",
    page_title="DistrictOS",
    initial_sidebar_state="expanded"
)

# -------------------------
# GLOBAL STYLE (ELITE UI)
# -------------------------
st.markdown("""
<style>
body {
    background: #0B0F17;
    color: #E6EAF2;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0A0D14;
    border-right: 1px solid #1F2937;
}

/* Cards */
.card {
    background: linear-gradient(145deg, #111827, #0B1220);
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #1F2937;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

/* KPI cards */
.kpi {
    font-size: 32px;
    font-weight: 700;
}

/* Labels */
.label {
    font-size: 12px;
    color: #9CA3AF;
}

/* Severity colors */
.red { color: #EF4444; }
.yellow { color: #FACC15; }
.green { color: #22C55E; }

/* Section titles */
.section-title {
    font-size: 18px;
    margin-bottom: 10px;
    color: #CBD5F5;
}

/* Divider spacing */
.divider {
    margin-top: 20px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)


# -------------------------
# SIDEBAR
# -------------------------
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


# -------------------------
# COMMAND CENTER
# -------------------------
if menu == "Command Center":

    st.markdown("# Command Center")

    r = st.session_state.results

    if not r:
        st.warning("No data loaded")
    else:
        score = r["district_score"]

        color_class = "green" if score > 80 else "yellow" if score > 60 else "red"

        st.markdown(f"""
        <div class="card">
            <div class="label">DISTRICT HEALTH</div>
            <div class="kpi {color_class}">{score}</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        col1.markdown(f"""
        <div class="card">
            <div class="label">Stores</div>
            <div class="kpi">{len(r["store_severity"])}</div>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class="card">
            <div class="label">Patterns</div>
            <div class="kpi">{len(r["patterns"])}</div>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div class="card">
            <div class="label">Alerts</div>
            <div class="kpi">{len(r["alerts"])}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
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
# OPERATIONS (ELITE)
# -------------------------
elif menu == "Operations":

    st.markdown("# Operations")

    r = st.session_state.results

    if r:
        for s in r["priority_stores"]:

            sev = r["store_severity"][s]
            impacts = r["impacts"].get(s, [])

            color_class = "red" if sev > 75 else "yellow" if sev > 40 else "green"

            st.markdown(f"""
            <div class="card">
                <div class="label">STORE {s}</div>
                <div class="kpi {color_class}">{sev}</div>
            """, unsafe_allow_html=True)

            # Trend sparkline (mini chart)
            trend = r.get("trend_memory", {}).get(s, [])
            if trend:
                df = pd.DataFrame(trend)
                st.line_chart(df["severity"], height=100)

            # Impacts
            st.markdown("<div class='section-title'>Impact</div>", unsafe_allow_html=True)
            for i in impacts:
                st.warning(i)

            # Actions
            st.markdown("<div class='section-title'>Actions</div>", unsafe_allow_html=True)
            for a in r["actions"]:
                if s in a:
                    st.success(a)

            st.markdown("</div>", unsafe_allow_html=True)


# -------------------------
# INTELLIGENCE
# -------------------------
elif menu == "Intelligence":

    st.markdown("# Intelligence")

    r = st.session_state.results

    if r:
        for p in r["patterns"]:
            st.markdown(f"""
            <div class="card">
                <div class="label">{p['metric'].upper()}</div>
                <div class="kpi">{p['count']} stores</div>
                <div class="label">{", ".join(map(str, p['stores']))}</div>
            </div>
            """, unsafe_allow_html=True)


# -------------------------
# ALERTS
# -------------------------
elif menu == "Alerts":

    st.markdown("# Alerts")

    r = st.session_state.results

    if r:
        if r["alerts"]:
            for a in r["alerts"]:
                st.error(a)
        else:
            st.success("No active alerts")


# -------------------------
# ASK AI (UPGRADED FEEL)
# -------------------------
elif menu == "Ask AI":

    st.markdown("# Ask DistrictOS")

    r = st.session_state.results

    if r:
        q = st.text_input("Ask a question")

        if q:
            with st.spinner("Thinking..."):
                if "worst" in q.lower():
                    st.markdown(f"### Focus on Store {r['priority_stores'][0]}")
                elif "fix" in q.lower():
                    for a in r["actions"][:3]:
                        st.write(a)
                else:
                    st.write("Try: 'worst store' or 'what should I fix'")
