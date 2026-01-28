import streamlit as st
from datetime import datetime, timedelta, date, time
import random

# ================= PAGE CONFIG =================
st.set_page_config(page_title="MedTimer", layout="wide")

# ================= SESSION INIT =================
def init():
    defaults = {
        "users": {},
        "logged": False,
        "user": None,
        "login_time": None,
        "meds": [],
        "streak": 0,
        "theme": "Light",
        "font": "Medium",
        "mascot": "🐢",
        "motivation": True,
        "last_refresh": datetime.now(),
        "last_day": date.today()
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

# ================= DAILY RESET =================
if st.session_state.last_day != date.today():
    st.session_state.meds = []
    st.session_state.last_day = date.today()

# ================= AUTO LOGOUT (48 HRS) =================
if st.session_state.logged:
    if datetime.now() - st.session_state.login_time > timedelta(hours=48):
        st.session_state.logged = False
        st.warning("Session expired. Please login again.")
        st.stop()

# ================= THEME =================
dark = st.session_state.theme == "Dark"
bg = "#0e1117" if dark else "#f4fff6"
fg = "white" if dark else "black"
font = {"Small":"14px","Medium":"18px","Large":"22px"}[st.session_state.font]

st.markdown(f"""
<style>
body {{
    background-color:{bg};
    color:{fg};
    font-size:{font};
}}
.big {{ font-size:80px; text-align:center; font-weight:900; }}
.mascot {{ font-size:60px; }}
</style>
""", unsafe_allow_html=True)

# ================= DATA =================
COMMON_MEDS = [
    ("Paracetamol","Tablet","500mg","Fever relief","Liver risk if overused"),
    ("Ibuprofen","Tablet","400mg","Pain relief","Stomach irritation"),
    ("Metformin","Tablet","500mg","Controls sugar","GI upset"),
    ("Insulin","Injection","As prescribed","Sugar control","Injection"),
    ("Vitamin D","Capsule","60000 IU","Bone strength","Overdose risk"),
    ("Vitamin B12","Tablet","500mcg","Nerve health","Rare allergy"),
    ("Amlodipine","Tablet","5mg","BP control","Ankle swelling"),
    ("Losartan","Tablet","50mg","BP + kidney","Dizziness"),
]

QUOTES = [
    "💙 Taking medicine is self-care",
    "🐢 Slow consistency builds health",
    "🌱 Small steps heal big problems",
    "✨ You’re doing great today",
    "🧠 Your future self thanks you"
]

# ================= AUTO MOTIVATION (10s) =================
if datetime.now() - st.session_state.last_refresh > timedelta(seconds=10):
    st.session_state.last_refresh = datetime.now()
    st.session_state.current_quote = random.choice(QUOTES)

# ================= LOGIN / SIGNUP =================
def login():
    st.markdown("<div class='big'>MedTimer</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;font-size:130px;'>🐢</div>", unsafe_allow_html=True)

    t1, t2 = st.tabs(["Login", "Sign Up"])

    with t1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in st.session_state.users and st.session_state.users[u] == p:
                st.session_state.logged = True
                st.session_state.user = u
                st.session_state.login_time = datetime.now()
                st.rerun()
            else:
                st.error("Invalid credentials")

    with t2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            st.session_state.users[nu] = np
            st.success("Account created. Login now.")

# ================= MAIN APP =================
def app():
    # -------- SETTINGS --------
    st.sidebar.header("⚙️ Settings")
    st.session_state.theme = st.sidebar.selectbox("Theme", ["Light","Dark"])
    st.session_state.font = st.sidebar.selectbox("Font Size", ["Small","Medium","Large"])
    st.session_state.mascot = st.sidebar.selectbox("Mascot", ["🐢","🧑‍⚕️","🤖","🐼","🦉"])
    st.session_state.motivation = st.sidebar.checkbox("Motivation Messages", True)

    if st.sidebar.button("Clear Today Medicines"):
        st.session_state.meds = []
    if st.sidebar.button("Reset Streak"):
        st.session_state.streak = 0
    if st.sidebar.button("Logout"):
        st.session_state.logged = False
        st.rerun()

    st.sidebar.info("⚠️ Educational app\nAlways consult doctor")

    left, right = st.columns([2,1])

    # -------- LEFT --------
    with left:
        st.title("➕ Add Medicine")

        c1, c2 = st.columns([3,1])
        with c2:
            st.markdown(f"<div class='mascot'>{st.session_state.mascot}</div>", unsafe_allow_html=True)

        with c1:
            with st.form("add"):
                name = st.text_input("Medicine Name")
                mtype = st.selectbox("Type", ["Tablet","Syrup","Injection","Drops"])
                t = st.time_input("Time", time(8,0))
                dose = st.text_input("Dosage")
                pros = st.text_input("Pros")
                cons = st.text_input("Cons")
                if st.form_submit_button("Add") and name:
                    st.session_state.meds.append({
                        "name":name,"type":mtype,"time":t,
                        "dose":dose,"pros":pros,"cons":cons,"taken":False
                    })

        st.subheader("📋 Today Checklist")
        now = datetime.now().time()
        taken = 0

        for i,m in enumerate(st.session_state.meds):
            status = "🟢 Taken" if m["taken"] else "🔴 Missed" if now > m["time"] else "🟡 Upcoming"
            a,b,c,d = st.columns([3,2,2,1])
            a.write(f"{m['name']} ({m['type']})")
            b.write(m["time"].strftime("%I:%M %p"))
            c.write(status)
            if not m["taken"] and d.button("✔", key=i):
                m["taken"] = True
            if m["taken"]:
                taken += 1

    # -------- RIGHT --------
    with right:
        st.subheader("💊 Medicine Suggestions")
        for n,t,d,p,c in COMMON_MEDS:
            with st.expander(n):
                st.write(f"**Type:** {t}")
                st.write(f"**Dosage:** {d}")
                st.write(f"✅ Pros: {p}")
                st.write(f"⚠️ Cons: {c}")

        total = len(st.session_state.meds)
        score = int((taken/total)*100) if total else 0
        if score == 100 and total > 0:
            st.session_state.streak += 1

        st.metric("Adherence", f"{score}%")
        st.metric("🔥 Streak", st.session_state.streak)

        if st.session_state.motivation:
            st.success(st.session_state.current_quote)

# ================= RUN =================
if not st.session_state.logged:
    login()
else:
    app()
