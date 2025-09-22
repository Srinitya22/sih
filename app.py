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
DATA_PATH = os.path.join("data","career_tree.json")
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

    # 🔹 Anime-style Visme form
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

    st.info("➡️ For hackathon demo, skip Visme login & press 'Demo Login' below.")
    if st.button("Demo Login"):
        st.session_state.user = {"name":"HackathonUser","email":"demo@sih.com"}
        st.success("Logged in as Demo User ✅")
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
    menu = st.sidebar.radio("📍 Navigate", ["Home","Quiz","Roadmap","About","Logout"])

    if menu=="Logout":
        st.session_state.user = None
        st.experimental_rerun()

    # ---------------- Home ----------------
    if menu=="Home":
        st.header("🏠 Home")

        # Search Section
        st.markdown("""
        <div class="bg-white p-4 rounded-xl shadow-md mb-4">
          <h3 class="text-xl font-bold">🔎 Search</h3>
        </div>
        """, unsafe_allow_html=True)

        search_text = st.text_input("Free Search (College / Course / Career)")
        filter_type = st.selectbox("Filter by", ["Select","College","Course","Career"])

        if st.button("Search"):
            if filter_type=="College":
                names = [c["name"] for c in DATA["colleges"]]
                st.write("Colleges:", names)
            elif filter_type=="Course":
                st.write("Courses across colleges:")
                for c in DATA["colleges"]:
                    for cr in c["courses"]:
                        if search_text.lower() in cr.lower():
                            st.write(f"- {cr} ({c['name']})")
            elif filter_type=="Career":
                if search_text in DATA["careers"]:
                    roadmap.show_roadmap(search_text)
                else:
                    st.error("Career not found in demo dataset")

        st.markdown("---")
        st.subheader("📢 Notifications")
        for n in DATA["notifications"]:
            st.info(n["msg"])

    # ---------------- Quiz ----------------
    if menu=="Quiz":
        st.header("🎯 Career Quiz")

        # Initialize session state
        if "quiz_step" not in st.session_state:
            st.session_state.quiz_step = "interest"
            st.session_state.answers = []
            st.session_state.selected_interest = None
            st.session_state.selected_course = None
            st.session_state.colleges = []

        # Step 1: Ask main interests
        if st.session_state.quiz_step == "interest":
            interests = ["Engineering","Medical","Commerce","Arts","Architecture","Other"]
            selected = st.radio("What are your main interests?", interests, key="interest")
            if st.button("Next"):
                st.session_state.selected_interest = selected
                st.session_state.quiz_step = "course"

        # Step 2: List courses based on interest
        elif st.session_state.quiz_step == "course":
            # Gather all courses from DATA dynamically
            course_set = set()
            for college in DATA["colleges"]:
                for c in college["courses"]:
                    course_lower = c.lower()
                    interest_lower = st.session_state.selected_interest.lower()
                    # Simple matching logic
                    if interest_lower in course_lower or \
                       (interest_lower=="engineering" and "be" in course_lower) or \
                       (interest_lower=="medical" and any(x in course_lower for x in ["mbbs","nursing","bams","bds","paramedical"])):
                        course_set.add(c)
            course_list = sorted(course_set)

            if not course_list:
                st.warning("No courses found for this interest. Try a different interest.")
                if st.button("Back"):
                    st.session_state.quiz_step = "interest"
            else:
                selected_course = st.radio(f"Which course in {st.session_state.selected_interest} are you interested in?", course_list, key="course")
                if st.button("Next"):
                    st.session_state.selected_course = selected_course
                    # Find matching colleges
                    matching_colleges = []
                    for college in DATA["colleges"]:
                        if any(selected_course.lower() in cr.lower() for cr in college["courses"]):
                            matching_colleges.append(college["name"])
                    st.session_state.colleges = matching_colleges
                    st.session_state.quiz_step = "result"

        # Step 3: Show personalized result
        elif st.session_state.quiz_step == "result":
            st.success(f"✅ Based on your interest in **{st.session_state.selected_course}**, here are matching colleges:")
            for col in st.session_state.colleges:
                st.write(f"- {col}")

            if st.button("Restart Quiz"):
                st.session_state.quiz_step = "interest"
                st.session_state.answers = []
                st.session_state.selected_interest = None
                st.session_state.selected_course = None
                st.session_state.colleges = []

    # ---------------- Roadmap ----------------
    if menu=="Roadmap":
        st.header("🛤 Career Roadmap")
        career = st.text_input("Enter a career to view roadmap", "Culinary")
        if st.button("Show Roadmap"):
            roadmap.show_roadmap(career)

    # ---------------- About ----------------
    if menu=="About":
        st.header("ℹ️ About")
        st.write("Prototype for SIH Hackathon — Personalized Career & Education Advisor.")
