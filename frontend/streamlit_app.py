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
        st.warning("No data yet. Go to Intake.")
    else:
        col1, col2, col3 = st.columns(3)

        col1.metric("Records", results.get("records_found", 0))
        col2.metric("Priority Stores", len(results.get("priority_stores", [])))
        col3.metric("Patterns", len(results.get("patterns", [])))

        st.markdown("---")

        st.subheader("🔥 Top Priority Stores")
        for s in results.get("priority_stores", [])[:5]:
            st.error(f"Store {s}")

        st.markdown("---")

        st.subheader("🧠 Summary")
        st.info(results.get("summary", ""))


# -------------------------
# INTAKE
# -------------------------
elif menu == "Intake":
    st.header("📥 Data Intake")

    uploaded_file = st.file_uploader(
        "Upload file",
        type=["csv", "xlsx", "xls", "png", "jpg", "jpeg", "mp4", "mov"]
    )

    text_input = st.text_area("Or paste report text")

    if st.button("Analyze"):
        if uploaded_file:
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }

            res = requests.post(
                f"{API}/analyze/upload",
                files=files,
                timeout=120
            )

        elif text_input:
            res = requests.post(
                f"{API}/analyze/text",
                json={"text": text_input},
                timeout=120
            )

        else:
            st.warning("Upload or paste something")
            st.stop()

        if res.status_code == 200:
            st.session_state.results = res.json()
            st.success("Analysis complete")
        else:
            st.error(res.text)


# -------------------------
# 🔥 PRIORITIES (FINAL)
# -------------------------
elif menu == "Priorities":
    st.header("🔥 Priority Stores")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        stores = results.get("priority_stores", [])
        metrics_data = results.get("store_metrics", {})
        severity_data = results.get("store_severity", {})
        actions = results.get("actions", [])

        if not stores:
            st.success("No critical stores")
        else:
            for store in stores:
                metrics = metrics_data.get(store, [])
                severity = severity_data.get(store, 0)

                # COLOR LOGIC
                if severity > 75:
                    color = "🔴"
                elif severity > 40:
                    color = "🟡"
                else:
                    color = "🟢"

                with st.container():
                    st.markdown(f"## {color} Store {store}")
                    st.metric("Severity Score", severity)

                    # METRICS GRID
                    if metrics:
                        cols = st.columns(len(metrics))
                        for i, m in enumerate(metrics):
                            with cols[i]:
                                variance = round(m["variance"], 2) if m["variance"] else 0

                                st.metric(
                                    m["metric"].upper(),
                                    f"{m['actual']}",
                                    f"{variance}"
                                )

                    # WHY
                    st.markdown("### 🧠 Why This Store is Flagged")
                    flagged = False

                    for m in metrics:
                        if m["status"] == "off_track":
                            flagged = True
                            st.error(
                                f"{m['metric'].upper()} off track "
                                f"(Actual: {m['actual']} vs Target: {m['target']})"
                            )

                    if not flagged:
                        st.info("No major KPI issues detected")

                    # ACTIONS
                    st.markdown("### ✅ Actions")
                    store_actions = [a for a in actions if store in a]

                    if store_actions:
                        for a in store_actions:
                            st.success(a)
                    else:
                        st.info("No actions available")

                    st.markdown("---")


# -------------------------
# 🧠 PATTERNS
# -------------------------
elif menu == "Patterns":
    st.header("🧠 Pattern Detection")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        patterns = results.get("patterns", [])

        if not patterns:
            st.success("No cross-store patterns detected")
        else:
            for p in patterns:
                st.error(
                    f"{p['metric'].upper()} across {p['count']} stores\n\n"
                    f"Stores: {', '.join([str(s) for s in p['stores']])}"
                )


# -------------------------
# RISKS
# -------------------------
elif menu == "Risks":
    st.header("⚠️ Risks & Signals")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        patterns = results.get("patterns", [])

        if patterns:
            st.subheader("🔥 Detected Patterns")
            for p in patterns:
                st.error(
                    f"{p['metric'].upper()} affecting {len(p['stores'])} stores"
                )

        st.markdown("---")

        risks = results.get("risks", [])
        if risks:
            for r in risks:
                st.warning(r)
        else:
            st.success("No major risks detected")


# -------------------------
# ACTIONS
# -------------------------
elif menu == "Actions":
    st.header("✅ Actions")

    results = st.session_state.results

    if not results:
        st.warning("No data yet.")
    else:
        actions = results.get("actions", [])

        if actions:
            for a in actions:
                st.success(a)
        else:
            st.info("No actions generated")
