import streamlit as st
import requests
import pandas as pd

API = "https://districtos.onrender.com/api"

st.set_page_config(layout="wide")

# -------------------------
# STATE
# -------------------------
if "results" not in st.session_state:
    st.session_state.results = None

if "focus_store" not in st.session_state:
    st.session_state.focus_store = None

# -------------------------
# ELITE STYLE 🔥
# -------------------------
st.markdown("""
<style>

/* GLOBAL */
body {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: #E2E8F0;
}

/* GLASS CARDS */
.card {
    backdrop-filter: blur(16px);
    background: rgba(15, 23, 42, 0.6);
    border-radius: 18px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.05);
    box-shadow: 0 10px 40px rgba(0,0,0,0.6);
    transition: all 0.2s ease;
}

/* HOVER EFFECT */
.card:hover {
    transform: scale(1.02);
    border: 1px solid rgba(255,255,255,0.15);
}

/* KPI */
.kpi {
    font-size: 42px;
    font-weight: 700;
}

/* LABEL */
.label {
    font-size: 11px;
    color: #94A3B8;
}

/* GRADIENT BAR */
.bar {
    height: 8px;
    border-radius: 8px;
    background: linear-gradient(90deg, #22c55e, #facc15, #ef4444);
    margin-top: 8px;
}

/* SECTION */
.section {
    margin-top: 25px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# SIDEBAR
# -------------------------
menu = st.sidebar.radio("", [
    "Command Center",
    "Operations",
    "Intelligence",
    "AI Command",
    "Intake"
])

st.sidebar.markdown("## DistrictOS")
st.sidebar.caption("Flagship Intelligence System")

r = st.session_state.results

# -------------------------
# COMMAND CENTER 🔥 (NOW FEELS PREMIUM)
# -------------------------
if menu == "Command Center":

    st.title("Command Center")

    if not r:
        st.warning("No data loaded")
    else:
        score = r["district_score"]

        # HERO KPI (BIG DIFFERENCE)
        st.markdown(f"""
        <div class="card">
            <div class="label">DISTRICT HEALTH</div>
            <div class="kpi">{score}</div>
            <div class="bar"></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Priority Stores")

        cols = st.columns(3)

        for i, s in enumerate(r["priority_stores"][:3]):
            sev = r["store_severity"][s]

            with cols[i]:
                if st.button(f"Store {s}"):
                    st.session_state.focus_store = s

                st.markdown(f"""
                <div class="card">
                    <div class="label">STORE {s}</div>
                    <div class="kpi">{sev}</div>
                </div>
                """, unsafe_allow_html=True)


# -------------------------
# OPERATIONS (FOCUS MODE 🔥)
# -------------------------
elif menu == "Operations":

    st.title("Operations")

    if r:

        # SELECT STORE
        selected = st.selectbox("Select Store", r["priority_stores"])
        st.session_state.focus_store = selected

        store = st.session_state.focus_store

        sev = r["store_severity"][store]
        metrics = r["store_metrics"][store]
        impacts = r["impacts"].get(store, [])

        # 🔥 FOCUS PANEL (THIS IS THE BIG DIFFERENCE)
        st.markdown(f"""
        <div class="card">
            <div class="label">FOCUS STORE</div>
            <div class="kpi">Store {store}</div>
            <div class="kpi">{sev}</div>
            <div class="bar"></div>
        </div>
        """, unsafe_allow_html=True)

        # KPI GRID
        st.markdown("### Performance")

        cols = st.columns(len(metrics))

        for i, m in enumerate(metrics):
            with cols[i]:
                st.markdown(f"""
                <div class="card">
                    <div class="label">{m['metric']}</div>
                    <div class="kpi">{m['actual']}</div>
                    <div class="label">Target {m['target']}</div>
                </div>
                """, unsafe_allow_html=True)

        # TREND
        trend = r.get("trend_memory", {}).get(store, [])
        if trend:
            df = pd.DataFrame(trend)
            st.line_chart(df["severity"])

        # IMPACT
        st.markdown("### Impact")
        for i in impacts:
            st.error(i)

        # ACTIONS
        st.markdown("### Actions")
        for a in r["actions"]:
            if store in a:
                st.success(a)


# -------------------------
# INTELLIGENCE
# -------------------------
elif menu == "Intelligence":

    st.title("Intelligence")

    if r:
        for p in r["patterns"]:
            st.markdown(f"""
            <div class="card">
                <div class="label">{p['metric']}</div>
                <div class="kpi">{p['count']} stores</div>
            </div>
            """, unsafe_allow_html=True)


# -------------------------
# AI COMMAND (FEELS LIKE PRODUCT)
# -------------------------
elif menu == "AI Command":

    st.title("AI Command")

    if r:
        q = st.text_input("What do you want to know?")

        if q:
            with st.spinner("Thinking..."):
                res = requests.post(f"{API}/ask", json={"question": q})
                if res.status_code == 200:
                    st.markdown(f"""
                    <div class="card">
                        <div class="label">AI RESPONSE</div>
                        <p>{res.json()["response"]}</p>
                    </div>
                    """, unsafe_allow_html=True)


# -------------------------
# INTAKE
# -------------------------
elif menu == "Intake":

    st.title("Data Intake")

    f = st.file_uploader("Upload File")
    t = st.text_area("Paste Data")

    if st.button("Run Analysis"):
        if f:
            res = requests.post(
                f"{API}/analyze/upload",
                files={"file": (f.name, f.getvalue())}
            )
        else:
            res = requests.post(
                f"{API}/analyze/text",
                json={"text": t}
            )

        if res.status_code == 200:
            st.session_state.results = res.json()
            st.success("Analysis complete")
