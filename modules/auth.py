import json
import os

USER_FILE = os.path.join("data", "users.json")

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def signup(name, email, password):
    users = load_users()
    # Check if email exists
    if any(u["email"] == email for u in users):
        return False, "Email already registered"
    # Add new user
    users.append({"name": name, "email": email, "password": password})
    save_users(users)
    return True, "Signup successful! Please login."

def login(email, password):
    users = load_users()
    for u in users:
        if u["email"] == email and u["password"] == password:
            return u
    return None
