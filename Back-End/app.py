from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from strawberry.fastapi import GraphQLRouter
from schema import schema
from auth.authentication import register_user, pwd_context, verify_password, \
    login_user  # Make sure these imports are correct
import sys
import os
from sqlalchemy.orm import Session
from datetime import datetime
from models import User, Contact
from config import get_db
import uuid

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


# Pydantic model for validating login requests
class UserLogin(BaseModel):
    username: str
    password: str


# Passwort-Hashing-Funktion
def hash_password(password: str):
    return pwd_context.hash(password)


# Signup-Route
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


# Login-Route
@app.post("/signin")
def signin(user_data: UserLogin, db: Session = Depends(get_db)):
    # Benutzer in der Datenbank finden
    user_in_db = db.query(User).filter(User.username == user_data.username).first()

    if not user_in_db or not verify_password(user_data.password, user_in_db.password):
        raise HTTPException(status_code=400, detail="Falsche Anmeldedaten")

    return {"message": "Login erfolgreich", "user_id": user_in_db.id}


@app.get("/check_user/{username}")
def check_user(username: str, db: Session = Depends(get_db)):
    # Query the database for a user with the given username
    user = db.query(User).filter(User.username == username).first()

    if user:
        return {"message": f"User {username} exists."}
    else:
        raise HTTPException(status_code=404, detail=f"User {username} not found.")


graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.post("/add_contact")
def add_contact(user_id: uuid.UUID, contact_username: str, db: Session = Depends(get_db)):
    # Find the contact in the Users table
    contact = db.query(User).filter(User.username == contact_username).first()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Check if contact already exists for this user
    existing_contact = db.query(Contact).filter_by(user_id=user_id, contact_id=contact.id).first()
    if existing_contact:
        raise HTTPException(status_code=400, detail="Contact already added")

    # Add the new contact
    new_contact = Contact(user_id=user_id, contact_id=contact.id)
    db.add(new_contact)
    db.commit()

    return {"message": f"Contact {contact_username} added successfully"}


@app.get("/get_contacts/{user_id}")
def get_contacts(user_id: uuid.UUID, db: Session = Depends(get_db)):
    # Holen Sie alle Kontakte für den Benutzer aus der Datenbank
    contacts = db.query(Contact).filter_by(user_id=user_id).all()

    if not contacts:
        return {"message": "No contacts found"}

    contact_list = []
    for contact in contacts:
        contact_user = db.query(User).filter_by(id=contact.contact_id).first()
        contact_list.append({"username": contact_user.username})

    return contact_list
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8083)
