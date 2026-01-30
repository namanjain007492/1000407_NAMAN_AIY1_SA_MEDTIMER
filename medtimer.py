import streamlit as st
from datetime import date, timedelta
import hashlib

# ================== PAGE CONFIG ==================
st.set_page_config(page_title="MedTimer Pro", layout="wide")

# ================== SESSION INIT ==================
def init_state():
    return {
        "users": {},
        "logged_in": False,
        "current_user": None,
        "theme": "Dark",
        "mascot": "🩺",
        "medicines": [],
        "taken": {},
        "celebrate": True
    }

if "app" not in st.session_state:
    st.session_state.app = init_state()

# ================== THEME FUNCTION ==================
def apply_theme():
    theme = st.session_state.app["theme"]
    if theme == "Dark":
        st.markdown("""
        <style>
        .stApp { background-color:#0f172a; color:white; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp { background-color:white; color:black; }
        </style>
        """, unsafe_allow_html=True)

apply_theme()

# ================== HELPERS ==================
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def today_key():
    return str(date.today())

def daily_adherence():
    meds = st.session_state.app["medicines"]
    taken = st.session_state.app["taken"].get(today_key(), [])
    return (len(taken) / len(meds) * 100) if meds else 0

def weekly_adherence():
    meds = st.session_state.app["medicines"]
    if not meds:
        return 0
    total = 0
    for i in range(7):
        d = str(date.today() - timedelta(days=i))
        total += len(st.session_state.app["taken"].get(d, [])) / len(meds) * 100
    return total / 7

# ================== LOGIN / SIGNUP ==================
if not st.session_state.app["logged_in"]:
    st.title("💊 MedTimer Pro")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in st.session_state.app["users"] and st.session_state.app["users"][u] == hash_pw(p):
                st.session_state.app["logged_in"] = True
                st.session_state.app["current_user"] = u
                st.success("Logged in successfully")
            else:
                st.error("Invalid credentials")

    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            if nu in st.session_state.app["users"]:
                st.error("User already exists")
            else:
                st.session_state.app["users"][nu] = hash_pw(np)
                st.success("Account created! Please login")

    st.stop()

# ================== SIDEBAR ==================
st.sidebar.title(f"{st.session_state.app['mascot']} MedTimer")

menu = st.sidebar.radio(
    "Menu",
    ["Home", "Medicines", "Suggestions", "Settings"]
)

# ================== HOME ==================
if menu == "Home":
    st.title("🏠 Home")

    st.metric("Daily Adherence", f"{daily_adherence():.0f}%")
    st.metric("Weekly Adherence", f"{weekly_adherence():.0f}%")

    st.subheader("Today's Medicines")

    for i, m in enumerate(st.session_state.app["medicines"]):
        checked = m["name"] in st.session_state.app["taken"].get(today_key(), [])
        if st.checkbox(f"{m['name']} – {m['dose']} at {m['time']}", value=checked, key=f"take{i}"):
            if not checked:
                st.session_state.app["taken"].setdefault(today_key(), []).append(m["name"])
                if st.session_state.app["celebrate"]:
                    st.balloons()

# ================== MEDICINES ==================
elif menu == "Medicines":
    st.title("💊 Medicines")

    with st.form("add_med"):
        n = st.text_input("Medicine Name")
        t = st.time_input("Time")
        d = st.text_input("Dose")
        if st.form_submit_button("Add Medicine"):
            st.session_state.app["medicines"].append({
                "name": n,
                "time": str(t),
                "dose": d
            })
            st.success("Medicine added")

    for i, m in enumerate(st.session_state.app["medicines"]):
        with st.expander(m["name"]):
            m["name"] = st.text_input("Name", m["name"], key=f"n{i}")
            m["time"] = st.text_input("Time", m["time"], key=f"t{i}")
            m["dose"] = st.text_input("Dose", m["dose"], key=f"d{i}")
            if st.button("Delete", key=f"del{i}"):
                st.session_state.app["medicines"].pop(i)
                st.warning("Deleted")

# ================== SUGGESTIONS ==================
elif menu == "Suggestions":
    st.title("🧠 Medicine Suggestions")

    data = {
        "Fever": ("Paracetamol", "Reduces fever", "Liver risk"),
        "Cold": ("Cetirizine", "Relieves allergy", "Drowsiness"),
        "Headache": ("Ibuprofen", "Pain relief", "Stomach upset"),
        "Diabetes": ("Metformin", "Controls sugar", "Nausea"),
        "Blood Pressure": ("Amlodipine", "Controls BP", "Dizziness")
    }

    disease = st.selectbox("Select Disease", list(data))
    med, pros, cons = data[disease]

    st.write(f"**Medicine:** {med}")
    st.write(f"✅ Pros: {pros}")
    st.write(f"⚠️ Cons: {cons}")

    if st.button("Add this medicine"):
        st.session_state.app["medicines"].append({
            "name": med,
            "time": "09:00",
            "dose": "Standard"
        })
        st.success("Added")

# ================== SETTINGS ==================
elif menu == "Settings":
    st.title("⚙️ Settings")

    st.session_state.app["theme"] = st.selectbox(
        "Theme",
        ["Dark", "Light"],
        index=["Dark", "Light"].index(st.session_state.app["theme"])
    )

    st.session_state.app["mascot"] = st.selectbox(
        "Mascot",
        ["🩺", "🐶", "🐱", "🐼", "🦊"],
        index=["🩺", "🐶", "🐱", "🐼", "🦊"].index(st.session_state.app["mascot"])
    )

    st.session_state.app["celebrate"] = st.checkbox(
        "Celebrate on medicine taken",
        value=st.session_state.app["celebrate"]
    )

    apply_theme()

    if st.button("Reset All Medicines"):
        st.session_state.app["medicines"].clear()
        st.session_state.app["taken"].clear()
        st.warning("All medicines reset")

    if st.button("Logout"):
        st.session_state.clear()
        st.success("Logged out")
