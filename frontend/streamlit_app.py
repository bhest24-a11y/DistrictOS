import streamlit as st
import requests

st.set_page_config(layout="wide", page_title="DistrictOS")

API = "https://districtos.onrender.com/api"

# -------------------------
# SIDEBAR NAV
# -------------------------
menu = st.sidebar.radio("DistrictOS", [
    "Command Center",
    "Intake",
    "Priorities",
    "Risks",
    "Actions",
    "VP Brief",
    "Huddle"
])

st.sidebar.markdown("---")
st.sidebar.caption("AI District Operating System")

if "results" not in st.session_state:
    st.session_state.results = None


# -------------------------
# COMMAND CENTER
# -------------------------
if menu == "Command Center":
    st.title("🧠 Command Center")

    results = st.session_state.results

    if not results:
        st.warning("No data yet. Go to Intake.")
    else:
        col1, col2, col3 = st.columns(3)

        col1.metric("Records", results.get("records_found", 0))
        col2.metric("Priority Stores", len(results.get("priority_stores", [])))
        col3.metric("Risks", len(results.get("risks", [])))

        st.markdown("---")

        st.subheader("🔥 Top Priorities")
        for s in results.get("priority_stores", [])[:5]:
            st.error(f"{s}")

        st.markdown("---")
        st.subheader("🧠 AI Summary")
        st.info(results.get("summary", ""))


# -------------------------
# INTAKE
# -------------------------
elif menu == "Intake":
    st.header("📥 Data Intake")

    uploaded_file = st.file_uploader(
        "Upload file",
        type=["csv", "xlsx", "xls", "png", "jpg", "jpeg", "mp4", "mov", "avi", "mkv"]
    )

    text_input = st.text_area("Or paste report text")

    if st.button("Analyze"):
        response = None

        if uploaded_file:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            response = requests.post(
                f"{API}/analyze/upload",
                files=files,
                timeout=120
            )

        elif text_input:
            response = requests.post(
                f"{API}/analyze/text",
                json={"text": text_input},
                timeout=120
            )

        else:
            st.warning("Upload a file or paste text.")
            st.stop()

        if response.status_code == 200:
            st.session_state.results = response.json()
            st.success("Analysis complete")
        else:
            st.error(f"Error: {response.status_code}")
            st.text(response.text)


# -------------------------
# 🔥 PRIORITIES (UPGRADED)
# -------------------------
elif menu == "Priorities":
    st.header("🔥 Priority Stores")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        stores = results.get("priority_stores", [])

        if not stores:
            st.success("No critical stores")
        else:
            for store in stores:
                with st.container():
                    col1, col2 = st.columns([2, 1])

                    # LEFT: STORE INFO
                    with col1:
                        st.markdown(f"### 🔴 Store {store}")

                        st.markdown("""
                        **Issues Detected:**
                        - KPI variance detected
                        - Performance off target
                        """)

                    # RIGHT: SEVERITY SCORE (mock for now)
                    with col2:
                        st.metric("Severity", "HIGH")

                    st.markdown("---")


# -------------------------
# RISKS
# -------------------------
elif menu == "Risks":
    st.header("⚠️ Risks")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        for r in results.get("risks", []):
            st.warning(f"⚠️ {r}")


# -------------------------
# ACTIONS
# -------------------------
elif menu == "Actions":
    st.header("✅ Actions")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        for a in results.get("actions", []):
            st.success(f"✅ {a}")


# -------------------------
# VP BRIEF
# -------------------------
elif menu == "VP Brief":
    st.header("👔 VP Brief")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        st.code(results.get("vp_summary", ""), language="markdown")


# -------------------------
# HUDDLE
# -------------------------
elif menu == "Huddle":
    st.header("🗣 Huddle")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        st.code(results.get("huddle", ""), language="markdown")
