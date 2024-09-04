import strawberry
from fastapi import HTTPException
from tokens.jwt_handler import verify_access_token

@strawberry.type
class Query:
    @strawberry.field
    def protected_data(self, token: str) -> str:
        username = verify_access_token(token)
        if username is None:
            raise HTTPException(status_code=403, detail="Ungültiges Token")
        return f"Willkommen {username}, hier sind deine geschützten Daten!"
