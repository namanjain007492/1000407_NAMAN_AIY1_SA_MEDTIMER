import streamlit as st
import pandas as pd
from datetime import date, time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MedTimer", layout="wide")

# ---------------- STATE INIT ----------------
if "meds" not in st.session_state:
    st.session_state.meds = []
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None
if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "mascot" not in st.session_state:
    st.session_state.mascot = "🐢 Turtle"

# ---------------- THEME ----------------
def apply_theme():
    if st.session_state.theme == "Dark":
        st.markdown("""
        <style>
        body { background:#0e1117; color:white; }
        </style>
        """, unsafe_allow_html=True)

apply_theme()

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙ Settings")

st.session_state.theme = st.sidebar.selectbox(
    "Theme", ["Light", "Dark"],
    index=0 if st.session_state.theme == "Light" else 1
)

st.session_state.mascot = st.sidebar.selectbox(
    "Mascot", ["🐢 Turtle", "🐶 Dog", "🐱 Cat", "🦁 Lion"]
)

st.sidebar.divider()

# ---------------- ADD / EDIT MED ----------------
st.title("💊 MedTimer")

if st.session_state.edit_id is None:
    st.subheader("➕ Add Medicine")

    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Medicine name")
        t = st.time_input("Time", value=time(8, 0))
        submitted = st.form_submit_button("Add Medicine")

        if submitted and name:
            st.session_state.meds.append({
                "id": len(st.session_state.meds),
                "name": name,
                "time": t.strftime("%H:%M"),
                "taken": False,
                "date": str(date.today())
            })

else:
    med = st.session_state.meds[st.session_state.edit_id]
    st.subheader("✏ Edit Medicine")

    with st.form("edit_form"):
        new_name = st.text_input("Medicine name", med["name"])
        new_time = st.text_input("Time (HH:MM)", med["time"])
        save = st.form_submit_button("Save")
        cancel = st.form_submit_button("Cancel")

        if save:
            med["name"] = new_name
            med["time"] = new_time
            st.session_state.edit_id = None

        if cancel:
            st.session_state.edit_id = None

st.divider()

# ---------------- MED LIST ----------------
st.subheader("📋 Today’s Medicines")

if not st.session_state.meds:
    st.info("No medicines added yet.")
else:
    for i, med in enumerate(st.session_state.meds):
        c1, c2, c3, c4, c5 = st.columns([3,2,2,1,1])

        c1.write(med["name"])
        c2.write(med["time"])

        med["taken"] = c3.checkbox(
            "Taken",
            med["taken"],
            key=f"taken_{i}"
        )

        if c4.button("✏", key=f"edit_{i}"):
            st.session_state.edit_id = i

        if c5.button("🗑", key=f"del_{i}"):
            st.session_state.meds.pop(i)
            st.session_state.edit_id = None
            st.stop()

# ---------------- ADHERENCE ----------------
if st.session_state.meds:
    taken = sum(m["taken"] for m in st.session_state.meds)
    total = len(st.session_state.meds)
    percent = int((taken / total) * 100)

    st.subheader("📊 Daily Adherence")
    st.progress(percent)
    st.write(f"**{percent}% completed**")

    df = pd.DataFrame(st.session_state.meds)
    weekly = df.groupby("date")["taken"].mean() * 100

    st.subheader("📅 Weekly Adherence")
    st.line_chart(weekly)

# ---------------- MASCOT ----------------
st.subheader("🐾 Mascot")

if not st.session_state.meds:
    st.info(f"{st.session_state.mascot} says: Add medicines to begin!")
elif percent == 100:
    st.success(f"{st.session_state.mascot} is PROUD of you 🎉")
elif percent >= 50:
    st.warning(f"{st.session_state.mascot} says: Almost there!")
else:
    st.error(f"{st.session_state.mascot} says: Don’t forget your meds!")
