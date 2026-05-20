import streamlit as st
import requests

API = "https://districtos.onrender.com/api"

st.set_page_config(layout="wide")

# -------------------------
# SESSION
# -------------------------
if "history" not in st.session_state:
    st.session_state.history = []

menu = st.sidebar.radio("", [
    "Dashboard",
    "Upload",
    "Ask AI",
    "History"
])

st.sidebar.markdown("## DistrictOS")
st.sidebar.caption("Enterprise Platform")


# -------------------------
# DASHBOARD
# -------------------------
if menu == "Dashboard":

    st.title("District Overview")

    if st.session_state.history:
        data = st.session_state.history[-1]

        st.metric("District Score", data["district_score"])
        st.write(data["summary"])

        for s in data["priority_stores"]:
            st.write(f"Store {s}: {data['store_severity'][s]}")
    else:
        st.warning("No data")


# -------------------------
# UPLOAD
# -------------------------
elif menu == "Upload":

    f = st.file_uploader("Upload")

    if st.button("Analyze") and f:

        res = requests.post(
            f"{API}/analyze/upload",
            files={"file": (f.name, f.getvalue())}
        )

        if res.status_code == 200:
            data = res.json()
            st.session_state.history.append(data)
            st.success("Saved")


# -------------------------
# ASK AI (REAL AI)
# -------------------------
elif menu == "Ask AI":

    q = st.text_input("Ask anything about your district")

    if q:
        res = requests.post(f"{API}/ask", json={"question": q})

        if res.status_code == 200:
            st.write(res.json()["response"])


# -------------------------
# HISTORY
# -------------------------
elif menu == "History":

    st.title("Past Analyses")

    for i, h in enumerate(st.session_state.history):
        with st.expander(f"Run {i+1}"):
            st.write(h["summary"])
