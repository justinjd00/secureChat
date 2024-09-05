import strawberry
from typing import List
from datetime import datetime
import psycopg2
# Dummy-Daten 
users_data = [
    {"id": "1", "username": "Alice", "email": "alice@example.com", "last_login": "2024-09-04 14:23"},
    {"id": "2", "username": "Bob", "email": "bob@example.com", "last_login": "2024-09-03 12:10"}
]

messages_data = [
    {"id": "1", "content": "Hello Bob!", "sender": "Alice", "receiver": "Bob", "timestamp": "2024-09-04 14:25"},
    {"id": "2", "content": "Hi Alice!", "sender": "Bob", "receiver": "Alice", "timestamp": "2024-09-04 14:26"}
]

# Benutzer-Typ
@strawberry.type
class User:
    id: str
    username: str
    email: str
#   last_login: str

# Nachrichten-Typ
@strawberry.type
class Message:
    id: str
    content: str
    sender: str
    receiver: str
    timestamp: str

@strawberry.type
class LoggedInUser:
    id: str
    username: str
    login_time: str

# Query-Klasse
@strawberry.type
class Query:

    @strawberry.field
    def get_user_by_username(self, username: str) -> User:
        user = next((user for user in users_data if user["username"] == username), None)
        if not user:
            raise ValueError(f"Benutzer mit dem Benutzernamen {username} nicht gefunden")
        return User(**user)

    @strawberry.field
    def all_users(self) -> List[User]:
        # Verbindung zur Datenbank herstellen
        conn = psycopg2.connect('postgres://avnadmin:AVNS_wwY6Tw8KwsNrL5cWf5Z@pg-3ec1ff15-justinjd00-e424.e.aivencloud.com:16693/SecureChat?sslmode=require')
        cur = conn.cursor()

        # SQL-Abfrage, um alle Benutzer aus der Tabelle 'Users' zu holen
        cur.execute('SELECT id, username, email FROM "Users"')
        rows = cur.fetchall()

        # Liste von User-Objekten erstellen
        users = [User(id=row[0], username=row[1], email=row[2]) for row in rows]

        # Verbindung schließen
        cur.close()
        conn.close()

        return users
    @strawberry.field
    def messages_between(self, user1: str, user2: str) -> List[Message]:
        messages = [
            Message(**message) for message in messages_data
            if (message["sender"] == user1 and message["receiver"] == user2) or
               (message["sender"] == user2 and message["receiver"] == user1)
        ]
        return messages

    @strawberry.field
    def last_login(self, username: str) -> str:
        user = next((user for user in users_data if user["username"] == username), None)
        if not user:
            raise ValueError(f"Benutzer {username} nicht gefunden")
        return user["last_login"]
    
    @strawberry.field
    def get_logged_in_users(self) -> List[LoggedInUser]:
        # Verbindung zur Datenbank herstellen
        conn = psycopg2.connect('postgres://avnadmin:AVNS_wwY6Tw8KwsNrL5cWf5Z@pg-3ec1ff15-justinjd00-e424.e.aivencloud.com:16693/SecureChat?sslmode=require')
        cur = conn.cursor()
    
        # Alle eingeloggten Benutzer abfragen
        cur.execute('SELECT id, username, login_time FROM "LoggedInUsers"')
        rows = cur.fetchall()
    
        cur.close()
        conn.close()
    
        return [LoggedInUser(id=row[0], username=row[1], login_time=row[2].strftime("%Y-%m-%d %H:%M:%S")) for row in rows]