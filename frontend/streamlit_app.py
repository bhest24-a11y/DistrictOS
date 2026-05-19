import streamlit as st
import requests
import pandas as pd

API = "https://districtos.onrender.com/api"

st.set_page_config(page_title="DistrictOS Capture", layout="wide")

st.title("DistrictOS Capture + Intelligence")
st.caption("Upload it, screenshot it, or show it to DistrictOS — turn messy operational data into priorities.")

def render_output(data):
    st.success("Analysis complete")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("District Health Summary")
        for item in data.get("district_health_summary", []):
            st.write(f"- {item}")

        st.subheader("Highest Priority Stores")
        stores = data.get("highest_priority_stores", [])
        st.write(", ".join(stores) if stores else "No store-level priority detected yet.")

        st.subheader("Risks")
        for item in data.get("risks", []):
            st.write(f"- {item}")

    with c2:
        st.subheader("Likely Root Causes")
        for item in data.get("likely_root_causes", []):
            st.write(f"- {item}")

        st.subheader("Suggested Actions")
        for item in data.get("suggested_actions", []):
            st.write(f"- {item}")

    st.subheader("Cleaned KPI Records")
    records = data.get("cleaned_records", [])
    if records:
        st.dataframe(pd.DataFrame(records), use_container_width=True)

    st.subheader("VP Email Draft")
    st.text_area("Copy/paste VP recap", data.get("vp_email_draft", ""), height=260)

    st.subheader("Huddle Script")
    st.text_area("Copy/paste huddle script", data.get("huddle_script", ""), height=220)

st.warning(
    "Capture rules: user-initiated only, visible recording indicator, redact sensitive fields, "
    "process locally where possible, delete raw recordings after extraction, store cleaned KPI data and summaries only."
)

tab1, tab2, tab3 = st.tabs(["Upload Pictures / Files", "Paste Table Text", "Record Session Upload"])

with tab1:
    st.subheader("Upload pictures, screenshots, Excel, CSV, or video")
    files = st.file_uploader(
        "Drop files here",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg", "webp", "xlsx", "xls", "csv", "mp4", "mov", "avi", "mkv"]
    )
    if st.button("Analyze Uploads", type="primary") and files:
        multipart = [("files", (f.name, f.getvalue(), f.type or "application/octet-stream")) for f in files]
        with st.spinner("DistrictOS is extracting, redacting, normalizing, and analyzing..."):
            r = requests.post(f"{API}/analyze/upload", files=multipart)
        if r.ok:
            render_output(r.json())
        else:
            st.error(r.text)

with tab2:
    st.subheader("Paste copied report/table text")
    text = st.text_area("Paste report text here", height=250)
    if st.button("Analyze Text") and text:
        with st.spinner("Analyzing pasted text..."):
            r = requests.post(f"{API}/analyze/text", data={"text": text})
        if r.ok:
            render_output(r.json())
        else:
            st.error(r.text)

with tab3:
    st.subheader("Record my review session")
    st.info(
        "Browser-level screen recording is normally handled by a web front end using getDisplayMedia. "
        "For this Streamlit MVP, record using your OS tool, then upload the video here. "
        "The backend extracts frames, redacts sensitive text, analyzes them, and deletes raw video after extraction."
    )
    video = st.file_uploader("Upload recorded review session", type=["mp4", "mov", "avi", "mkv"], key="video_only")
    if st.button("Analyze Recording") and video:
        multipart = [("files", (video.name, video.getvalue(), video.type or "application/octet-stream"))]
        with st.spinner("Extracting frames and deleting raw recording after processing..."):
            r = requests.post(f"{API}/analyze/upload", files=multipart)
        if r.ok:
            render_output(r.json())
        else:
            st.error(r.text)
