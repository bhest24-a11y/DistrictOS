import streamlit as st
import requests

API = "https://districtos.onrender.com/api"

st.set_page_config(layout="wide")

# -------------------------
# STATE
# -------------------------
if "results" not in st.session_state:
    st.session_state.results = None

# -------------------------
# 🔥 GLOBAL STYLE (TOP 1% LOOK)
# -------------------------
st.markdown("""
<style>

/* BACKGROUND */
body {
    background: radial-gradient(circle at top left, #0f172a, #020617);
    color: #E2E8F0;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
    border-right: 1px solid #1e293b;
}

/* SIDEBAR TEXT */
section[data-testid="stSidebar"] label {
    font-size: 14px;
    font-weight: 500;
    color: #cbd5f5;
}

/* HEADER BAR */
.header-bar {
    position: sticky;
    top: 0;
    z-index: 999;
    background: rgba(2,6,23,0.7);
    backdrop-filter: blur(10px);
    padding: 12px 20px;
    border-bottom: 1px solid #1e293b;
}

/* KPI CARD */
.kpi-card {
    background: linear-gradient(145deg, #020617, #0f172a);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #1e293b;
    box-shadow: 0 6px 30px rgba(0,0,0,0.6);
}

/* BIG NUMBER */
.kpi-big {
    font-size: 52px;
    font-weight: 700;
}

/* LABEL */
.kpi-label {
    font-size: 12px;
    color: #94a3b8;
}

/* CARD */
.card {
    background: linear-gradient(145deg, #020617, #0f172a);
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #1e293b;
    margin-bottom: 16px;
}

/* COLORS */
.red { color: #ef4444; }
.yellow { color: #facc15; }
.green { color: #22c55e; }

</style>
""", unsafe_allow_html=True)

# -------------------------
# SIDEBAR NAV
# -------------------------
menu = st.sidebar.radio("", [
    "Command Center",
    "Operations",
    "AI Command",
    "Intake"
])

st.sidebar.markdown("## DistrictOS")
st.sidebar.caption("Enterprise Intelligence System")

r = st.session_state.results

# -------------------------
# 🔥 STICKY EXECUTIVE HEADER
# -------------------------
if r:
    score = r["district_score"]

    color = "green" if score > 80 else "yellow" if score > 60 else "red"

    st.markdown(f"""
    <div class="header-bar">
        <span style="font-size:14px; color:#94a3b8;">DISTRICT HEALTH</span><br>
        <span class="kpi-big {color}">{score}</span>
    </div>
    """, unsafe_allow_html=True)

# -------------------------
# COMMAND CENTER
# -------------------------
if menu == "Command Center":

    st.title("Command Center")

    if not r:
        st.warning("No data loaded")
    else:
        # 🔥 EXECUTIVE OVERVIEW
        st.markdown("## Overview")

        col1, col2, col3 = st.columns(3)

        col1.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Stores</div>
            <div class="kpi-big">{len(r["store_severity"])}</div>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Patterns</div>
            <div class="kpi-big">{len(r["patterns"])}</div>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Alerts</div>
            <div class="kpi-big">{len(r["alerts"])}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # 🔥 PRIORITY STORES
        st.markdown("### Top Risk Stores")

        for s in r["priority_stores"][:3]:
            sev = r["store_severity"][s]

            color = "red" if sev > 75 else "yellow" if sev > 40 else "green"

            st.markdown(f"""
            <div class="card">
                <div class="kpi-label">STORE {s}</div>
                <div class="kpi-big {color}">{sev}</div>
            </div>
            """, unsafe_allow_html=True)

# -------------------------
# OPERATIONS
# -------------------------
elif menu == "Operations":

    st.title("Operations")

    if r:
        store = st.selectbox("Select Store", r["priority_stores"])

        sev = r["store_severity"][store]
        metrics = r["store_metrics"][store]
        impacts = r["impacts"].get(store, [])

        st.markdown(f"""
        <div class="card">
            <div class="kpi-label">STORE {store}</div>
            <div class="kpi-big">{sev}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Metrics")

        for m in metrics:
            st.markdown(f"""
            <div class="card">
                <div class="kpi-label">{m['metric']}</div>
                <div class="kpi-big">{m['actual']}</div>
                <div class="kpi-label">Target {m['target']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### Impact")
        for i in impacts:
            st.error(i)

        st.markdown("### Actions")
        for a in r["actions"]:
            if store in a:
                st.success(a)

# -------------------------
# AI COMMAND
# -------------------------
elif menu == "AI Command":

    st.title("AI Command")

    if r:
        q = st.text_input("Ask a question")

        if q:
            res = requests.post(f"{API}/ask", json={"question": q})

            if res.status_code == 200:
                st.markdown(f"""
                <div class="card">
                    <div class="kpi-label">AI RESPONSE</div>
                    <p>{res.json()["response"]}</p>
                </div>
                """, unsafe_allow_html=True)

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
