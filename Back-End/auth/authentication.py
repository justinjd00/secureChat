from passlib.context import CryptContext
import psycopg2
from .user_management import load_users, save_users
import uuid
from datetime import datetime
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_ip(ip_address: str) -> str:
    return hashlib.sha256(ip_address.encode()).hexdigest()

# Funktion zum Benutzer-Login, die ein Benutzerobjekt als Dictionary zurückgibt
def login_user(username: str, password: str, ip_address: str):
    users_data = load_users()

    user = next((user for user in users_data["users"] if user["username"] == username), None)
    if not user:
        raise ValueError("Ungültige Anmeldedaten.")

    if not verify_password(password, user["password"]):
        raise ValueError("Ungültige Anmeldedaten.")

    user["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user["ip_address"] = hash_ip(ip_address)

    save_users(users_data)

    # Benutzer als online tracken
    track_logged_in_user(user)

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "last_login": user["last_login"]
    }
# Funktion, um Benutzer zu registrieren und sowohl in der JSON-Datei als auch in der DB zu speichern
def register_user(username: str, password: str, email: str, ip_address: str, user_agent: str, os: str):
    # PostgreSQL-Verbindung herstellen
    conn = psycopg2.connect('postgres://avnadmin:AVNS_wwY6Tw8KwsNrL5cWf5Z@pg-3ec1ff15-justinjd00-e424.e.aivencloud.com:16693/SecureChat?sslmode=require')
    cur = conn.cursor()

    users_data = load_users()

    # Prüfen, ob Benutzer bereits existiert
    if any(user["username"] == username for user in users_data["users"]):
        raise ValueError("Benutzername bereits vergeben.")
    if any(user["email"] == email for user in users_data["users"]):
        raise ValueError("E-Mail bereits vergeben.")

    user_id = str(uuid.uuid4())
    registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Passwort und IP-Adresse hashen
    hashed_password = hash_password(password)
    hashed_ip = hash_ip(ip_address)

    # Benutzerobjekt erstellen
    new_user = {
        "id": user_id,
        "username": username,
        "password": hashed_password,
        "email": email,
        "registration_date": registration_date,
        "last_login": None,
        "ip_address": hashed_ip,
        "user_agent": user_agent,
        "os": os
    }

    # Benutzer in JSON-Datei speichern
    users_data["users"].append(new_user)
    save_users(users_data)

    # SQL-Abfrage, um Benutzer in die DB einzufügen
    insert_query = '''
    INSERT INTO "Users" (id, username, password, email, registration_date, last_login, ip_address, user_agent, os)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO NOTHING;
    '''
    cur.execute(insert_query, (
        new_user['id'],
        new_user['username'],
        new_user['password'],
        new_user['email'],
        new_user['registration_date'],
        new_user['last_login'],
        new_user['ip_address'],
        new_user['user_agent'],
        new_user['os']
    ))

    # Änderungen in der DB speichern und Verbindung schließen
    conn.commit()
    cur.close()
    conn.close()

    return f"Benutzer {username} erfolgreich registriert."


def track_logged_in_user(user):
    # Verbindung zur Datenbank herstellen
    conn = psycopg2.connect('postgres://avnadmin:AVNS_wwY6Tw8KwsNrL5cWf5Z@pg-3ec1ff15-justinjd00-e424.e.aivencloud.com:16693/SecureChat?sslmode=require')
    cur = conn.cursor()

    # Benutzer in die LoggedInUsers-Tabelle einfügen
    insert_query = '''
    INSERT INTO "loggedinusers" (id, username)
    VALUES (%s, %s)
    ON CONFLICT (id) DO NOTHING;
    '''

    cur.execute(insert_query, (user['id'], user['username']))

    conn.commit()
    cur.close()
    conn.close()
    print(f"[INFO] Benutzer {user['username']} erfolgreich in LoggedInUsers eingefügt.")


def logout_user(user_id: str):
    # Verbindung zur Datenbank herstellen
    conn = psycopg2.connect('postgres://avnadmin:AVNS_wwY6Tw8KwsNrL5cWf5Z@pg-3ec1ff15-justinjd00-e424.e.aivencloud.com:16693/SecureChat?sslmode=require')
    cur = conn.cursor()

    # Benutzer aus der LoggedInUsers-Tabelle entfernen
    delete_query = '''
    DELETE FROM loggedinusers WHERE id = %s;
    '''

    cur.execute(delete_query, (user_id,))
    conn.commit()
    cur.close()
    conn.close()

    print(f"[INFO] Benutzer mit ID {user_id} erfolgreich aus LoggedInUsers entfernt.")