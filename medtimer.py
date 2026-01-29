import streamlit as st
from datetime import datetime, timedelta, time
import random

# ------------------ APP CONFIG ------------------
st.set_page_config("MedTimer", "💊", layout="wide")

# ------------------ SESSION STATE ------------------
defaults = {
    "users": {},
    "logged_in": False,
    "user": None,
    "login_time": None,
    "meds": [],
    "theme": "Light",
    "streak": 0,
    "show_mascot": True,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------------------ AUTO LOGOUT (48 HRS) ------------------
if st.session_state.logged_in and st.session_state.login_time:
    if datetime.now() - st.session_state.login_time > timedelta(hours=48):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.warning("Session expired. Please login again.")
        st.stop()

# ------------------ THEME ------------------
if st.session_state.theme == "Dark":
    st.markdown("""
    <style>
    body { background-color:#0e1117; color:white; }
    </style>
    """, unsafe_allow_html=True)

# ------------------ DATA ------------------
QUOTES = [
    "💙 Taking medicine is self-care.",
    "🐢 Slow and steady wins health.",
    "🌱 Consistency builds strength.",
    "✨ Your health matters every day.",
    "💪 Small steps, big results."
]

MED_DB = {
    "Fever": [
        ("Paracetamol", "500mg", "Analgesic", "Safe", "Liver damage if overused"),
        ("Ibuprofen", "400mg", "NSAID", "Pain + fever", "Stomach irritation"),
    ],
    "Diabetes": [
        ("Metformin", "500mg", "Antidiabetic", "Controls sugar", "GI upset"),
        ("Insulin", "As prescribed", "Hormone", "Fast control", "Injection"),
    ],
    "BP": [
        ("Amlodipine", "5mg", "Calcium blocker", "Controls BP", "Ankle swelling"),
        ("Losartan", "50mg", "ARB", "Kidney safe", "Dizziness"),
    ],
    "Cold & Allergy": [
        ("Cetirizine", "10mg", "Antihistamine", "Allergy relief", "Drowsy"),
    ]
}

# ------------------ LOGIN ------------------
def login_page():
    st.title("💊 MedTimer")
    st.subheader("Your Daily Medicine Companion")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in st.session_state.users and st.session_state.users[u] == p:
                st.session_state.logged_in = True
                st.session_state.user = u
                st.session_state.login_time = datetime.now()
                st.success("Logged in successfully")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            st.session_state.users[nu] = np
            st.success("Account created. Login now.")

# ------------------ MAIN APP ------------------
def app():
    st.title("💊 MedTimer Dashboard")

    colA, colB = st.columns([2, 1])

    # -------- ADD MEDICINE --------
    with colA:
        st.subheader("➕ Add Medicine")

        name = st.text_input("Medicine Name")
        t = st.time_input("Time", value=time(8, 0))

        if st.button("Add Medicine"):
            st.session_state.meds.append({
                "name": name,
                "time": t,
                "taken": False,
                "date": datetime.now().date()
            })
            st.success("Medicine added")

        # Mascot
        if st.session_state.show_mascot:
            st.markdown("### 🐢 Health Buddy")
            st.info("I'm here to remind you!")

    # -------- MEDICINE LIST --------
    with colB:
        st.subheader("📋 Today’s Medicines")

        taken = 0
        now = datetime.now().time()

        for i, m in enumerate(st.session_state.meds):
            status = "🟡 Upcoming"
            if m["taken"]:
                status = "🟢 Taken"
                taken += 1
            elif now > m["time"]:
                status = "🔴 Missed"

            c1, c2, c3 = st.columns([3, 2, 1])
            c1.write(m["name"])
            c2.write(m["time"].strftime("%I:%M %p"))
            if not m["taken"]:
                if c3.button("✔", key=i):
                    m["taken"] = True
                    st.rerun()
            st.caption(status)

    # -------- STATS --------
    total = len(st.session_state.meds)
    score = int((taken / total) * 100) if total else 0

    if score == 100 and total > 0:
        st.session_state.streak += 1
    else:
        st.session_state.streak = 0

    st.sidebar.metric("Adherence", f"{score}%")
    st.sidebar.metric("Streak", f"{st.session_state.streak} 🔥")
    st.sidebar.info(random.choice(QUOTES))

    # -------- MEDICINE SUGGESTION --------
    st.sidebar.subheader("💊 Medicine Reference")
    disease = st.sidebar.selectbox("Choose Disease", MED_DB.keys())

    for med in MED_DB[disease]:
        with st.sidebar.expander(med[0]):
            st.write(f"**Dosage:** {med[1]}")
            st.write(f"**Type:** {med[2]}")
            st.write(f"✅ Pros: {med[3]}")
            st.write(f"⚠️ Cons: {med[4]}")
            st.caption("Consult doctor before use.")

    # -------- SETTINGS --------
    st.sidebar.subheader("⚙️ Settings")

    st.session_state.theme = st.sidebar.radio(
        "Theme", ["Light", "Dark"],
        index=0 if st.session_state.theme == "Light" else 1
    )

    st.session_state.show_mascot = st.sidebar.checkbox(
        "Show Mascot", value=st.session_state.show_mascot
    )

    if st.sidebar.button("Clear All Medicines"):
        st.session_state.meds = []
        st.success("Cleared")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ------------------ RUN ------------------
if not st.session_state.logged_in:
    login_page()
else:
    app()
