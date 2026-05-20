import streamlit as st
import requests

st.set_page_config(layout="wide", page_title="DistrictOS")

API = "https://districtos.onrender.com/api"

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

if "results" not in st.session_state:
    st.session_state.results = None


if menu == "Home":
    st.title("DistrictOS")
    st.subheader("AI-Powered District Intelligence")

    st.markdown("""
    Upload messy data, screenshots, reports, or paste raw text.

    DistrictOS will:
    - Extract KPI data
    - Identify risks
    - Prioritize stores
    - Generate actions
    - Create VP summaries
    - Create huddle scripts
    """)


elif menu == "Upload":
    st.header("Upload Data")

    uploaded_file = st.file_uploader(
        "Upload file (CSV, Excel, Image)",
        type=["csv", "xlsx", "xls", "png", "jpg", "jpeg", "mp4", "mov", "avi", "mkv"]
    )

    text_input = st.text_area("Or paste raw report text")

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
            st.json(st.session_state.results)
        else:
            st.error(f"Error processing data: {response.status_code}")
            st.text(response.text)


elif menu == "District Health":
    st.header("District Health Summary")

    results = st.session_state.results

    if not results:
        st.warning("No data yet. Upload data first.")
    else:
        st.subheader(results.get("summary", "No summary available."))

        records_found = results.get("records_found")
        if records_found is not None:
            st.metric("Records Found", records_found)

        raw_text = results.get("raw_text_preview")
        if raw_text:
            with st.expander("Raw Extracted Text Preview"):
                st.text(raw_text)


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


elif menu == "Actions":
    st.header("Action Plan")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        actions = results.get("actions", [])

        if not actions:
            st.info("No actions generated.")
        else:
            for a in actions:
                st.write(f"✅ {a}")


elif menu == "VP Recap":
    st.header("VP Summary")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        st.code(results.get("vp_summary", "No VP summary generated."), language="markdown")


elif menu == "Huddle":
    st.header("Huddle Script")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        st.code(results.get("huddle", "No huddle script generated."), language="markdown")
