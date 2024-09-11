import strawberry
from auth.authentication import register_user, login_user, logout_user
from fastapi import Request
from strawberry.types import Info
from auth.jwt_handler import create_access_token
from config import get_db
from models import User as UserModel, Message as MessageModel
from datetime import datetime
from uuid import uuid4
# Definiere das Rückgabe-Objekt für den Login
@strawberry.type
class LoginResponse:
    token: str
@strawberry.type
class SendMessageResponse:
    id: str
    content: str
    sender: str
    receiver: str
    timestamp: str
@strawberry.type
class Mutation:
    @strawberry.mutation
    def register(self, username: str, password: str, email: str, info: Info) -> str:
        request: Request = info.context['request']
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent")
        os = request.headers.get("sec-ch-ua-platform")

        return register_user(username, password, email, ip_address, user_agent, os)

    @strawberry.mutation
    def login(self, username: str, password: str, info: Info) -> LoginResponse:
        request: Request = info.context['request']
        ip_address = request.client.host

        # login_user gibt jetzt das Benutzerobjekt als Dictionary zurück
        user = login_user(username, password, ip_address)

        if not user:
            raise Exception("Falsche Anmeldedaten")

        # Erstelle den Token mit dem Benutzernamen aus dem Benutzer-Dictionary
        access_token = create_access_token(data={"sub": user["username"]})  # Korrigiert: user["username"]

        return LoginResponse(token=access_token)

    @strawberry.mutation
    def logout(self, user_id: str) -> str:
        """
        Diese Mutation loggt einen Benutzer aus und entfernt ihn aus der LoggedInUsers-Tabelle.
        """
        logout_user(user_id)
        return f"Benutzer mit ID {user_id} wurde erfolgreich ausgeloggt."

    @strawberry.mutation
    def send_message(self, sender_username: str, receiver_username: str, content: str,
                     info: Info = None) -> SendMessageResponse:
        """
        This mutation sends a message from one user to another and saves it in the database.
        """
        # Create a database session
        db = next(get_db())

        # Fetch the sender and receiver from the database
        sender = db.query(UserModel).filter(UserModel.username == sender_username).first()
        receiver = db.query(UserModel).filter(UserModel.username == receiver_username).first()

        if not sender or not receiver:
            raise Exception("Sender or receiver not found.")

        # Save the message to the database
        new_message = MessageModel(
            id=str(uuid4()),
            content=content,
            sender_id=sender.id,
            receiver_id=receiver.id,
            timestamp=datetime.now()
        )
        db.add(new_message)
        db.commit()

        # Format the response
        return SendMessageResponse(
            id=new_message.id,
            content=new_message.content,
            sender=sender.username,
            receiver=receiver.username,
            timestamp=new_message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        )
