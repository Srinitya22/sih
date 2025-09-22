import streamlit as st
import json
import os
from datetime import date
import modules.auth as auth
import modules.recommender as recommender
import modules.roadmap as roadmap

# ---------------- Tailwind CSS ----------------
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
""", unsafe_allow_html=True)

# ---------------- Load Data ----------------
DATA_PATH = os.path.join("data","career_tree.json")
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

# ---------------- Authentication ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.markdown("""
    <div class="bg-gradient-to-r from-purple-500 to-indigo-600 text-white p-6 rounded-2xl shadow-lg text-center">
      <h1 class="text-4xl font-bold mb-4">Career Compass</h1>
      <p class="text-lg">Your personalized career & education advisor 🚀</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")
    st.subheader("✨ Login / Sign Up")

    login_email = st.text_input("Email")
    login_password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = auth.login(login_email, login_password)
        if user:
            st.session_state.user = user
            st.success(f"Logged in as {user['name']} ✅")
            st.experimental_rerun()
        else:
            st.error("Invalid email or password.")

    st.markdown("---")
    st.subheader("Sign Up")
    signup_name = st.text_input("Name")
    signup_email = st.text_input("Email", key="signup_email")
    signup_password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Sign Up"):
        success, message = auth.signup(signup_name, signup_email, signup_password)
        if success:
            st.success(message)
        else:
            st.error(message)

else:
    # ---------------- Dashboard ----------------
    user = st.session_state.user

    st.markdown(f"""
    <div class="bg-gradient-to-r from-green-400 to-blue-500 text-white p-6 rounded-2xl shadow-lg mb-4">
      <h2 class="text-2xl font-bold">👋 Welcome, {user['name']}</h2>
      <p>{daily_affirmation()}</p>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- Sidebar Navigation ----------------
    menu = st.sidebar.radio("📍 Navigate", ["Home","Profile","Explore","Quiz","About Us","Notifications","Logout"])

    if menu=="Logout":
        st.session_state.user = None
        st.experimental_rerun()

    # ---------------- Home ----------------
    if menu=="Home":
        st.header("🏠 Home")
        st.write("Welcome to Career Compass! Here’s your daily insight:")
        st.info("💡 Tip: Explore courses, take the quiz, and find colleges that match your interests.")
        st.markdown("---")
        st.subheader("Featured Courses")
        courses = set()
        for c in DATA["colleges"]:
            for cr in c["courses"]:
                courses.add(cr)
        for course in sorted(courses):
            st.write(f"- {course}")

    # ---------------- Profile ----------------
    if menu=="Profile":
        st.header("👤 Profile")
        st.write(f"**Name:** {user['name']}")
        st.write(f"**Email:** {user['email']}")

    # ---------------- Explore ----------------
    if menu=="Explore":
        st.header("🔎 Explore Colleges & Careers")
        search_text = st.text_input("Search term")
        search_type = st.selectbox("Search by", ["Select","College","Course","Career"])
        if st.button("Search"):
            if search_type=="College":
                results = [c["name"] for c in DATA["colleges"] if search_text.lower() in c["name"].lower()]
                if results:
                    st.write("Colleges found:")
                    for r in results:
                        st.write(f"- {r}")
                else:
                    st.warning("No colleges found.")
            elif search_type=="Course":
                results = []
                for c in DATA["colleges"]:
                    for cr in c["courses"]:
                        if search_text.lower() in cr.lower():
                            results.append(f"{cr} ({c['name']})")
                if results:
                    st.write("Courses found:")
                    for r in results:
                        st.write(f"- {r}")
                else:
                    st.warning("No courses found.")
            elif search_type=="Career":
                if search_text in DATA["careers"]:
                    st.write(f"Career roadmap available for {search_text}")
                    roadmap.show_roadmap(search_text)
                else:
                    st.warning("Career not found.")

    # ---------------- Quiz ----------------
    if menu=="Quiz":
        st.header("🎯 Career Quiz")

        if "quiz_step" not in st.session_state:
            st.session_state.quiz_step = 1
            st.session_state.answers = []
            st.session_state.quiz_result = None

        # Step 1: Main Interests
        if st.session_state.quiz_step == 1:
            st.subheader("What are your main interests?")
            options = list(DATA["career_fields"].keys())
            choice = st.radio("Select your interest:", options)
            if st.button("Next Question"):
                st.session_state.answers.append(choice)
                st.session_state.quiz_step = 2
                st.session_state.selected_field = choice
                st.experimental_rerun()

        # Step 2: Courses in that field
        elif st.session_state.quiz_step == 2:
            field = st.session_state.selected_field
            st.subheader(f"Which course in {field} are you interested in?")
            courses = DATA["career_fields"][field]
            choice = st.radio("Select a course:", courses)
            if st.button("Next Question"):
                st.session_state.answers.append(choice)
                st.session_state.quiz_result = choice
                st.session_state.quiz_step = 3
                st.experimental_rerun()

        # Step 3: Show Recommendation + Roadmap + Colleges
        elif st.session_state.quiz_step == 3:
            course = st.session_state.quiz_result
            st.success(f"✅ Based on your answers, we suggest: **{course}**")
            roadmap.show_roadmap(course)
            colleges = recommender.colleges_for_course(course, DATA)
            if colleges:
                st.subheader("🏫 Recommended Colleges")
                for c in colleges:
                    st.write(f"- {c}")
            st.markdown("---")
            if st.button("Restart Quiz"):
                st.session_state.quiz_step = 1
                st.session_state.answers = []
                st.session_state.quiz_result = None
                st.experimental_rerun()

    # ---------------- About Us ----------------
    if menu=="About Us":
        st.header("ℹ️ About Us")
        st.write("Career Compass: Your personalized career & education advisor. Explore courses, find colleges, and build your roadmap!")

    # ---------------- Notifications ----------------
    if menu=="Notifications":
        st.header("📢 Notifications")
        for n in DATA.get("notifications", []):
            st.info(n["msg"])
