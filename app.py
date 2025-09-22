import streamlit as st
import json
import os
from datetime import date
import modules.roadmap as roadmap

# ---------------- Tailwind (optional styling) ----------------
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
""", unsafe_allow_html=True)

# ---------------- Load career DB ----------------
DATA_PATH = os.path.join("data", "career_tree.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)

# ---------------- Daily Affirmation ----------------
def daily_affirmation():
    affirmations = [
        "🌟 You are capable of amazing things.",
        "🚀 Small steps every day lead to big changes.",
        "💡 Believe in yourself and your potential.",
        "🌱 Curiosity is your superpower — explore.",
        "🔥 Every attempt is progress."
    ]
    idx = date.today().toordinal() % len(affirmations)
    return affirmations[idx]

# ---------------- Session State Initialization ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if "quiz_step" not in st.session_state:
    st.session_state.quiz_step = None
if "selected_interest" not in st.session_state:
    st.session_state.selected_interest = None
if "selected_course" not in st.session_state:
    st.session_state.selected_course = None
if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None

# ---------------- Login ----------------
if not st.session_state.user:
    st.markdown("""
    <div class="bg-gradient-to-r from-purple-500 to-indigo-600 text-white p-6 rounded-2xl shadow-lg text-center">
      <h1 class="text-4xl font-bold mb-4">Career Compass</h1>
      <p class="text-lg">Your personalized career & education advisor 🚀</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("✨ Login")
    if st.button("Demo Login"):
        st.session_state.user = {"name": "User", "email": "demo@example.com"}
        st.success("Logged in ✅")
else:
    # ---------------- Dashboard ----------------
    user = st.session_state.user
    st.markdown(f"""
    <div class="bg-gradient-to-r from-green-400 to-blue-500 text-white p-6 rounded-2xl shadow-lg mb-4">
      <h2 class="text-2xl font-bold">👋 Welcome, {user['name']}</h2>
      <p>{daily_affirmation()}</p>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- Menu ----------------
    menu = st.sidebar.radio("📍 Navigate", ["Home","Quiz","Roadmap","About","Logout"])

    if menu == "Logout":
        st.session_state.user = None
        st.session_state.quiz_step = None
        st.session_state.selected_interest = None
        st.session_state.selected_course = None
        st.session_state.quiz_result = None
        st.experimental_rerun()

    # ---------------- Home ----------------
    if menu == "Home":
        st.header("🏠 Home")
        search_text = st.text_input("Free Search (College / Course / Career)")
        filter_type = st.selectbox("Filter by", ["Select", "College", "Course", "Career"])

        if st.button("Search"):
            if filter_type == "College":
                names = [c["name"] for c in DATA["colleges"]]
                st.write("Colleges:", names)
            elif filter_type == "Course":
                st.write("Courses across colleges:")
                for c in DATA["colleges"]:
                    for cr in c["courses"]:
                        if search_text.lower() in cr.lower():
                            st.write(f"- {cr} ({c['name']})")
            elif filter_type == "Career":
                if search_text in DATA["careers"]:
                    roadmap.show_roadmap(search_text)
                else:
                    st.error("Career not found in demo dataset")

        st.markdown("---")
        st.subheader("📢 Notifications")
        for n in DATA["notifications"]:
            st.info(n["msg"])

    # ---------------- Quiz ----------------
    if menu == "Quiz":
        st.header("🎯 Career Quiz")

        # Step 1: Select interest
        if st.session_state.quiz_step is None:
            st.session_state.quiz_step = "interest"

        if st.session_state.quiz_step == "interest":
            interest = st.radio("What are your main interests?", ["Engineering", "Medical", "Commerce", "Arts", "Architecture", "Other"])
            if st.button("Next - Select Interest"):
                st.session_state.selected_interest = interest
                st.session_state.quiz_step = "course"

        # Step 2: Select course based on interest
        elif st.session_state.quiz_step == "course":
            interest = st.session_state.selected_interest
            # Map available courses for each interest
            interest_courses_map = {
                "Engineering": ["B.E.", "B.Tech", "BCA"],
                "Medical": ["MBBS", "B.Sc. Nursing", "BDS", "BAMS", "B.Sc. Paramedical"],
                "Commerce": ["BBA", "Commerce", "MCA"],
                "Arts": ["B.A.", "B.Sc. Home Science", "B.Sc.", "Hons."],
                "Architecture": ["B.Arch."],
                "Other": ["Culinary", "Photography", "Management"]
            }
            courses = interest_courses_map.get(interest, [])
            course = st.radio(f"Which course in {interest} are you interested in?", courses)
            if st.button("Next - Get Recommendation"):
                st.session_state.selected_course = course
                st.session_state.quiz_step = "result"

        # Step 3: Show recommendation
        elif st.session_state.quiz_step == "result":
            course = st.session_state.selected_course
            st.session_state.quiz_result = course
            st.success(f"✅ Based on your answers, we suggest: **{course}**")
            matching_colleges = []
            for c in DATA["colleges"]:
                for cr in c["courses"]:
                    if course.lower() in cr.lower():
                        matching_colleges.append(c["name"])
            if matching_colleges:
                st.write("You may consider these colleges:")
                for col in matching_colleges:
                    st.write(f"- {col}")
            if st.button("View Roadmap"):
                if course in DATA["careers"]:
                    roadmap.show_roadmap(course)
                else:
                    st.info("No roadmap available for this course.")

    # ---------------- Roadmap ----------------
    if menu == "Roadmap":
        st.header("🛤 Career Roadmap")
        career = st.text_input("Enter a career to view roadmap")
        if st.button("Show Roadmap"):
            if career in DATA["careers"]:
                roadmap.show_roadmap(career)
            else:
                st.info("No roadmap available for this career.")

    # ---------------- About ----------------
    if menu == "About":
        st.header("ℹ️ About")
        st.write("Prototype for Personalized Career & Education Advisor.")
