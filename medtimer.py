import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MedTimer", layout="wide")

# ---------------- SESSION STATE ----------------
defaults = {
    "users": {},
    "logged_in": False,
    "current_user": None,
    "login_time": None,
    "meds": [],
    "theme": "Light",
    "mascot": "🐢 Turtle",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- THEME ----------------
def apply_theme():
    if st.session_state.theme == "Dark":
        st.markdown("""
        <style>
        body { background-color: #0e1117; color: white; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        body { background-color: #ffffff; color: black; }
        </style>
        """, unsafe_allow_html=True)

apply_theme()

# ---------------- LOGIN PAGE ----------------
def login_page():
    st.title("💊 MedTimer")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in st.session_state.users and st.session_state.users[u] == p:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.session_state.login_time = datetime.now()
                st.success("Logged in!")
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

    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.header("⚙ Settings")

        st.session_state.theme = st.selectbox(
            "Theme", ["Light", "Dark"], index=0 if st.session_state.theme == "Light" else 1
        )

        st.session_state.mascot = st.selectbox(
            "Mascot",
            ["🐢 Turtle", "🐶 Dog", "🐱 Cat", "🦁 Lion"]
        )

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.session_state.meds = []

    apply_theme()

    # ---------- ADD MED ----------
    st.subheader("➕ Add Medicine")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Medicine Name")
    with col2:
        time = st.time_input("Time")
    with col3:
        if st.button("Add"):
            if name:
                st.session_state.meds.append({
                    "name": name,
                    "time": time.strftime("%H:%M"),
                    "taken": False,
                    "date": date.today()
                })

    # ---------- MED LIST ----------
    st.subheader("📋 Today’s Medicines")

    if not st.session_state.meds:
        st.info("No medicines added yet.")
        return

    taken_count = 0

    for i, med in enumerate(st.session_state.meds):
        col1, col2, col3, col4, col5 = st.columns([3,2,2,2,1])

        with col1:
            st.write(f"💊 **{med['name']}**")
        with col2:
            st.write(f"⏰ {med['time']}")
        with col3:
            if st.checkbox(
                "Taken",
                value=med["taken"],
                key=f"taken_{i}"
            ):
                st.session_state.meds[i]["taken"] = True
                taken_count += 1
            else:
                st.session_state.meds[i]["taken"] = False
        with col4:
            new_name = st.text_input(
                "Edit",
                med["name"],
                key=f"edit_{i}"
            )
            st.session_state.meds[i]["name"] = new_name
        with col5:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.meds.pop(i)
                st.experimental_set_query_params()

    # ---------- TAKEN ALL ----------
    if st.button("✅ Mark All Taken"):
        for med in st.session_state.meds:
            med["taken"] = True

    # ---------- ADHERENCE ----------
    total = len(st.session_state.meds)
    taken = sum(1 for m in st.session_state.meds if m["taken"])
    adherence = int((taken / total) * 100) if total else 0

    st.subheader("📊 Adherence")
    st.progress(adherence)
    st.write(f"**{adherence}% taken today**")

    # ---------- WEEKLY ADHERENCE ----------
    st.subheader("📅 Weekly Adherence")
    df = pd.DataFrame(st.session_state.meds)
    if not df.empty:
        weekly = df.groupby("date")["taken"].mean() * 100
        st.line_chart(weekly)

    # ---------- MASCOT REACTION ----------
    st.subheader("🐾 Mascot Status")

    if adherence == 100:
        st.success(f"{st.session_state.mascot} is PROUD of you!")
    elif adherence >= 50:
        st.warning(f"{st.session_state.mascot} says: Keep going!")
    else:
        st.error(f"{st.session_state.mascot} says: Don’t forget your meds!")

# ---------------- MAIN ----------------
if not st.session_state.logged_in:
    login_page()
else:
    dashboard()
