import streamlit as st
import json
import os
from datetime import date
import modules.auth as auth
import modules.recommender as recommender
import modules.roadmap as roadmap

# 🔹 Tailwind CSS
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
    st.title("Career Compass")
    st.subheader("Login / Sign Up")

    tab = st.tabs(["Login", "Sign Up"])
    with tab[0]:
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

    with tab[1]:
        signup_name = st.text_input("Full Name", key="signup_name")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Sign Up"):
            success, message = auth.signup(signup_name, signup_email, signup_password)
            if success:
                st.success(message)
            else:
                st.error(message)

else:
    user = st.session_state.user

    # ---------------- Sidebar Navigation ----------------
    menu = st.sidebar.radio("📍 Navigate", ["Home","Profile","Explore","Quiz","About Us","Notifications","Logout"])

    # ---------------- Logout ----------------
    if menu=="Logout":
        st.session_state.user = None
        st.experimental_rerun()

    # ---------------- Home ----------------
    if menu=="Home":
        st.header(f"👋 Welcome, {user['name']}")
        st.markdown(f"💬 {daily_affirmation()}")
        st.markdown("---")
        st.subheader("💡 Tip of the Day")
        tips = [
            "Explore new skills related to your interests.",
            "Research colleges and courses before applying.",
            "Set small achievable goals daily.",
            "Network with professionals in your field.",
        ]
        st.info(tips[date.today().toordinal() % len(tips)])

    # ---------------- Profile ----------------
    if menu=="Profile":
        st.header("👤 Your Profile")
        st.write(f"**Name:** {user['name']}")
        st.write(f"**Email:** {user['email']}")

    # ---------------- Explore ----------------
    if menu=="Explore":
        st.header("🔎 Explore Colleges & Careers")
        search_text = st.text_input("Search term")
        filter_type = st.selectbox("Search by", ["Select","College","Course","Career"])

        if st.button("Search"):
            if filter_type=="College":
                names = [c["name"] for c in DATA["colleges"] if search_text.lower() in c["name"].lower()]
                if names:
                    st.write("🏫 Colleges found:")
                    for n in names:
                        st.write(f"- {n}")
                else:
                    st.warning("No colleges found")
            elif filter_type=="Course":
                found = []
                for c in DATA["colleges"]:
                    for cr in c["courses"]:
                        if search_text.lower() in cr.lower():
                            found.append(f"{cr} ({c['name']})")
                if found:
                    st.write("📚 Courses found:")
                    for f in found:
                        st.write(f"- {f}")
                else:
                    st.warning("No courses found")
            elif filter_type=="Career":
                if search_text in DATA["careers"]:
                    st.write(f"Career roadmap for {search_text}:")
                    roadmap.show_roadmap(search_text)
                else:
                    st.warning("Career not found")

    # ---------------- Quiz ----------------
    if menu=="Quiz":
        st.header("🎯 Career Quiz")

        if "quiz_step" not in st.session_state:
            st.session_state.quiz_step = "Q1"
            st.session_state.answers = []
            st.session_state.quiz_result = None
            st.session_state.recommended_colleges = []

        # Define quiz tree
        quiz_tree = {
            "Q1": {"q":"What are your main interests?",
                   "options":["Engineering","Medical","Commerce","Arts","Architecture","Other"]},
            "Q2-Engineering": {"q":"Which branch of Engineering interests you?",
                                "options":["CSE","ECE","Mechanical","Civil","Other"]},
            "Q2-Medical": {"q":"Which field in Medical interests you?",
                            "options":["MBBS","BDS","BAMS","B.Sc. Nursing","Other"]},
            "Q2-Commerce": {"q":"Which course in Commerce are you interested in?",
                             "options":["BBA","B.Com","CA/CPA"]},
            "Q2-Arts": {"q":"Which course in Arts are you interested in?",
                        "options":["BA","BFA","B.Sc."]},
            "Q2-Architecture": {"q":"Which Architecture course are you interested in?",
                                 "options":["B.Arch."]}
        }

        node = quiz_tree[st.session_state.quiz_step]
        choice = st.radio(node["q"], node["options"], key=st.session_state.quiz_step)

        if st.button("Next Question"):
            st.session_state.answers.append(choice)

            # Determine next question or final recommendation
            next_key = f"Q2-{choice}" if st.session_state.quiz_step=="Q1" else None
            if next_key and next_key in quiz_tree:
                st.session_state.quiz_step = next_key
            else:
                st.session_state.quiz_result = choice
                # Get recommended colleges from dataset
                recommended = recommender.colleges_for_course(choice, DATA["colleges"])
                st.session_state.recommended_colleges = recommended
                st.success(f"✅ Based on your answers, we suggest: **{choice}**")
                if recommended:
                    st.write("🏫 Recommended Colleges:")
                    for c in recommended:
                        st.write(f"- {c}")
                # Show roadmap
                st.markdown(f"🛤 Roadmap for {choice}")
                roadmap.show_roadmap(choice)

    # ---------------- About Us ----------------
    if menu=="About Us":
        st.header("ℹ️ About Us")
        st.write("Prototype: Personalized Career & Education Advisor App.")

    # ---------------- Notifications ----------------
    if menu=="Notifications":
        st.header("📢 Notifications")
        for n in DATA["notifications"]:
            st.info(n["msg"])
