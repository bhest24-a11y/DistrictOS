import streamlit as st
import requests
import random
import pandas as pd
import re
from datetime import datetime

st.set_page_config(layout="wide")

# ================================
# GLOBAL STYLE
# ================================
st.markdown("""
<style>
body { background: radial-gradient(circle at top left, #0f172a, #020617); color: #E2E8F0; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
    border-right: 1px solid #1e293b;
}

.header-bar {
    background: rgba(2,6,23,0.7);
    padding: 16px;
    border-bottom: 1px solid #1e293b;
}

.card {
    background: linear-gradient(145deg, #020617, #0f172a);
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #1e293b;
    margin-bottom: 12px;
}

.kpi-big { font-size: 48px; font-weight: 700; }
.kpi-label { font-size: 12px; color: #94a3b8; }

.red { color: #ef4444; }
.yellow { color: #facc15; }
.green { color: #22c55e; }
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

API_BASE = "http://127.0.0.1:8000/api"

# ================================
# BACKEND CALL
# ================================
def analyze_text(text):
    try:
        res = requests.post(f"{API_BASE}/analyze/text", json={"text": text})
        return res.json()
    except:
        return None

# ================================
# SIDEBAR
# ================================
view = st.sidebar.radio("View", [
    "Command Center",
    "Store Drilldown",
    "Intelligence",
    "Alerts",
    "Intake",
    "AI Chat",
    "History"
])

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
        st.info("Upload data first")
        st.stop()

    score = r.get("district_score", 75)
    color = "green" if score > 80 else "yellow" if score > 60 else "red"

    st.markdown(f"""
    <div class="header-bar">
        <div class="kpi-label">DISTRICT HEALTH</div>
        <div class="kpi-big {color}">{score}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
    {r.get("summary", "No summary")}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🚨 Top Risk Stores")

    for s in r.get("priority_stores", [])[:5]:
        sev = r["store_severity"].get(s, 0)

        if st.button(f"Store {s} — {sev}"):
            st.session_state.selected_store = s

# ================================
# STORE DRILLDOWN (REAL AI)
# ================================
if view == "Store Drilldown":

    r = st.session_state.results
    store = st.session_state.selected_store

    st.title(f"Store Drilldown: {store}")

    if not store or not r:
        st.warning("Select a store first")
        st.stop()

    st.metric("Store Health", r["store_severity"].get(store, 0))

    if st.button("Analyze Store"):

        res = requests.post(
            f"{API_BASE}/store/analyze",
            json={
                "store_id": store,
                "context": r.get("raw_text", "")
            }
        ).json()

        st.markdown(f"""
        <div class="card">
        {res.get("insight")}
        </div>
        """, unsafe_allow_html=True)

# ================================
# INTELLIGENCE
# ================================
if view == "Intelligence":

    r = st.session_state.results

    if not r:
        st.warning("No data")
        st.stop()

    sections = re.split(r"###+", r.get("summary", ""))

    for section in sections:
        if section.strip():
            st.markdown(f"<div class='card'>{section}</div>", unsafe_allow_html=True)

# ================================
# ALERTS
# ================================
if view == "Alerts":

    r = st.session_state.results

    if not r:
        st.warning("No data")
        st.stop()

    for alert in r.get("alerts", []):
        st.warning(alert)

# ================================
# AI CHAT
# ================================
if view == "AI Chat":

    st.title("AI Assistant")

    q = st.text_input("Ask a question")

    if st.button("Ask") and q:

        res = requests.post(
            f"{API_BASE}/chat",
            json={"question": q, "context": st.session_state.chat_history}
        ).json()

        st.session_state.chat_history += f"\nQ: {q}\nA: {res.get('response')}"

    st.text_area("Conversation", st.session_state.chat_history, height=300)

# ================================
# HISTORY
# ================================
if view == "History":

    st.title("History")

    try:
        res = requests.get(f"{API_BASE}/history").json()

        for item in res:
            st.markdown(f"""
            <div class="card">
                <div class="kpi-label">{item['created_at']}</div>
                {item['summary'][:200]}
            </div>
            """, unsafe_allow_html=True)

    except:
        st.error("Failed to load history")