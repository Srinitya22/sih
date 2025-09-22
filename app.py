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

# Generate roadmap dynamically
def generate_roadmap(course):
    return [
        f"Step 1: Explore basics of {course}",
        f"Step 2: Take relevant courses or certifications in {course}",
        f"Step 3: Gain practical experience through projects or internships",
        f"Step 4: Build portfolio and network",
        f"Step 5: Apply for professional opportunities in {course}"
    ]

# Get recommended colleges with name + location
def get_recommended_colleges(course):
    recommended_colleges = []
    normalized_course = course.lower().replace(".", "").strip()

    for c in DATA["colleges"]:
        for cr in c["courses"]:
            cr_norm = cr.lower().replace(".", "").strip()
            if normalized_course in cr_norm or cr_norm in normalized_course:
                if "location" in c and c["location"]:
                    recommended_colleges.append(f"{c['name']}, {c['location']}")
                else:
                    recommended_colleges.append(c["name"])
                break
    return recommended_colleges

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

    st.markdown("""
    <div class="visme_d"
         data-title="Webinar Registration Form"
         data-url="g7ddqxx0-untitled-project?fullPage=true"
         data-domain="forms"
         data-full-page="true"
         data-min-height="70vh"
         data-form-id="133190">
    </div>
    <script src="https://static-b-assets.visme.co/forms/vismeforms-embed.js"></script>
    """, unsafe_allow_html=True)

    if st.button("Demo Login"):
        st.session_state.user = {"name": "User", "email": "demo@sih.com"}
        st.success("Logged in ✅")
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
                roadmap_steps = generate_roadmap(search_text)
                st.subheader(f"🛤 Roadmap for {search_text}")
                for step in roadmap_steps:
                    st.write(step)

        st.markdown("---")
        st.subheader("📢 Notifications")
        for n in DATA["notifications"]:
            st.info(n["msg"])

    # ---------------- Quiz ----------------
    if menu == "Quiz":
        st.header("🎯 Career Quiz")

        quiz_tree = {
            "Q1": {"q": "What are your main interests?",
                   "options": ["Engineering", "Medical", "Commerce", "Arts", "Architecture"]},
            "Q2-Engineering": {"q": "Which branch of Engineering interests you?",
                               "options": ["CSE", "ECE", "Mechanical", "Civil"]},
            "Q2-Commerce": {"q": "Which course in Commerce are you interested in?",
                            "options": ["BBA", "B.Com", "CA/CPA"]},
            "Q2-Medical": {"q": "Which course in Medical are you interested in?",
                           "options": ["MBBS", "BDS", "B.Sc. Nursing"]},
            "Q2-Arts": {"q": "Which course in Arts are you interested in?",
                        "options": ["BA", "BFA", "History", "Psychology"]},
            "Q2-Architecture": {"q": "Which Architecture course are you interested in?",
                                "options": ["B.Arch."]}
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

                # Show roadmap
                roadmap_steps = generate_roadmap(choice)
                st.subheader(f"🛤 Roadmap for {choice}")
                for step in roadmap_steps:
                    st.write(step)

                # Show recommended colleges
                colleges = get_recommended_colleges(choice)
                if colleges:
                    st.subheader(f"🏫 Recommended Colleges for {choice}")
                    for col in colleges:
                        st.write(f"- {col}")
                else:
                    st.info(f"No colleges found offering {choice} in the dataset.")

        if st.session_state.quiz_result:
            if st.button("Restart Quiz"):
                st.session_state.quiz_step = "Q1"
                st.session_state.answers = []
                st.session_state.quiz_result = None
                st.rerun()

    # ---------------- Roadmap ----------------
    if menu == "Roadmap":
        st.header("🛤 Career Roadmap")
        career = st.text_input("Enter a career to view roadmap", "B.Arch.")
        if st.button("Show Roadmap"):
            roadmap_steps = generate_roadmap(career)
            st.subheader(f"🛤 Roadmap for {career}")
            for step in roadmap_steps:
                st.write(step)

            colleges = get_recommended_colleges(career)
            if colleges:
                st.subheader(f"🏫 Recommended Colleges for {career}")
                for col in colleges:
                    st.write(f"- {col}")
            else:
                st.info(f"No colleges found offering {career} in the dataset.")

    # ---------------- About ----------------
    if menu == "About":
        st.header("ℹ️ About")
        st.write("Prototype for SIH Hackathon — Personalized Career & Education Advisor.")
