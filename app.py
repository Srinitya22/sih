import streamlit as st
import json
import os
from datetime import date
import modules.auth as auth
import modules.roadmap as roadmap

# 🔹 Tailwind injection
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
""", unsafe_allow_html=True)

# Load career DB
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

    st.info("➡️ For demo, press 'Login' to continue.")
    if st.button("Login"):
        st.session_state.user = {"name": "User", "email": "demo@example.com"}
        st.rerun()

else:
    # ---------------- Dashboard ----------------
    user = st.session_state.user

    st.markdown(f"""
    <div class="bg-gradient-to-r from-green-400 to-blue-500 text-white p-6 rounded-2xl shadow-lg mb-4">
      <h2 class="text-2xl font-bold">👋 Welcome, {user['name']}</h2>
      <p>{daily_affirmation()}</p>
    </div>
    """, unsafe_allow_html=True)

    # Menu
    menu = st.sidebar.radio("📍 Navigate", ["Home", "Quiz", "Roadmap", "About", "Logout"])

    if menu == "Logout":
        st.session_state.user = None
        st.rerun()

    # ---------------- Home ----------------
    if menu == "Home":
        st.header("🏠 Home")

        # Search Section
        st.markdown("""
        <div class="bg-white p-4 rounded-xl shadow-md mb-4">
          <h3 class="text-xl font-bold">🔎 Search</h3>
        </div>
        """, unsafe_allow_html=True)

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
                    st.error("Career not found in dataset")

        st.markdown("---")
        st.subheader("📢 Notifications")
        for n in DATA["notifications"]:
            st.info(n["msg"])

    # ---------------- Quiz ----------------
    if menu == "Quiz":
        st.header("🎯 Career Quiz")

        # Quiz Tree (multi-level)
        quiz_tree = {
            "Q1": {
                "q": "What are your main interests?",
                "options": ["Engineering", "Medical", "Commerce", "Arts", "Architecture", "Other"]
            },
            "Q2-Engineering": {
                "q": "Which Engineering course are you interested in?",
                "options": ["B.E.", "B.Tech"]
            },
            "Q2-Medical": {
                "q": "Which field are you interested in?",
                "options": ["MBBS", "B.Sc. Nursing", "BAMS", "B.Sc. Paramedical"]
            },
            "Q2-Commerce": {
                "q": "Which course in Commerce are you interested in?",
                "options": ["BBA", "B.Com", "CA/CPA"]
            },
            "Q2-Arts": {
                "q": "Which Arts course are you interested in?",
                "options": ["B.A.", "BFA", "BA(Hons.)"]
            },
            "Q2-Architecture": {
                "q": "Which Architecture course are you interested in?",
                "options": ["B.Arch."]
            },
            "Q2-Other": {
                "q": "Which other course are you interested in?",
                "options": ["BCA", "Diploma", "Other"]
            },
            # Q3 for Engineering specializations
            "Q3-B.Tech": {
                "q": "Which B.Tech branch are you interested in?",
                "options": ["CSE", "ECE", "Mechanical", "Civil", "IT", "Electrical"]
            },
            "Q3-B.E.": {
                "q": "Which B.E. branch are you interested in?",
                "options": ["CSE", "ECE", "Mechanical", "Civil", "IT", "Electrical"]
            }
        }

        # Initialize quiz state
        if "quiz_step" not in st.session_state:
            st.session_state.quiz_step = "Q1"
            st.session_state.quiz_answers = []
            st.session_state.quiz_result = None

        # Restart
        if st.button("🔄 Restart Quiz"):
            st.session_state.quiz_step = "Q1"
            st.session_state.quiz_answers = []
            st.session_state.quiz_result = None
            st.rerun()

        node = quiz_tree.get(st.session_state.quiz_step)

        if node:
            choice = st.radio(node["q"], node["options"], key=f"{st.session_state.quiz_step}_radio")

            if st.button("Next Question"):
                st.session_state.quiz_answers.append(choice)

                if st.session_state.quiz_step == "Q1":
                    next_step = f"Q2-{choice}"
                    if next_step in quiz_tree:
                        st.session_state.quiz_step = next_step
                        st.rerun()

                elif st.session_state.quiz_step.startswith("Q2-"):
                    next_step = f"Q3-{choice}"
                    if next_step in quiz_tree:
                        st.session_state.quiz_step = next_step
                        st.rerun()
                    else:
                        st.session_state.quiz_result = choice
                        st.success(f"✅ Based on your answers, we suggest: **{choice}**")

                elif st.session_state.quiz_step.startswith("Q3-"):
                    st.session_state.quiz_result = choice
                    st.success(f"✅ Based on your answers, we suggest: **{choice}**")

        else:
            if st.session_state.quiz_result:
                st.success(f"✅ Based on your answers, we suggest: **{st.session_state.quiz_result}**")

        # Roadmap + Colleges
        if st.session_state.quiz_result:
            if st.button("View Roadmap"):
                course = st.session_state.quiz_result

                # Roadmap
                if course in DATA["careers"]:
                    steps = DATA["careers"][course]
                else:
                    steps = [
                        f"Step 1: Explore basics of {course}",
                        f"Step 2: Take relevant courses or certifications in {course}",
                        f"Step 3: Gain practical experience through projects or internships",
                        f"Step 4: Build portfolio and network",
                        f"Step 5: Apply for professional opportunities in {course}"
                    ]

                st.subheader(f"🛤 Roadmap for {course}")
                for step in steps:
                    st.write("-", step)

                # Colleges
                recommended_colleges = []
                for c in DATA["colleges"]:
                    if any(course.lower() in cr.lower() for cr in c["courses"]):
                        recommended_colleges.append(c["name"])

                if recommended_colleges:
                    st.subheader(f"🏫 Recommended Colleges for {course}")
                    for col in recommended_colleges:
                        st.write("-", col)
                else:
                    st.info(f"No colleges found offering {course} in the dataset.")

    # ---------------- Roadmap ----------------
    if menu == "Roadmap":
        st.header("🛤 Career Roadmap")
        career = st.text_input("Enter a career to view roadmap", "B.Arch.")
        if st.button("Show Roadmap"):
            if career in DATA["careers"]:
                steps = DATA["careers"][career]
            else:
                steps = [
                    f"Step 1: Explore basics of {career}",
                    f"Step 2: Take relevant courses or certifications in {career}",
                    f"Step 3: Gain practical experience through projects or internships",
                    f"Step 4: Build portfolio and network",
                    f"Step 5: Apply for professional opportunities in {career}"
                ]
            st.subheader(f"🛤 Roadmap for {career}")
            for step in steps:
                st.write("-", step)

            # Colleges
            recommended_colleges = []
            for c in DATA["colleges"]:
                if any(career.lower() in cr.lower() for cr in c["courses"]):
                    recommended_colleges.append(c["name"])

            if recommended_colleges:
                st.subheader(f"🏫 Recommended Colleges for {career}")
                for col in recommended_colleges:
                    st.write("-", col)
            else:
                st.info(f"No colleges found offering {career} in the dataset.")

    # ---------------- About ----------------
    if menu == "About":
        st.header("ℹ️ About")
        st.write("Prototype for Personalized Career & Education Advisor.")
