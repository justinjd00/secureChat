﻿import strawberry
from fastapi import Request
from auth.authentication import register_user, login_user


@strawberry.type
class Mutation:
    @strawberry.mutation
    def register(self, username: str, password: str, email: str, request: Request) -> str:
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent")
        os = request.headers.get("sec-ch-ua-platform")
        return register_user(username, password, email, ip_address, user_agent, os)

    @strawberry.mutation
    def login(self, username: str, password: str, request: Request) -> str:
        ip_address = request.client.host
        return login_user(username, password, ip_address)