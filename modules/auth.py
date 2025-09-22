# modules/auth.py
import json
import os

DATA_FILE = os.path.join("data", "users.json")

# Load users
def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Save users
def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

# Signup function
def signup(name, email, password):
    users = load_users()
    if email in users:
        return False, "Email already exists."
    users[email] = {"name": name, "email": email, "password": password}
    save_users(users)
    return True, "Signup successful! You can now log in."

# Login function
def login(email, password):
    users = load_users()
    if email in users and users[email]["password"] == password:
        return users[email]
    return None
