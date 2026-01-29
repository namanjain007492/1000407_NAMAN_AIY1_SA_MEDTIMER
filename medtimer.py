import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import uuid

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MedTimer PRO", layout="wide")

# ---------------- SESSION INIT ----------------
def init_state():
    defaults = {
        "logged_in": False,
        "users": {},
        "current_user": None,
        "theme": "Light",
        "mascot": "🐢 Turtle",
        "meds": [],
        "edit_med_id": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ---------------- THEME ----------------
def apply_theme():
    if st.session_state.theme == "Dark":
        st.markdown("""
        <style>
        body { background:#0e1117; color:white; }
        .stButton>button { width:100%; }
        </style>
        """, unsafe_allow_html=True)

apply_theme()

# ---------------- LOGIN ----------------
def login_page():
    st.title("💊 MedTimer PRO")
    st.caption("Professional Medicine Adherence Tracker")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in st.session_state.users and st.session_state.users[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
            else:
                st.error("Invalid credentials")

    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            if nu and np:
                st.session_state.users[nu] = np
                st.success("Account created. Login now.")
            else:
                st.warning("Fill all fields")

# ---------------- DASHBOARD ----------------
def dashboard():
    st.title("💊 MedTimer Dashboard")

    # -------- SIDEBAR --------
    with st.sidebar:
        st.header("⚙ Settings")

        st.session_state.theme = st.selectbox(
            "Theme", ["Light", "Dark"],
            index=0 if st.session_state.theme == "Light" else 1
        )

        st.session_state.mascot = st.selectbox(
            "Mascot", ["🐢 Turtle", "🐶 Dog", "🐱 Cat", "🦁 Lion", "🐼 Panda"]
        )

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None

    apply_theme()

    # -------- ADD / EDIT MED --------
    if st.session_state.edit_med_id is None:
        st.subheader("➕ Add Medicine")

        with st.form("add_med_form", clear_on_submit=True):
            name = st.text_input("Medicine Name")
            t = st.time_input("Time", value=time(8, 0))
            submit = st.form_submit_button("Add Medicine")

            if submit and name:
                st.session_state.meds.append({
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "time": t.strftime("%H:%M"),
                    "taken": False,
                    "date": str(date.today())
                })
    else:
        med = next(m for m in st.session_state.meds if m["id"] == st.session_state.edit_med_id)

        st.subheader("✏ Edit Medicine")
        with st.form("edit_med_form"):
            new_name = st.text_input("Medicine Name", med["name"])
            new_time = st.text_input("Time (HH:MM)", med["time"])
            save = st.form_submit_button("Save")
            cancel = st.form_submit_button("Cancel")

            if save:
                med["name"] = new_name
                med["time"] = new_time
                st.session_state.edit_med_id = None

            if cancel:
                st.session_state.edit_med_id = None

    st.divider()

    # -------- MED LIST --------
    st.subheader("📋 Today’s Medicines")

    if not st.session_state.meds:
        st.info("No medicines added yet.")
    else:
        for med in st.session_state.meds:
            c1, c2, c3, c4, c5 = st.columns([3,2,2,1,1])

            c1.write(med["name"])
            c2.write(med["time"])

            med["taken"] = c3.checkbox(
                "Taken",
                med["taken"],
                key=f"taken_{med['id']}"
            )

            if c4.button("✏", key=f"edit_{med['id']}"):
                st.session_state.edit_med_id = med["id"]

            if c5.button("🗑", key=f"del_{med['id']}"):
                st.session_state.meds = [m for m in st.session_state.meds if m["id"] != med["id"]]
                st.session_state.edit_med_id = None
                st.stop()

    # -------- MARK ALL --------
    if st.session_state.meds:
        if st.button("✅ Mark All Taken"):
            for m in st.session_state.meds:
                m["taken"] = True

    # -------- ADHERENCE --------
    if st.session_state.meds:
        df = pd.DataFrame(st.session_state.meds)
        total = len(df)
        taken = df["taken"].sum()
        daily = int((taken / total) * 100)

        st.subheader("📊 Daily Adherence")
        st.progress(daily)
        st.write(f"**{daily}% completed today**")

        st.subheader("📅 Weekly Adherence")
        weekly = df.groupby("date")["taken"].mean() * 100
        st.line_chart(weekly)

    # -------- MASCOT --------
    st.subheader("🐾 Mascot Feedback")

    if not st.session_state.meds:
        st.info(f"{st.session_state.mascot} says: Add medicines to start!")
    elif daily == 100:
        st.success(f"{st.session_state.mascot} is SUPER proud of you 🎉")
    elif daily >= 50:
        st.warning(f"{st.session_state.mascot} says: Keep going!")
    else:
        st.error(f"{st.session_state.mascot} says: Don’t miss your meds!")

# ---------------- RUN ----------------
if not st.session_state.logged_in:
    login_page()
else:
    dashboard()
