import streamlit as st
import json
import os
from datetime import date

# ---------------- Tailwind CSS ----------------
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
    st.session_state.quiz_step = "Q1"
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = []
if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None
if "rerun_after_login" not in st.session_state:
    st.session_state.rerun_after_login = False

# ---------------- Login ----------------
if not st.session_state.user:
    st.markdown("""
    <div class="bg-gradient-to-r from-purple-500 to-indigo-600 text-white p-6 rounded-2xl shadow-lg text-center">
      <h1 class="text-4xl font-bold mb-4">Career Compass</h1>
      <p class="text-lg">Your personalized career & education advisor 🚀</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("✨ Login / Sign Up")
    email = st.text_input("Email")
    name = st.text_input("Name")
    if st.button("Login"):
        if email and name:
            st.session_state.user = {"name": name, "email": email}
            st.success(f"Logged in as {name}")
            st.session_state.rerun_after_login = True
        else:
            st.error("Please enter both name and email")

# Safe rerun after login
if st.session_state.rerun_after_login:
    st.session_state.rerun_after_login = False
    st.rerun()

# ---------------- Main App ----------------
if st.session_state.user:
    user = st.session_state.user
    st.markdown(f"""
    <div class="bg-gradient-to-r from-green-400 to-blue-500 text-white p-6 rounded-2xl shadow-lg mb-4">
      <h2 class="text-2xl font-bold">👋 Welcome, {user['name']}</h2>
      <p>{daily_affirmation()}</p>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- Sidebar Menu ----------------
    menu = st.sidebar.radio("📍 Navigate", ["Home", "Quiz", "About", "Logout"])

    if menu == "Logout":
        st.session_state.user = None
        st.rerun()

    # ---------------- Home ----------------
    if menu == "Home":
        st.header("🏠 Home")
        search_text = st.text_input("Search College / Course / Career")
        filter_type = st.selectbox("Filter by", ["Select", "College", "Course", "Career"])

        if st.button("Search"):
            if filter_type == "College":
                names = [c["name"] for c in DATA["colleges"] if search_text.lower() in c["name"].lower()]
                if names:
                    st.write("Colleges:", names)
                else:
                    st.info("No colleges found")
            elif filter_type == "Course":
                matches = []
                for c in DATA["colleges"]:
                    for cr in c["courses"]:
                        if search_text.lower() in cr.lower():
                            matches.append(f"{cr} ({c['name']})")
                if matches:
                    st.write("Courses found:")
                    for m in matches:
                        st.write("-", m)
                else:
                    st.info("No courses found")
            elif filter_type == "Career":
                course = search_text
                if course in DATA["careers"]:
                    st.write(f"Roadmap for {course}:")
                    for step in DATA["careers"][course]:
                        st.write("-", step)
                else:
                    st.info("No roadmap available")

        st.markdown("---")
        st.subheader("📢 Notifications")
        for n in DATA["notifications"]:
            st.info(n["msg"])

    # ---------------- Quiz ----------------
    if menu == "Quiz":
        st.header("🎯 Career Quiz")

        # Quiz Tree
        quiz_tree = {
            "Q1": {
                "q": "What are your main interests?",
                "options": ["Engineering", "Medical", "Commerce", "Arts", "Architecture", "Other"]
            },
            "Q2-Engineering": {
                "q": "Which branch are you interested in?",
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
            }
        }

        node = quiz_tree.get(st.session_state.quiz_step)
        if node:
            choice = st.radio(node["q"], node["options"], key=st.session_state.quiz_step)
            if st.button("Next Question"):
                st.session_state.quiz_answers.append(choice)
                next_step = f"Q2-{choice}" if st.session_state.quiz_step == "Q1" else None
                if next_step and next_step in quiz_tree:
                    st.session_state.quiz_step = next_step
                else:
                    st.session_state.quiz_result = choice
                    st.success(f"✅ Based on your answers, we suggest: **{choice}**")
        else:
            if st.session_state.quiz_result:
                st.success(f"✅ Based on your answers, we suggest: **{st.session_state.quiz_result}**")

        # ---------------- Show Roadmap + Colleges ----------------
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

                # Recommended Colleges (with fallback rules)
                recommended_colleges = []
                for c in DATA["colleges"]:
                    if any(course.lower() in cr.lower() for cr in c["courses"]):
                        recommended_colleges.append(c["name"])

                if recommended_colleges:
                    st.subheader(f"🏫 Recommended Colleges for {course}")
                    for col in recommended_colleges:
                        st.write("-", col)
                else:
                    # 🔹 Fallback logic
                    if "CA" in course or "Commerce" in course:
                        st.subheader("🏫 Recommended Colleges for Commerce-related courses")
                        for c in DATA["colleges"]:
                            if any("B.Com" in cr or "BBA" in cr for cr in c["courses"]):
                                st.write("-", c["name"])
                    elif "Engineering" in course or "Tech" in course:
                        st.subheader("🏫 Recommended Colleges for Engineering-related courses")
                        for c in DATA["colleges"]:
                            if any("B.E." in cr or "B.Tech" in cr for cr in c["courses"]):
                                st.write("-", c["name"])
                    elif "Medical" in course or "MBBS" in course or "Nursing" in course:
                        st.subheader("🏫 Recommended Colleges for Medical-related courses")
                        for c in DATA["colleges"]:
                            if any("MBBS" in cr or "Nursing" in cr for cr in c["courses"]):
                                st.write("-", c["name"])
                    else:
                        st.info(f"No colleges found offering {course} in the dataset.")

    # ---------------- About ----------------
    if menu == "About":
        st.header("ℹ️ About")
        st.write("Personalized Career & Education Advisor. Helps you discover suitable courses and provides roadmaps with recommended colleges.")
