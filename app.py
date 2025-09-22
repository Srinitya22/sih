import streamlit as st
import json
import os
from datetime import date
import modules.auth as auth
import modules.recommender as recommender
import modules.roadmap as roadmap

# 🔹 Tailwind injection
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
""", unsafe_allow_html=True)

# Load career and college data
DATA_PATH = os.path.join("data", "career_tree.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)

# Daily affirmation
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
    st.subheader("✨ Login")
    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        user = auth.login(login_email, login_password)
        if user:
            st.session_state.user = user
            st.success(f"Logged in as {user['name']}")
            st.experimental_rerun()
        else:
            st.error("Invalid email or password")

    st.write("---")
    st.subheader("📝 Sign Up")
    signup_name = st.text_input("Name", key="signup_name")
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
      <p>📌 Tip: Explore courses and colleges based on your interests!</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Menu
    menu = st.sidebar.radio("📍 Navigate", ["Home", "Profile", "Explore", "Quiz", "Notifications", "About Us", "Logout"])

    if menu == "Logout":
        st.session_state.user = None
        st.experimental_rerun()

    # ---------------- Home ----------------
    if menu == "Home":
        st.header("🏠 Home")
        st.write("Welcome to your career compass dashboard!")
        st.write("Explore courses, colleges, and personalized recommendations.")
        st.write("✨ Check back daily for motivation and tips!")

    # ---------------- Profile ----------------
    if menu == "Profile":
        st.header("👤 Profile")
        st.write(f"Name: {user['name']}")
        st.write(f"Email: {user['email']}")

    # ---------------- Explore ----------------
    if menu == "Explore":
        st.header("🔎 Explore Colleges & Careers")
        search_type = st.selectbox("Search by:", ["Select", "College", "Course", "Career"])
        query = st.text_input("Enter search text")
        if st.button("Search"):
            if search_type == "College":
                results = [c["name"] for c in DATA["colleges"] if query.lower() in c["name"].lower()]
                if results:
                    st.write("🏫 Colleges found:")
                    for r in results:
                        st.write(f"- {r}")
                else:
                    st.write("No colleges found")
            elif search_type == "Course":
                found = []
                for c in DATA["colleges"]:
                    for cr in c["courses"]:
                        if query.lower() in cr.lower():
                            found.append(f"{cr} ({c['name']})")
                if found:
                    st.write("📚 Courses found:")
                    for f in found:
                        st.write(f"- {f}")
                else:
                    st.write("No courses found")
            elif search_type == "Career":
                if query in DATA["careers"]:
                    roadmap.show_roadmap(query)
                else:
                    st.write("Career not found")

    # ---------------- Quiz ----------------
    if menu == "Quiz":
        st.header("🎯 Career Quiz")

        # Define quiz tree dynamically
        quiz_tree = {
            "Q1": {"q": "What are your main interests?",
                   "options": ["Engineering", "Medical", "Commerce", "Arts", "Architecture", "Other"]},
            "Q2-Engineering": {"q": "Which branch of Engineering interests you?",
                                "options": ["CSE", "ECE", "Mechanical", "Civil"]},
            "Q2-Medical": {"q": "Which field of Medical/Healthcare interests you?",
                           "options": ["MBBS", "BDS", "BAMS", "B.Sc. Nursing", "B.Sc. Paramedical"]},
            "Q2-Commerce": {"q": "Which course in Commerce are you interested in?",
                             "options": ["BBA", "B.Com", "CA/CPA"]},
            "Q2-Arts": {"q": "Which course in Arts are you interested in?",
                        "options": ["BA", "BFA", "B.Sc. Home Science"]},
            "Q2-Architecture": {"q": "Which Architecture course are you interested in?",
                                 "options": ["B.Arch."]},
            "Q2-Other": {"q": "Which other courses are you interested in?",
                         "options": ["Diploma", "Certificate"]}
        }

        if "quiz_step" not in st.session_state:
            st.session_state.quiz_step = "Q1"
            st.session_state.answers = []
            st.session_state.quiz_result = None

        node = quiz_tree[st.session_state.quiz_step]
        choice = st.radio(node["q"], node["options"], key=st.session_state.quiz_step)

        if st.button("Next Question"):
            st.session_state.answers.append(choice)
            next_key = f"Q2-{choice}"
            if next_key in quiz_tree:
                st.session_state.quiz_step = next_key
            else:
                st.session_state.quiz_result = choice
                st.success(f"✅ Based on your answers, we suggest: **{choice}**")

        if st.session_state.quiz_result:
            course = st.session_state.quiz_result
            st.markdown(f"🛤 **Roadmap for {course}**")
            roadmap.show_roadmap(course)
            # Recommended colleges
            colleges = recommender.colleges_for_course(course)
            if colleges:
                st.markdown(f"🏫 **Recommended Colleges for {course}:**")
                for c in colleges:
                    st.write(f"- {c}")
            else:
                st.write(f"No colleges found offering {course} in the dataset.")

    # ---------------- Notifications ----------------
    if menu == "Notifications":
        st.header("📢 Notifications")
        for n in DATA["notifications"]:
            st.info(n["msg"])

    # ---------------- About Us ----------------
    if menu == "About Us":
        st.header("ℹ️ About Us")
        st.write("Personalized Career & Education Advisor App")
        st.write("Provides career recommendations, college info, and roadmap guidance based on your interests.")
