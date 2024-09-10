
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from strawberry.fastapi import GraphQLRouter
from schema import schema
from auth.authentication import register_user, pwd_context  # Make sure this imports correctly
import sys
import os
from sqlalchemy.orm import Session
from config import get_db
from models import User
from datetime import datetime

app = FastAPI()



sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up CORS to allow frontend requests if they're on a different port (e.g., Vite on port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for validating signup requests
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# Passwort-Hashing-Funktion
def hash_password(password: str):
    return pwd_context.hash(password)

@app.post("/signup")
def signup(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    # Überprüfe, ob der Benutzer bereits existiert
    user_in_db = db.query(User).filter(User.email == user_data.email).first()
    if user_in_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Passwort hashen
    hashed_password = hash_password(user_data.password)

    # IP-Adresse und User-Agent aus der Anfrage holen
    ip_address = request.client.host
    user_agent = request.headers.get("User-Agent")
    os = request.headers.get("sec-ch-ua-platform")

    # Erstelle den neuen Benutzer
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,  # Gehashte Passwort speichern
        ip_address=ip_address,
        user_agent=user_agent,
        os=os,
        registration_date=datetime.utcnow()
    )

    # Füge den Benutzer zur Datenbank hinzu
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user_id": new_user.id}

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8077)


