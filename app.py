import streamlit as st
import requests
import feedparser
import json
import os
from datetime import date
import modules.auth as auth
import modules.recommender as recommender
import modules.roadmap as roadmap

# Load career dataset
DATA_PATH = os.path.join("data","career_tree.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)

# ----------------- Daily Affirmation -----------------
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

# ----------------- Fetch Dynamic Notifications -----------------
def get_notifications():
    notifications = []

    # 1️⃣ Live news from Google News (Education)
    try:
        RSS_URL = "https://news.google.com/rss/search?q=education&hl=en-IN&gl=IN&ceid=IN:en"
        feed = feedparser.parse(RSS_URL)
        for entry in feed.entries[:5]:
            notifications.append(f"📰 {entry.title} - <a href='{entry.link}' target='_blank'>Read</a>")
    except Exception as e:
        notifications.append("⚠️ Failed to fetch live news.")

    # 2️⃣ Career-specific notifications from dataset
    for c in DATA["colleges"][:5]:  # first 5 colleges for demo
        notifications.append(f"🏫 Admissions open for {c['name']}")

    return notifications

# ----------------- Streamlit App -----------------
if "user" not in st.session_state:
    st.session_state.user = None

# Login Section
if not st.session_state.user:
    st.title("Career Compass - Login")
    login_email = st.text_input("Email")
    login_password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = auth.login(login_email, login_password)
        if user:
            st.session_state.user = user
            st.success(f"Welcome, {user['name']}!")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

else:
    user = st.session_state.user

    # ----------------- Home Page -----------------
    st.header(f"👋 Welcome, {user['name']}")
    st.write(daily_affirmation())
    st.markdown("---")

    # Extra Home Content
    st.subheader("✨ Featured Tips")
    st.markdown(
        "- Set daily goals for your career path.\n"
        "- Explore top colleges and courses.\n"
        "- Keep track of upcoming admission deadlines.\n"
        "- Stay updated with education news."
    )
    st.markdown("---")

    # ----------------- Notifications -----------------
    st.subheader("📢 Notifications")
    notifs = get_notifications()
    for n in notifs:
        st.markdown(n, unsafe_allow_html=True)

    # ----------------- Navigation -----------------
    menu = st.sidebar.radio("Navigate", ["Home", "Profile", "Explore", "Quiz", "About Us", "Logout"])

    if menu=="Logout":
        st.session_state.user = None
        st.experimental_rerun()

    if menu=="Explore":
        st.header("🔎 Explore Colleges & Careers")
        search_term = st.text_input("Search term")
        search_by = st.selectbox("Search by", ["College", "Course", "Career"])
        if st.button("Search"):
            if search_by=="College":
                colleges = [c["name"] for c in DATA["colleges"] if search_term.lower() in c["name"].lower()]
                if colleges:
                    for clg in colleges:
                        st.markdown(f"- {clg}")
                else:
                    st.warning("No colleges found.")
            elif search_by=="Course":
                courses_found = []
                for c in DATA["colleges"]:
                    for crs in c["courses"]:
                        if search_term.lower() in crs.lower():
                            courses_found.append(f"{crs} ({c['name']})")
                if courses_found:
                    for c in courses_found:
                        st.markdown(f"- {c}")
                else:
                    st.warning("No courses found.")
            elif search_by=="Career":
                if search_term in DATA["careers"]:
                    st.info(f"Career found: {search_term}")
                else:
                    st.warning("Career not found.")

    if menu=="Quiz":
        st.header("🎯 Career Quiz")
        recommender.run_quiz(DATA)

    if menu=="Profile":
        st.header("👤 Your Profile")
        st.write(f"Name: {user['name']}")
        st.write(f"Email: {user['email']}")

    if menu=="About Us":
        st.header("ℹ️ About Us")
        st.markdown(
            "Career Compass is a personalized career and education advisor app."
            " Stay updated, find colleges, explore courses, and plan your roadmap."
        )
