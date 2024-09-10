import strawberry
from auth.authentication import register_user, login_user, logout_user
from fastapi import Request
from strawberry.types import Info
from auth.jwt_handler import create_access_token
from config import get_db
from models import User as UserModel, Group as GroupModel, GroupMessage as GroupMessageModel
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
class SendGroupMessageResponse:
    id: str
    content: str
    sender: str
    group: str
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

        user = login_user(username, password, ip_address)

        if not user:
            raise Exception("Falsche Anmeldedaten")

        access_token = create_access_token(data={"sub": user["username"]})

        return LoginResponse(token=access_token)

    @strawberry.mutation
    def logout(self, user_id: str) -> str:
        logout_user(user_id)
        return f"Benutzer mit ID {user_id} wurde erfolgreich ausgeloggt."

    @strawberry.mutation
    def send_message(self, sender_username: str, receiver_username: str, content: str, info: Info) -> SendMessageResponse:
        request: Request = info.context['request']
        db = next(get_db())

        sender = db.query(UserModel).filter(UserModel.username == sender_username).first()
        receiver = db.query(UserModel).filter(UserModel.username == receiver_username).first()

        if not sender or not receiver:
            raise Exception("Sender oder Empfänger nicht gefunden.")

        new_message = MessageModel(
            id=str(uuid4()),
            content=content,
            sender_id=sender.id,
            receiver_id=receiver.id,
            timestamp=datetime.now()
        )
        db.add(new_message)
        db.commit()

        return SendMessageResponse(
            id=new_message.id,
            content=new_message.content,
            sender=sender.username,
            receiver=receiver.username,
            timestamp=new_message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        )

    @strawberry.mutation
    def send_group_message(self, sender_username: str, group_name: str, content: str, info: Info) -> SendGroupMessageResponse:
        """
        Diese Mutation sendet eine Nachricht an eine Gruppe und speichert sie in der Datenbank.
        """
        request: Request = info.context['request']
        db = next(get_db())

        # Holen der Sender-ID und Gruppen-ID
        sender = db.query(UserModel).filter(UserModel.username == sender_username).first()
        group = db.query(GroupModel).filter(GroupModel.name == group_name).first()

        if not sender or not group:
            raise Exception("Sender oder Gruppe nicht gefunden.")

        # Nachricht speichern
        new_group_message = GroupMessageModel(
            id=str(uuid4()),
            content=content,
            sender_id=sender.id,
            group_id=group.id,
            timestamp=datetime.now()
        )
        db.add(new_group_message)
        db.commit()

        return SendGroupMessageResponse(
            id=new_group_message.id,
            content=new_group_message.content,
            sender=sender.username,
            group=group.name,
            timestamp=new_group_message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        )
