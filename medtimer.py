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

# ------------------ DATA ------------------
QUOTES = [
    "💙 Taking medicine is self-care.",
    "🐢 Slow and steady wins health.",
    "🌱 Consistency builds strength.",
    "✨ Your health matters every day.",
    "💪 Small steps, big results."
]

HEALTH_TIPS = [
    "Drink 8 glasses of water daily! 💧",
    "A 5-minute walk after meals improves digestion 🚶‍♂️",
    "Good sleep = Strong immunity 😴",
    "Eat fruits and veggies daily! 🥦🍎",
    "Smile 😊 It's good for your heart!",
    "Take deep breaths for stress relief 🌬️",
    "Stretching keeps you flexible 🤸‍♂️"
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

MASCOTS = [
    "🐢 Health Buddy", "🦊 Foxy Care", "🐼 Panda Pal", "🦄 Unicorn Helper",
    "🐶 Doggy Doctor", "🐱 Kitty Care", "🐸 Froggy Friend", "🐵 Monkey Medic",
    "🦋 Butterfly Wellness", "🦖 Dino Doctor", "🐰 Bunny Buddy", "🦉 Wise Owl",
    "🦁 Lion Heart", "🐮 Moo Medic", "🐷 Piggy Care", "🐧 Penguin Pal",
    "🦦 Otter Health", "🦈 Sharky Aid", "🐍 Snake Sage", "🐝 Bee Helper",
    "🦗 Cricket Care", "🦔 Hedgehog Health", "🐲 Dragon Doc", "🦢 Swan Support",
    "🐦 Birdy Buddy", "🦚 Peacock Pal", "🐴 Horse Helper", "🦓 Zebra Zen",
    "🦄 Magical Unicorn", "🦊 Cunning Fox", "🐻 Bear Buddy", "🐨 Koala Care",
    "🐺 Wolf Wellness", "🦁 Brave Lion", "🐵 Monkey Medic", "🐸 Frog Friend",
    "🐧 Penguin Protector", "🦦 Otter Aid", "🐝 Busy Bee", "🦉 Owl Advisor",
    "🦋 Butterfly Bliss", "🦄 Sparkle Unicorn", "🐶 Doggo Medic", "🐱 Kitty Comfort",
    "🐯 Tiger Trainer", "🐴 Horse Health", "🦄 Fantasy Unicorn", "🐹 Hamster Helper",
    "🐸 Jumping Frog"
]

THEMES = {
    "Light": {"bg": "#ffffff", "color": "#000000"},
    "Dark": {"bg": "#0e1117", "color": "#ffffff"},
    "Ocean": {"bg": "#a2d5f2", "color": "#034f84"},
    "Sunset": {"bg": "#ffadad", "color": "#4a1c40"}
}

# ------------------ LOGIN PAGE ------------------
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
                st.experimental_rerun()
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
                st.warning("Enter username & password")

# ------------------ MAIN APP ------------------
def app():
    st.title("💊 MedTimer Dashboard")

    # Apply theme
    theme = THEMES.get(st.session_state.theme, THEMES["Light"])
    st.markdown(f"""
    <style>
    body {{
        background-color:{theme['bg']};
        color:{theme['color']};
    }}
    </style>
    """, unsafe_allow_html=True)

    colA, colB = st.columns([2, 1])

    # -------- ADD MEDICINE --------
    with colA:
        st.subheader("➕ Add Medicine")
        name = st.text_input("Medicine Name")
        t = st.time_input("Time", value=time(8, 0))
        if st.button("Add Medicine"):
            if name:
                st.session_state.meds.append({
                    "name": name,
                    "time": t,
                    "taken": False,
                    "date": datetime.now().date()
                })
                st.success(f"{name} added!")
            else:
                st.warning("Enter medicine name")

        # Mascot display
        if st.session_state.show_mascot:
            st.markdown(f"### {st.session_state.get('mascot', random.choice(MASCOTS))}")
            st.info("I'm here to remind you to take care of yourself!")

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
                    st.experimental_rerun()
            st.caption(status)

        # Reminder for missed meds
        for m in st.session_state.meds:
            if not m["taken"] and datetime.now().time() > m["time"]:
                st.warning(f"🔔 Time to take {m['name']}!")

    # -------- STATS --------
    total = len(st.session_state.meds)
    score = int((taken / total) * 100) if total else 0

    if score == 100 and total > 0:
        st.session_state.streak += 1
        st.balloons()
        st.success(f"🔥 Perfect day! Streak: {st.session_state.streak}")
    elif score < 100:
        st.session_state.streak = 0

    st.sidebar.metric("Adherence", f"{score}%")
    st.sidebar.metric("Streak", f"{st.session_state.streak} 🔥")
    st.sidebar.info(random.choice(QUOTES + HEALTH_TIPS))

    # -------- MEDICINE REFERENCE --------
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

    # Theme selector
    selected_theme = st.sidebar.radio(
        "Theme", list(THEMES.keys()),
        index=list(THEMES.keys()).index(st.session_state.theme)
    )
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.experimental_rerun()

    # Mascot selector
    mascot_option = st.sidebar.selectbox(
        "Choose Mascot", ["Random"] + MASCOTS
    )
    if mascot_option == "Random":
        st.session_state.show_mascot = True
        st.session_state.mascot = random.choice(MASCOTS)
    else:
        st.session_state.show_mascot = True
        st.session_state.mascot = mascot_option

    if st.sidebar.button("Clear All Medicines"):
        st.session_state.meds = []
        st.success("Cleared all medicines")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# ------------------ RUN ------------------
if not st.session_state.logged_in:
    login_page()
else:
    app()
