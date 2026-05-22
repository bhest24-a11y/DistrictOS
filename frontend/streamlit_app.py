import streamlit as st
import requests
import random
import pandas as pd
import re

st.set_page_config(layout="wide")

# ================================
# 🔥 GLOBAL STYLE (YOUR FINAL + MERGED)
# ================================
st.markdown("""
<style>
body { background: radial-gradient(circle at top left, #0f172a, #020617); color: #E2E8F0; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
    border-right: 1px solid #1e293b;
}

/* HEADER */
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

/* KPI */
.kpi-card {
    background: linear-gradient(145deg, #020617, #0f172a);
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #1e293b;
    transition: all 0.25s ease;
}
.kpi-card:hover {
    transform: translateY(-6px) scale(1.02);
}

/* TEXT */
.kpi-big {
    font-size: 52px;
    font-weight: 700;
    animation: popIn 0.4s ease;
}
.kpi-label {
    font-size: 12px;
    color: #94a3b8;
}

/* CARDS */
.card {
    background: linear-gradient(145deg, #020617, #0f172a);
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #1e293b;
    margin-bottom: 12px;
    transition: 0.25s;
}
.card:hover {
    transform: translateX(6px);
}

/* COLORS */
.red { color: #ef4444; }
.yellow { color: #facc15; }
.green { color: #22c55e; }

/* SHIMMER */
.shimmer {
    height: 20px;
    width: 100%;
    border-radius: 6px;
    background: linear-gradient(90deg, #020617 25%, #1e293b 50%, #020617 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
}

/* ANIMATIONS */
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
# STATE
# ================================
if "results" not in st.session_state:
    st.session_state.results = None

if "selected_store" not in st.session_state:
    st.session_state.selected_store = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = ""

# ================================
# BACKEND
# ================================
def analyze_text(text):
    try:
        res = requests.post(
            "http://127.0.0.1:8000/api/analyze/text",  # ✅ FIXED ROUTE
            json={"text": text}
        )
        return res.json()
    except:
        return None

# ================================
# SIDEBAR (UPDATED)
# ================================
view = st.sidebar.radio(
    "View",
    [
        "Command Center",
        "Store Drilldown",
        "Intelligence",
        "Alerts",
        "Intake",
        "AI Chat",
        "History"
    ]
)

# ================================
# INTAKE
# ================================
if view == "Intake":
    st.title("Upload Data")

    text = st.text_area("Paste report text")

    if st.button("Analyze"):
        st.session_state.results = analyze_text(text)

# ================================
# COMMAND CENTER
# ================================
if view == "Command Center":

    r = st.session_state.results
    st.title("Command Center")

    if not r:
        for _ in range(4):
            st.markdown('<div class="shimmer"></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
        st.stop()

    score = r.get("district_score", 75)
    color = "green" if score > 80 else "yellow" if score > 60 else "red"

    st.markdown(f"""
    <div class="header-bar">
        <div class="kpi-label">DISTRICT HEALTH</div>
        <div class="kpi-big {color}">{score}</div>
    </div>
    """, unsafe_allow_html=True)

    status = random.choice([
        "Analyzing store performance...",
        "Detecting risk patterns...",
        "Scanning execution gaps...",
        "Optimizing district health..."
    ])

    st.markdown(f"""
    <div style="font-size:12px; color:#94a3b8; margin-bottom:10px;">
    ⚡ {status}
    </div>
    """, unsafe_allow_html=True)

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

        if st.button(f"Open Store {s}", key=f"btn_{s}"):
            st.session_state.selected_store = s

# ================================
# STORE DRILLDOWN
# ================================
if view == "Store Drilldown":

    r = st.session_state.results
    store = st.session_state.selected_store

    st.title(f"Store Drilldown: {store}")

    if not store or not r:
        st.warning("Select a store first")
        st.stop()

    sev = r["store_severity"].get(store, 0)

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">STORE HEALTH</div>
        <div class="kpi-big">{sev}</div>
    </div>
    """, unsafe_allow_html=True)

    trend = pd.DataFrame({
        "Day": ["Mon","Tue","Wed","Thu","Fri"],
        "Score": [random.randint(50,90) for _ in range(5)]
    })

    st.line_chart(trend.set_index("Day"))

# ================================
# INTELLIGENCE
# ================================
if view == "Intelligence":

    r = st.session_state.results
    st.title("Intelligence")

    if not r:
        st.warning("No data")
        st.stop()

    st.markdown("### AI Executive Summary")

    summary = r.get("summary", "")
    sections = re.split(r"###+", summary)

    for section in sections:
        if section.strip():
            st.markdown(f"""
            <div class="card">
            {section}
            </div>
            """, unsafe_allow_html=True)

# ================================
# ALERTS
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

# ================================
# 🧠 AI CHAT
# ================================
if view == "AI Chat":

    st.title("🧠 AI Data Assistant")

    question = st.text_input("Ask about your data")

    if st.button("Ask") and question:
        res = requests.post(
            "http://127.0.0.1:8000/api/chat",
            json={
                "question": question,
                "context": st.session_state.chat_history
            }
        ).json()

        answer = res.get("response", "No response")

        st.session_state.chat_history += f"\n\nQ: {question}\nA: {answer}"

    st.markdown(f"""
    <div class="card">{st.session_state.chat_history}</div>
    """, unsafe_allow_html=True)

# ================================
# 📊 HISTORY
# ================================
if view == "History":

    st.title("📊 Past Analyses")

    try:
        res = requests.get("http://127.0.0.1:8000/api/history").json()

        for item in res:
            st.markdown(f"""
            <div class="card">
                <div class="kpi-label">{item['created_at']}</div>
                {item['summary']}
            </div>
            """, unsafe_allow_html=True)

    except:
        st.error("Could not load history")