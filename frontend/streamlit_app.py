import streamlit as st
import requests

API = "https://districtos.onrender.com/api"

st.set_page_config(layout="wide")

menu = st.sidebar.radio("DistrictOS", [
    "Command Center",
    "Intake",
    "Priorities",
    "Patterns",
    "Alerts",
    "Ask AI"
])

if "results" not in st.session_state:
    st.session_state.results = None


# -------------------------
# COMMAND CENTER
# -------------------------
if menu == "Command Center":
    st.title("🧠 Command Center")

    r = st.session_state.results

    if r:
        score = r["district_score"]

        color = "🟢" if score > 80 else "🟡" if score > 60 else "🔴"
        st.markdown(f"# {color} {score}")

        col1, col2 = st.columns(2)
        col1.metric("Stores", len(r["store_severity"]))
        col2.metric("Patterns", len(r["patterns"]))

        st.info(r["summary"])
    else:
        st.warning("No data yet")


# -------------------------
# INTAKE
# -------------------------
elif menu == "Intake":
    f = st.file_uploader("Upload")
    t = st.text_area("Paste")

    if st.button("Analyze"):
        if f:
            res = requests.post(f"{API}/analyze/upload",
                                files={"file": (f.name, f.getvalue())})
        else:
            res = requests.post(f"{API}/analyze/text",
                                json={"text": t})

        if res.status_code == 200:
            st.session_state.results = res.json()


# -------------------------
# PRIORITIES
# -------------------------
elif menu == "Priorities":
    r = st.session_state.results

    if r:
        for s in r["priority_stores"]:
            sev = r["store_severity"][s]

            st.markdown(f"## Store {s} ({sev})")

            for impact in r["impacts"].get(s, []):
                st.warning(impact)

            for a in r["actions"]:
                if s in a:
                    st.success(a)

            st.markdown("---")


# -------------------------
# PATTERNS
# -------------------------
elif menu == "Patterns":
    r = st.session_state.results

    if r:
        for p in r["patterns"]:
            st.error(f"{p['metric']} across {p['count']} stores")


# -------------------------
# ALERTS 🔥
# -------------------------
elif menu == "Alerts":
    r = st.session_state.results

    if r:
        if r["alerts"]:
            for a in r["alerts"]:
                st.error(a)
        else:
            st.success("No alerts")


# -------------------------
# ASK AI 🔥
# -------------------------
elif menu == "Ask AI":
    r = st.session_state.results

    if r:
        q = st.text_input("Ask DistrictOS")

        if q:
            # simple local logic (expand later)
            if "worst" in q.lower():
                st.write(f"Focus on store {r['priority_stores'][0]}")
            elif "fix" in q.lower():
                st.write(r["actions"][:3])
            else:
                st.write("Ask about priorities or risks")
