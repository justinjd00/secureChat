import strawberry
from auth.authentication import register_user, login_user
from fastapi import Request
from strawberry.types import Info
from auth.jwt_handler import create_access_token

# Definiere das Rückgabe-Objekt für den Login
@strawberry.type
class LoginResponse:
    token: str

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
