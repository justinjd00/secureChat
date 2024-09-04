from .user_management import load_users, save_users
import uuid
from datetime import datetime

# benutzer registrieren
def register_user(username: str, password: str, email: str, ip_address: str, user_agent: str, os: str):
    users_data = load_users()

    # check duplicates
    if any(user["username"] == username for user in users_data["users"]):
        raise ValueError("Benutzername bereits vergeben.")
    if any(user["email"] == email for user in users_data["users"]):
        raise ValueError("E-Mail bereits vergeben.")

    user_id = str(uuid.uuid4())
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # user data
    new_user = {
        "id": user_id,
        "username": username,
        "password": password,  
        "email": email,
        "registration_date": registration_date,
        "last_login": None,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "os": os
    }

    users_data["users"].append(new_user)
    save_users(users_data)

    return f"Benutzer {username} erfolgreich registriert."
def login_user(username: str, password: str, ip_address: str):
    users_data = load_users()

    user = next((user for user in users_data["users"] if user["username"] == username), None)
    if not user or user["password"] != password:  
        raise ValueError("Ungültige Anmeldedaten.")

    user["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user["ip_address"] = ip_address

    save_users(users_data)

    return f"Benutzer {username} erfolgreich angemeldet."
