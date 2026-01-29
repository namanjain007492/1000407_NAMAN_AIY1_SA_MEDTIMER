import streamlit as st
import pandas as pd
from datetime import date, datetime, time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="MedTimer", layout="wide")

# ---------------- SESSION STATE ----------------
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.users = {}
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.theme = "Light"
    st.session_state.mascot = "🐢 Turtle"
    st.session_state.meds = []
    st.session_state.edit_index = None

# ---------------- THEME ----------------
def apply_theme():
    if st.session_state.theme == "Dark":
        st.markdown("""
        <style>
        body { background-color:#0e1117; color:white; }
        .stButton>button { width:100%; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        body { background-color:white; color:black; }
        .stButton>button { width:100%; }
        </style>
        """, unsafe_allow_html=True)

apply_theme()

# ---------------- LOGIN ----------------
def login_page():
    st.title("💊 MedTimer")
    st.caption("Professional Medicine Adherence Tracker")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in st.session_state.users and st.session_state.users[u] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.success("Logged in successfully")
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
            "Theme", ["Light", "Dark"],
            index=0 if st.session_state.theme == "Light" else 1
        )

        st.session_state.mascot = st.selectbox(
            "Mascot", ["🐢 Turtle", "🐶 Dog", "🐱 Cat", "🦁 Lion"]
        )

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.meds.clear()

    apply_theme()

    # ---------- ADD MEDICINE ----------
    st.subheader("➕ Add Medicine")
    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Medicine name")
    with c2:
        med_time = st.time_input("Time", value=time(8, 0))
    with c3:
        if st.button("Add"):
            if name:
                st.session_state.meds.append({
                    "name": name,
                    "time": med_time.strftime("%H:%M"),
                    "taken": False,
                    "date": date.today()
                })

    # ---------- EDIT MODE ----------
    if st.session_state.edit_index is not None:
        idx = st.session_state.edit_index
        med = st.session_state.meds[idx]

        st.subheader("✏ Edit Medicine")
        new_name = st.text_input("Edit name", med["name"])
        new_time = st.text_input("Edit time (HH:MM)", med["time"])

        colA, colB = st.columns(2)
        with colA:
            if st.button("Save"):
                st.session_state.meds[idx]["name"] = new_name
                st.session_state.meds[idx]["time"] = new_time
                st.session_state.edit_index = None
        with colB:
            if st.button("Cancel"):
                st.session_state.edit_index = None

        st.divider()

    # ---------- MEDICINE LIST ----------
    st.subheader("📋 Today’s Medicines")

    if not st.session_state.meds:
        st.info("No medicines added yet.")
        return

    for i, med in enumerate(st.session_state.meds):
        col1, col2, col3, col4, col5 = st.columns([3,2,2,1,1])

        col1.write(med["name"])
        col2.write(med["time"])

        taken = col3.checkbox(
            "Taken",
            value=med["taken"],
            key=f"taken_{i}"
        )
        st.session_state.meds[i]["taken"] = taken

        if col4.button("✏", key=f"edit_{i}"):
            st.session_state.edit_index = i

        if col5.button("🗑", key=f"del_{i}"):
            st.session_state.meds.pop(i)
            st.session_state.edit_index = None
            st.stop()

    # ---------- MARK ALL ----------
    if st.button("✅ Mark All Taken"):
        for med in st.session_state.meds:
            med["taken"] = True

    # ---------- ADHERENCE ----------
    total = len(st.session_state.meds)
    taken_count = sum(m["taken"] for m in st.session_state.meds)
    daily_adherence = int((taken_count / total) * 100) if total else 0

    st.subheader("📊 Daily Adherence")
    st.progress(daily_adherence)
    st.write(f"**{daily_adherence}% completed**")

    # ---------- WEEKLY ADHERENCE ----------
    st.subheader("📅 Weekly Adherence")
    df = pd.DataFrame(st.session_state.meds)
    if not df.empty:
        weekly = df.groupby("date")["taken"].mean() * 100
        st.line_chart(weekly)

    # ---------- MASCOT ----------
    st.subheader("🐾 Mascot Reaction")
    if daily_adherence == 100:
        st.success(f"{st.session_state.mascot} is proud of you! 🎉")
    elif daily_adherence >= 50:
        st.warning(f"{st.session_state.mascot} says: Keep going!")
    else:
        st.error(f"{st.session_state.mascot} says: Don’t forget your meds!")

# ---------------- MAIN ----------------
if not st.session_state.logged_in:
    login_page()
else:
    dashboard()
