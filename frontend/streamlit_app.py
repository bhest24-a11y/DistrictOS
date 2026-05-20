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
    "Risks",
    "Actions"
])

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
        col3.metric("Risks", len(results.get("risks", [])))

        st.markdown("---")

        for s in results.get("priority_stores", [])[:5]:
            st.error(f"Store {s}")

        st.markdown("---")
        st.info(results.get("summary", ""))


# -------------------------
# INTAKE
# -------------------------
elif menu == "Intake":
    st.header("Upload Data")

    uploaded_file = st.file_uploader("Upload file")
    text_input = st.text_area("Or paste text")

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
            st.success("Done")
        else:
            st.error(res.text)


# -------------------------
# 🔥 PRIORITIES (FINAL VERSION)
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

        for store in stores:
            metrics = metrics_data.get(store, [])
            severity = severity_data.get(store, 0)

            # COLOR
            if severity > 75:
                color = "🔴"
            elif severity > 40:
                color = "🟡"
            else:
                color = "🟢"

            with st.container():
                st.markdown(f"## {color} Store {store}")
                st.metric("Severity Score", severity)

                cols = st.columns(len(metrics) if metrics else 1)

                # METRICS
                for i, m in enumerate(metrics):
                    with cols[i]:
                        variance = round(m["variance"], 2) if m["variance"] else 0

                        st.metric(
                            m["metric"].upper(),
                            f"{m['actual']}",
                            f"{variance}"
                        )

                # WHY
                st.markdown("### 🧠 Why")
                for m in metrics:
                    if m["status"] == "off_track":
                        st.error(
                            f"{m['metric']} off track "
                            f"({m['actual']} vs {m['target']})"
                        )

                # ACTIONS
                st.markdown("### ✅ Actions")
                store_actions = [a for a in actions if store in a]

                for a in store_actions:
                    st.success(a)

                st.markdown("---")


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
