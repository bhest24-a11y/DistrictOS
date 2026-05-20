import streamlit as st
import requests

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(layout="wide", page_title="DistrictOS")

API = "https://districtos.onrender.com/api"

# -------------------------
# SIDEBAR NAVIGATION
# -------------------------
menu = st.sidebar.radio("DistrictOS", [
    "Home",
    "Upload",
    "District Health",
    "Store Priorities",
    "Risks",
    "Actions",
    "VP Recap",
    "Huddle"
])

st.sidebar.markdown("---")
st.sidebar.caption("AI District Operating System")

# -------------------------
# SESSION STATE
# -------------------------
if "results" not in st.session_state:
    st.session_state.results = None

# -------------------------
# HOME
# -------------------------
if menu == "Home":
    st.title("DistrictOS")
    st.subheader("AI-Powered District Intelligence")

    st.markdown("""
    Upload messy data, screenshots, or reports.

    DistrictOS will:
    - Extract KPI data
    - Identify risks
    - Prioritize stores
    - Generate actions
    - Create VP summaries + huddles
    """)

# -------------------------
# UPLOAD
# -------------------------
elif menu == "Upload":
    st.header("Upload Data")

    uploaded_file = st.file_uploader(
        "Upload file (CSV, Excel, Image)",
        type=["csv", "xlsx", "xls", "png", "jpg", "jpeg"]
    )

    text_input = st.text_area("Or paste raw report text")

    if st.button("Analyze"):
        if uploaded_file:
            files = {"file": uploaded_file.getvalue()}

            response = requests.post(f"{API}/analyze/upload", files=files)

        elif text_input:
            response = requests.post(
                f"{API}/analyze/text",
                json={"text": text_input}
            )
        else:
            st.warning("Upload a file or paste text.")
            st.stop()

        if response.status_code == 200:
            st.session_state.results = response.json()
            st.success("Analysis complete")
        else:
            st.error("Error processing data")

# -------------------------
# DISTRICT HEALTH
# -------------------------
elif menu == "District Health":
    st.header("District Health Summary")

    results = st.session_state.results

    if not results:
        st.warning("No data yet. Upload data first.")
    else:
        st.metric("Summary", results.get("summary", ""))

# -------------------------
# STORE PRIORITIES
# -------------------------
elif menu == "Store Priorities":
    st.header("Priority Stores")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        stores = results.get("priority_stores", [])

        if not stores:
            st.info("No priority stores detected.")
        else:
            for s in stores:
                st.write(f"🔥 {s}")

# -------------------------
# RISKS
# -------------------------
elif menu == "Risks":
    st.header("Risks")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        risks = results.get("risks", [])

        if not risks:
            st.info("No risks detected.")
        else:
            for r in risks:
                st.write(f"⚠️ {r}")

# -------------------------
# ACTIONS
# -------------------------
elif menu == "Actions":
    st.header("Action Plan")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        actions = results.get("actions", [])

        for a in actions:
            st.write(f"✅ {a}")

# -------------------------
# VP RECAP
# -------------------------
elif menu == "VP Recap":
    st.header("VP Summary")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        st.code(results.get("vp_summary", ""), language="markdown")

# -------------------------
# HUDDLE
# -------------------------
elif menu == "Huddle":
    st.header("Huddle Script")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        st.code(results.get("huddle", ""), language="markdown")
