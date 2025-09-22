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

# Load career/college data
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
    st.subheader("✨ Login / Sign Up")

    # Login Form
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            user = auth.login(email, password)
            if user:
                st.session_state.user = user
                st.success(f"Logged in as {user['name']}")
                st.experimental_rerun()
            else:
                st.error("Invalid email or password")

    st.markdown("-----")

    # Sign-up Form
    with st.form("signup_form"):
        st.subheader("Create an account")
        name = st.text_input("Name")
        signup_email = st.text_input("Email")
        signup_password = st.text_input("Password", type="password")
        signup_submit = st.form_submit_button("Sign Up")
        if signup_submit:
            success, message = auth.signup(name, signup_email, signup_password)
            if success:
                st.success("Account created successfully! Please log in.")
            else:
                st.error(message)

else:
    # ---------------- Dashboard ----------------
    user = st.session_state.user
    st.sidebar.title(f"👤 {user['name']}")
    menu = st.sidebar.radio("📍 Navigate", ["Home", "Profile", "Explore", "Quiz", "Notifications", "About", "Logout"])

    if menu == "Logout":
        st.session_state.user = None
        st.experimental_rerun()

    # ---------------- Home ----------------
    if menu == "Home":
        st.header("🏠 Home")
        st.markdown(f"""
        <div class="bg-gradient-to-r from-green-400 to-blue-500 text-white p-6 rounded-2xl shadow-lg mb-4">
          <h2 class="text-2xl font-bold">👋 Welcome, {user['name']}</h2>
          <p>{daily_affirmation()}</p>
        </div>
        """, unsafe_allow_html=True)

        # Extra section
        st.subheader("✨ Today's Tip")
        st.info("Set clear goals and explore courses that align with your strengths.")

    # ---------------- Profile ----------------
    if menu == "Profile":
        st.header("📝 Profile")
        st.write(f"**Name:** {user['name']}")
        st.write(f"**Email:** {user['email']}")

    # ---------------- Explore ----------------
    if menu == "Explore":
        st.header("🔎 Explore Colleges and Courses")
        search_type = st.radio("Search by:", ["College", "Course", "Career"])
        search_text = st.text_input("Enter keyword")

        if st.button("Search"):
            if search_type == "College":
                matched = [c["name"] for c in DATA["colleges"] if search_text.lower() in c["name"].lower()]
                if matched:
                    st.write("🏫 Colleges Found:")
                    for m in matched:
                        st.write(f"- {m}")
                else:
                    st.warning("No matching colleges found.")

            elif search_type == "Course":
                matched_courses = []
                for c in DATA["colleges"]:
                    for cr in c["courses"]:
                        if search_text.lower() in cr.lower():
                            matched_courses.append((cr, c["name"]))
                if matched_courses:
                    st.write("📚 Courses Found:")
                    for cr, clg in matched_courses:
                        st.write(f"- {cr} ({clg})")
                else:
                    st.warning("No matching courses found.")

            elif search_type == "Career":
                if search_text in DATA["careers"]:
                    roadmap.show_roadmap(search_text)
                else:
                    st.warning("Career not found in dataset.")

    # ---------------- Quiz ----------------
    if menu == "Quiz":
        st.header("🎯 Career Quiz")

        # Quiz Tree Example
        quiz_tree = {
            "Q1": {"q": "What are your main interests?", "options": ["Engineering", "Medical", "Commerce", "Arts", "Architecture", "Other"]},
            "Q2-Engineering": {"q": "Which branch of Engineering interests you?", "options": ["CSE", "ECE", "Mechanical", "Civil"]},
            "Q2-Medical": {"q": "Which field of Medical are you interested in?", "options": ["MBBS", "BDS", "BAMS", "B.Sc. Nursing", "Paramedical"]},
            "Q2-Commerce": {"q": "Which course in Commerce are you interested in?", "options": ["BBA", "B.Com", "CA/CPA"]},
            "Q2-Arts": {"q": "Which field of Arts are you interested in?", "options": ["Literature", "Psychology", "History", "Fine Arts"]},
            "Q2-Architecture": {"q": "Which Architecture course are you interested in?", "options": ["B.Arch"]},
            "Q2-Other": {"q": "Other courses"}
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

        if st.session_state.quiz_result:
            st.success(f"✅ Based on your answers, we suggest: **{st.session_state.quiz_result}**")

            # Show roadmap
            roadmap.show_roadmap(st.session_state.quiz_result)

            # Show recommended colleges
            colleges = recommender.colleges_for_course(st.session_state.quiz_result)
            if colleges:
                st.subheader("🏫 Recommended Colleges for this course:")
                for clg in colleges:
                    st.write(f"- {clg}")
            else:
                st.warning("No colleges found offering this course in the dataset.")

            if st.button("Restart Quiz"):
                st.session_state.quiz_step = "Q1"
                st.session_state.answers = []
                st.session_state.quiz_result = None

    # ---------------- Notifications ----------------
    if menu == "Notifications":
        st.header("📢 Notifications")
        for n in DATA["notifications"]:
            st.info(n["msg"])

    # ---------------- About ----------------
    if menu == "About":
        st.header("ℹ️ About Us")
        st.write("Prototype for Career Compass — Personalized Career & Education Advisor.")
