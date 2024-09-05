from passlib.context import CryptContext
from .user_management import load_users, save_users
import uuid
from datetime import datetime
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    hashed = pwd_context.hash(password)
    print(f"[INFO] Passwort gehasht: {hashed}")
    return hashed

def verify_password(plain_password: str, hashed_password: str) -> bool:
    result = pwd_context.verify(plain_password, hashed_password)
    print(f"[INFO] Passwortüberprüfung erfolgreich: {result}")
    return result

def hash_ip(ip_address: str) -> str:
    hashed_ip = hashlib.sha256(ip_address.encode()).hexdigest()
    print(f"[INFO] IP-Adresse gehasht: {hashed_ip}")
    return hashed_ip

def register_user(username: str, password: str, email: str, ip_address: str, user_agent: str, os: str):
    print(f"[INFO] Registrierungsversuch für Benutzername: {username}, E-Mail: {email}")

    users_data = load_users()
    print(f"[INFO] Benutzerliste geladen. Anzahl der Benutzer: {len(users_data['users'])}")

    if any(user["username"] == username for user in users_data["users"]):
        print(f"[ERROR] Benutzername bereits vergeben: {username}")
        raise ValueError("Benutzername bereits vergeben.")
    if any(user["email"] == email for user in users_data["users"]):
        print(f"[ERROR] E-Mail bereits vergeben: {email}")
        raise ValueError("E-Mail bereits vergeben.")

    user_id = str(uuid.uuid4())
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    hashed_password = hash_password(password)
    hashed_ip_address = hash_ip(ip_address)

    new_user = {
        "id": user_id,
        "username": username,
        "password": hashed_password,
        "email": email,
        "registration_date": registration_date,
        "last_login": None,
        "ip_address": hashed_ip_address,
        "user_agent": user_agent,
        "os": os
    }

    users_data["users"].append(new_user)
    save_users(users_data)
    print(f"[INFO] Benutzer {username} erfolgreich registriert und gespeichert.")

    return f"Benutzer {username} erfolgreich registriert."

def login_user(username: str, password: str, ip_address: str):
    print(f"[INFO] Anmeldeversuch für Benutzername: {username}")

    users_data = load_users()
    print(f"[INFO] Benutzerliste geladen. Anzahl der Benutzer: {len(users_data['users'])}")

    user = next((user for user in users_data["users"] if user["username"] == username), None)
    if not user:
        print(f"[ERROR] Benutzername nicht gefunden: {username}")
        raise ValueError("Ungültige Anmeldedaten.")

    if not verify_password(password, user["password"]):
        print(f"[ERROR] Ungültiges Passwort für Benutzername: {username}")
        raise ValueError("Ungültige Anmeldedaten.")

    user["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user["ip_address"] = hash_ip(ip_address)

    save_users(users_data)
    print(f"[INFO] Benutzerdaten für {username} erfolgreich gespeichert.")

    return f"Benutzer {username} erfolgreich angemeldet."
