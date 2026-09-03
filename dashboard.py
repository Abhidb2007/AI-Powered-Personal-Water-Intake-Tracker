from datetime import date

import pandas as pd
import streamlit as st

from src.agent import WaterIntakeAgent
from src.database import get_intake_history, log_intake


st.set_page_config(page_title="AI Water Tracker", page_icon="💧", layout="wide")
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --ink:#172b3a; --muted:#617381; --blue:#087ea4; --line:#dce8ed; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
h1,h2,h3 { font-family:'Space Grotesk',sans-serif; letter-spacing:0; color:var(--ink); }
.block-container { max-width:1180px; padding:2.5rem 3rem 4rem; }
[data-testid="stSidebar"] { background:#f2f6f8; border-right:1px solid var(--line); }
[data-testid="stSidebar"] .block-container { padding:2rem 1.5rem; }
.brand { color:var(--blue); font-size:.78rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; margin-bottom:.5rem; }
.hero { padding:1rem 0 2rem; border-bottom:1px solid var(--line); margin-bottom:2rem; }
.hero h1 { font-size:clamp(2rem,4vw,3.25rem); margin:0 0 .5rem; }
.hero p { color:var(--muted); font-size:1.05rem; margin:0; }
.welcome { background:linear-gradient(135deg,#eaf7fa,#f8fbfc); border:1px solid #ccebf1; border-radius:16px; padding:3rem; max-width:760px; }
.welcome h1 { margin-top:0; }
[data-testid="stMetric"] { background:#fff; border:1px solid var(--line); border-radius:12px; padding:1rem 1.1rem; box-shadow:0 4px 16px rgba(23,43,58,.04); }
[data-testid="stMetricLabel"] { color:var(--muted); }
.section-title { margin:2rem 0 .8rem; }
.feedback { background:#eef8f1; border:1px solid #cce8d3; border-radius:12px; padding:1rem 1.2rem; margin:1.2rem 0; }
.sidebar-note { color:var(--muted); font-size:.88rem; line-height:1.45; }
div.stButton > button, div[data-testid="stFormSubmitButton"] button { border-radius:8px; font-weight:600; min-height:2.7rem; }
@media (max-width:700px) { .block-container { padding:1.5rem 1rem 3rem; } .welcome { padding:1.5rem; } }
</style>
""",
    unsafe_allow_html=True,
)


if "tracker_started" not in st.session_state:
    st.session_state.tracker_started = False


def render_welcome():
    st.markdown('<div class="brand">Daily hydration companion</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome"><h1>Stay hydrated, with less effort.</h1><p>Log your water intake, understand your progress, and get practical feedback throughout the day.</p></div>', unsafe_allow_html=True)
    if st.button("Start tracking", type="primary"):
        st.session_state.tracker_started = True
        st.rerun()


def render_dashboard():
    with st.sidebar:
        st.markdown('<div class="brand">AI Water Tracker</div>', unsafe_allow_html=True)
        st.header("Log intake")
        st.markdown('<p class="sidebar-note">Add each glass or bottle as you drink it. Your history stays on this device.</p>', unsafe_allow_html=True)
        with st.form("intake_form"):
            user_id = st.text_input("User ID", value="user_123", max_chars=100).strip()
            intake_ml = st.number_input("Water intake (ml)", min_value=1, max_value=10000, value=250, step=50)
            submitted = st.form_submit_button("Log water", type="primary")

    if submitted:
        if not user_id:
            st.sidebar.error("Enter a User ID before logging intake.")
        else:
            log_intake(user_id, int(intake_ml))
            st.session_state.last_analysis = WaterIntakeAgent().analyze_intake(intake_ml)
            st.session_state.active_user = user_id
            st.sidebar.success(f"Logged {int(intake_ml):,} ml")

    active_user = st.session_state.get("active_user", user_id)
    history = get_intake_history(active_user) if active_user else []
    history_df = pd.DataFrame(history, columns=["Water intake (ml)", "Date"])
    today_total = int(sum(row[0] for row in history if row[1] == date.today().isoformat()))
    all_time_total = int(history_df["Water intake (ml)"].sum()) if not history_df.empty else 0

    st.markdown('<div class="hero"><div class="brand">Your hydration overview</div><h1>AI Water Tracker</h1><p>Small, consistent sips add up.</p></div>', unsafe_allow_html=True)
    metrics = st.columns(3)
    metrics[0].metric("Today", f"{today_total:,} ml")
    metrics[1].metric("All-time logged", f"{all_time_total:,} ml")
    metrics[2].metric("Entries", f"{len(history):,}")
    if "last_analysis" in st.session_state:
        st.markdown(f'<div class="feedback"><strong>AI feedback</strong><br>{st.session_state.last_analysis}</div>', unsafe_allow_html=True)

    st.markdown('<h2 class="section-title">Water intake history</h2>', unsafe_allow_html=True)
    if history:
        st.dataframe(history_df[["Date", "Water intake (ml)"]], hide_index=True)
        st.line_chart(history_df.set_index("Date")[["Water intake (ml)"]], height=280)
    else:
        st.info("No intake logged yet. Use the form in the sidebar to record your first drink.")


if st.session_state.tracker_started:
    render_dashboard()
else:
    render_welcome()
