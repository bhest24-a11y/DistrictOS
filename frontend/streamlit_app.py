import streamlit as st
import requests
import random

st.set_page_config(layout="wide")

# ================================
# 🔥 GLOBAL ELITE STYLE (FULL)
# ================================
st.markdown("""
<style>

/* --- BACKGROUND --- */
body {
    background: radial-gradient(circle at top left, #0f172a, #020617);
    color: #E2E8F0;
}

/* --- SIDEBAR --- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
    border-right: 1px solid #1e293b;
}

/* --- HEADER BAR --- */
.header-bar {
    position: sticky;
    top: 0;
    z-index: 999;
    background: rgba(2,6,23,0.7);
    backdrop-filter: blur(12px);
    padding: 14px 22px;
    border-bottom: 1px solid #1e293b;
    animation: fadeSlide 0.6s ease;
}

/* --- KPI CARD --- */
.kpi-card {
    background: linear-gradient(145deg, #020617, #0f172a);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #1e293b;
    box-shadow: 0 6px 30px rgba(0,0,0,0.6);
    transition: all 0.25s ease;
}
.kpi-card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 12px 40px rgba(0,0,0,0.9);
}

/* --- BIG NUMBER --- */
.kpi-big {
    font-size: 52px;
    font-weight: 700;
    animation: popIn 0.4s ease;
}

/* --- LABEL --- */
.kpi-label {
    font-size: 12px;
    color: #94a3b8;
}

/* --- CARD --- */
.card {
    background: linear-gradient(145deg, #020617, #0f172a);
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #1e293b;
    margin-bottom: 16px;
    transition: all 0.25s ease;
}
.card:hover {
    transform: translateX(6px);
}

/* --- COLORS --- */
.red { color: #ef4444; }
.yellow { color: #facc15; }
.green { color: #22c55e; }

/* --- SHIMMER LOADING --- */
.shimmer {
    height: 20px;
    width: 100%;
    border-radius: 6px;
    background: linear-gradient(
        90deg,
        #020617 25%,
        #1e293b 50%,
        #020617 75%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
}

/* --- ANIMATIONS --- */
@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

@keyframes fadeSlide {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes popIn {
    from { transform: scale(0.9); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(239,68,68,0.6); }
    70% { box-shadow: 0 0 0 12px rgba(239,68,68,0); }
    100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
}

</style>
""", unsafe_allow_html=True)

# ================================
# 🧠 SESSION STATE
# ================================
if "results" not in st.session_state:
    st.session_state.results = None

# ================================
# 📡 BACKEND CALL
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
# 📊 SIDEBAR NAV
# ================================
view = st.sidebar.radio(
    "View",
    ["Command Center", "Operations", "Intelligence", "Alerts", "AI Command", "Intake"]
)

# ================================
# 📥 INTAKE PAGE
# ================================
if view == "Intake":
    st.title("Upload Data")

    text = st.text_area("Paste report text")

    if st.button("Analyze"):
        st.session_state.results = analyze_text(text)

# ================================
# 📊 COMMAND CENTER
# ================================
if view == "Command Center":

    r = st.session_state.results

    st.title("Command Center")

    # ----------------------------
    # 🔥 HEADER BAR
    # ----------------------------
    if r:
        score = r.get("district_score", 75)
        color = "green" if score > 80 else "yellow" if score > 60 else "red"

        st.markdown(f"""
        <div class="header-bar">
            <div class="kpi-label">DISTRICT HEALTH</div>
            <div class="kpi-big {color}">{score}</div>
        </div>
        """, unsafe_allow_html=True)

        # ----------------------------
        # ⚡ LIVE SYSTEM STATUS
        # ----------------------------
        status = random.choice([
            "Analyzing store performance...",
            "Detecting risk patterns...",
            "Scanning execution gaps...",
            "Optimizing district health..."
        ])

        st.markdown(f"""
        <div style="font-size:12px; color:#94a3b8; margin-top:10px;">
        ⚡ {status}
        </div>
        """, unsafe_allow_html=True)

    # ----------------------------
    # 🚫 LOADING STATE
    # ----------------------------
    if not r:
        for _ in range(4):
            st.markdown('<div class="shimmer"></div><br>', unsafe_allow_html=True)
        st.stop()

    # ----------------------------
    # 📈 KPI ROW
    # ----------------------------
    col1, col2, col3 = st.columns(3)

    def kpi(label, value):
        return f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-big">{value}</div>
        </div>
        """

    col1.markdown(kpi("Stores", len(r.get("store_severity", {}))), unsafe_allow_html=True)
    col2.markdown(kpi("Patterns", len(r.get("patterns", []))), unsafe_allow_html=True)
    col3.markdown(kpi("Alerts", len(r.get("alerts", []))), unsafe_allow_html=True)

    st.markdown("---")

    # ----------------------------
    # 🔥 PRIORITY STORES (WITH PULSE)
    # ----------------------------
    st.markdown("### Top Risk Stores")

    for s in r.get("priority_stores", [])[:5]:
        sev = r["store_severity"].get(s, 0)

        color = "red" if sev > 75 else "yellow" if sev > 40 else "green"
        pulse = "animation: pulse 1.5s infinite;" if sev > 75 else ""

        st.markdown(f"""
        <div class="card" style="{pulse}">
            <div class="kpi-label">STORE {s}</div>
            <div class="kpi-big {color}">{sev}</div>
        </div>
        """, unsafe_allow_html=True)

# ================================
# 🚨 ALERTS PAGE
# ================================
if view == "Alerts":
    st.title("Alerts")

    r = st.session_state.results

    if not r:
        st.warning("No data loaded")
    else:
        for alert in r.get("alerts", []):
            st.error(alert)

# ================================
# 🧠 INTELLIGENCE PAGE
# ================================
if view == "Intelligence":
    st.title("Intelligence")

    r = st.session_state.results

    if not r:
        st.warning("No data loaded")
    else:
        st.write(r.get("patterns", []))

# ================================
# ⚙️ OPERATIONS PAGE
# ================================
if view == "Operations":
    st.title("Operations")

    r = st.session_state.results

    if not r:
        st.warning("No data loaded")
    else:
        st.write(r.get("actions", []))

# ================================
# 🤖 AI COMMAND PAGE
# ================================
if view == "AI Command":
    st.title("AI Command")

    r = st.session_state.results

    if not r:
        st.warning("No data loaded")
    else:
        st.write(r.get("summary", ""))
