import streamlit as st
import requests
import random
import pandas as pd

st.set_page_config(layout="wide")

# ================================
# 🔥 GLOBAL STYLE (KEEP ELITE)
# ================================
st.markdown("""
<style>
body { background: radial-gradient(circle at top left, #0f172a, #020617); color: #E2E8F0; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #020617, #0f172a); border-right: 1px solid #1e293b; }

.header-bar {
    position: sticky; top: 0; z-index: 999;
    background: rgba(2,6,23,0.7);
    backdrop-filter: blur(12px);
    padding: 14px 22px;
    border-bottom: 1px solid #1e293b;
}

.kpi-card {
    background: linear-gradient(145deg, #020617, #0f172a);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #1e293b;
    transition: 0.25s;
}
.kpi-card:hover { transform: translateY(-6px); }

.kpi-big { font-size: 48px; font-weight: 700; }
.kpi-label { font-size: 12px; color: #94a3b8; }

.card {
    background: linear-gradient(145deg, #020617, #0f172a);
    padding: 14px;
    border-radius: 12px;
    border: 1px solid #1e293b;
    margin-bottom: 10px;
    cursor: pointer;
}

.red { color: #ef4444; }
.yellow { color: #facc15; }
.green { color: #22c55e; }

</style>
""", unsafe_allow_html=True)

# ================================
# 🧠 STATE
# ================================
if "results" not in st.session_state:
    st.session_state.results = None

if "selected_store" not in st.session_state:
    st.session_state.selected_store = None

# ================================
# 📡 BACKEND
# ================================
def analyze_text(text):
    try:
        res = requests.post(
            "http://localhost:8000/analyze/text",
            json={"text": text}
        )
        return res.json()
    except:
        return None

# ================================
# 📊 SIDEBAR
# ================================
view = st.sidebar.radio(
    "View",
    ["Command Center", "Store Drilldown", "Intelligence", "Alerts", "Intake"]
)

# ================================
# 📥 INTAKE
# ================================
if view == "Intake":
    st.title("Upload Data")

    text = st.text_area("Paste report text")

    if st.button("Analyze"):
        st.session_state.results = analyze_text(text)

# ================================
# 🧠 COMMAND CENTER
# ================================
if view == "Command Center":

    r = st.session_state.results
    st.title("Command Center")

    if not r:
        st.warning("Load data first")
        st.stop()

    # HEADER
    score = r.get("district_score", 75)
    color = "green" if score > 80 else "yellow" if score > 60 else "red"

    st.markdown(f"""
    <div class="header-bar">
        <div class="kpi-label">DISTRICT HEALTH</div>
        <div class="kpi-big {color}">{score}</div>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    col1, col2, col3 = st.columns(3)

    col1.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Stores</div>
        <div class="kpi-big">{len(r.get("store_severity", {}))}</div>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Patterns</div>
        <div class="kpi-big">{len(r.get("patterns", []))}</div>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Alerts</div>
        <div class="kpi-big">{len(r.get("alerts", []))}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # CLICKABLE STORES
    st.markdown("### Top Risk Stores")

    for s in r.get("priority_stores", [])[:10]:
        sev = r["store_severity"].get(s, 0)

        color = "red" if sev > 75 else "yellow" if sev > 40 else "green"

        if st.button(f"Store {s} — {sev}", key=f"store_{s}"):
            st.session_state.selected_store = s
            st.switch_page("Store Drilldown")

# ================================
# 🏪 STORE DRILLDOWN (🔥 BIG FEATURE)
# ================================
if view == "Store Drilldown":

    r = st.session_state.results
    store = st.session_state.selected_store

    st.title(f"Store Drilldown: {store}")

    if not store or not r:
        st.warning("Select a store from Command Center")
        st.stop()

    sev = r["store_severity"].get(store, 0)

    # STORE KPI
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">STORE HEALTH</div>
        <div class="kpi-big">{sev}</div>
    </div>
    """, unsafe_allow_html=True)

    # MOCK TREND DATA (replace later with real DB)
    trend = pd.DataFrame({
        "Day": ["Mon","Tue","Wed","Thu","Fri"],
        "Score": [random.randint(50,90) for _ in range(5)]
    })

    st.line_chart(trend.set_index("Day"))

# ================================
# 🧠 INTELLIGENCE PANEL
# ================================
if view == "Intelligence":

    r = st.session_state.results
    st.title("Intelligence")

    if not r:
        st.warning("No data")
        st.stop()

    st.markdown("### Detected Patterns")

    for p in r.get("patterns", []):
        st.info(p)

    st.markdown("### AI Insight")

    st.success(r.get("summary", "No summary available"))

# ================================
# 🚨 ALERTS PANEL (UPGRADED)
# ================================
if view == "Alerts":

    r = st.session_state.results
    st.title("Alerts")

    if not r:
        st.warning("No data")
        st.stop()

    for alert in r.get("alerts", []):
        if "critical" in alert.lower():
            st.error(alert)
        elif "warning" in alert.lower():
            st.warning(alert)
        else:
            st.info(alert)
