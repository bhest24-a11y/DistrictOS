import streamlit as st
import requests

st.set_page_config(layout="wide", page_title="DistrictOS")

API = "https://districtos.onrender.com/api"

# -------------------------
# SIDEBAR
# -------------------------
menu = st.sidebar.radio("DistrictOS", [
    "Command Center",
    "Intake",
    "Priorities",
    "Patterns",
    "Risks",
    "Actions"
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
        st.warning("No data yet.")
    else:
        col1, col2, col3 = st.columns(3)

        col1.metric("Records", results.get("records_found", 0))
        col2.metric("Priority Stores", len(results.get("priority_stores", [])))
        col3.metric("Patterns", len(results.get("patterns", [])))

        st.markdown("---")
        st.info(results.get("summary", ""))


# -------------------------
# INTAKE
# -------------------------
elif menu == "Intake":
    st.header("📥 Data Intake")

    uploaded_file = st.file_uploader("Upload file")
    text_input = st.text_area("Paste report text")

    if st.button("Analyze"):
        if uploaded_file:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }
            res = requests.post(f"{API}/analyze/upload", files=files)

        elif text_input:
            res = requests.post(f"{API}/analyze/text", json={"text": text_input})

        else:
            st.warning("Upload or paste something")
            st.stop()

        if res.status_code == 200:
            st.session_state.results = res.json()
            st.success("Analysis complete")
        else:
            st.error(res.text)


# -------------------------
# PRIORITIES
# -------------------------
elif menu == "Priorities":
    st.header("🔥 Priority Stores")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        for store in results.get("priority_stores", []):

            metrics = results["store_metrics"].get(store, [])
            severity = results["store_severity"].get(store, 0)
            impacts = results.get("impacts", {}).get(store, [])
            actions = results.get("actions", [])

            # COLOR
            if severity > 75:
                color = "🔴"
            elif severity > 40:
                color = "🟡"
            else:
                color = "🟢"

            st.markdown(f"## {color} Store {store}")
            st.metric("Severity Score", severity)

            # METRICS
            if metrics:
                cols = st.columns(len(metrics))
                for i, m in enumerate(metrics):
                    with cols[i]:
                        st.metric(
                            m["metric"].upper(),
                            m["actual"],
                            round(m["variance"], 2) if m["variance"] else 0
                        )

            # WHY
            st.markdown("### 🧠 Why")
            for m in metrics:
                if m["status"] == "off_track":
                    st.error(
                        f"{m['metric'].upper()} off track "
                        f"({m['actual']} vs {m['target']})"
                    )

            # 🔥 WHY THIS MATTERS
            st.markdown("### 💰 Why This Matters")
            for impact in impacts:
                st.warning(impact)

            # ACTIONS
            st.markdown("### ✅ Actions")
            for a in actions:
                if store in a:
                    st.success(a)

            st.markdown("---")


# -------------------------
# PATTERNS
# -------------------------
elif menu == "Patterns":
    st.header("🧠 Pattern Detection")

    results = st.session_state.results

    if results:
        patterns = results.get("patterns", [])

        if not patterns:
            st.success("No patterns detected")
        else:
            for p in patterns:
                st.error(
                    f"{p['metric'].upper()} across {p['count']} stores\n"
                    f"Stores: {', '.join(map(str, p['stores']))}"
                )


# -------------------------
# RISKS
# -------------------------
elif menu == "Risks":
    st.header("⚠️ Risks")

    results = st.session_state.results

    if results:
        for r in results.get("risks", []):
            st.warning(r)


# -------------------------
# ACTIONS
# -------------------------
elif menu == "Actions":
    st.header("✅ Actions")

    results = st.session_state.results

    if results:
        for a in results.get("actions", []):
            st.success(a)
