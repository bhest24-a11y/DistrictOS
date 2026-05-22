import streamlit as st
import requests
import re

st.set_page_config(layout="wide")

API_BASE = "http://127.0.0.1:8000/api"

if "results" not in st.session_state:
    st.session_state.results = None

if "selected_store" not in st.session_state:
    st.session_state.selected_store = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = ""

# =========================
# ANALYZE
# =========================
def analyze_text(text):
    try:
        res = requests.post(f"{API_BASE}/analyze/text", json={"text": text})
        return res.json()
    except:
        return None

# =========================
# SIDEBAR
# =========================
view = st.sidebar.radio("View", [
    "Command Center",
    "Store Drilldown",
    "Intake",
    "AI Chat"
])

# =========================
# INTAKE
# =========================
if view == "Intake":
    text = st.text_area("Paste report text")

    if st.button("Analyze"):
        st.session_state.results = analyze_text(text)

# =========================
# COMMAND CENTER
# =========================
if view == "Command Center":

    r = st.session_state.results

    if not r:
        st.warning("Upload data first")
        st.stop()

    st.title("District Overview")

    st.metric("District Score", r.get("district_score"))

    st.markdown("### Summary")
    st.markdown(r.get("summary"))

    st.markdown("### Top Stores")
    for s in r.get("priority_stores", [])[:5]:
        sev = r["store_severity"].get(s, 0)
        if st.button(f"Store {s} ({sev})"):
            st.session_state.selected_store = s

    st.markdown("### Key Actions 🔥")
    for a in r.get("actions", []):
        st.markdown(f"- {a}")

# =========================
# STORE DRILLDOWN
# =========================
if view == "Store Drilldown":

    r = st.session_state.results
    store = st.session_state.selected_store

    if not store:
        st.warning("Select a store")
        st.stop()

    st.title(f"Store {store}")

    st.metric("Health", r["store_severity"].get(store))

    st.markdown("### Impacts")
    for i in r.get("impacts", {}).get(store, []):
        st.markdown(f"- {i}")

    if st.button("Run AI Analysis"):
        res = requests.post(
            f"{API_BASE}/store/analyze",
            json={"store_id": store, "context": r.get("raw_text")}
        ).json()

        st.markdown(res.get("insight"))

# =========================
# AI CHAT
# =========================
if view == "AI Chat":

    q = st.text_input("Ask a question")

    if st.button("Ask") and q:
        res = requests.post(
            f"{API_BASE}/chat",
            json={"question": q, "context": st.session_state.chat_history}
        ).json()

        st.session_state.chat_history += f"\nQ: {q}\nA: {res.get('response')}"

    st.text_area("Chat", st.session_state.chat_history)