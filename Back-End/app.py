from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from strawberry.fastapi import GraphQLRouter
from schema import schema
from auth.authentication import register_user, pwd_context, verify_password, login_user
import sys
import os
from sqlalchemy.orm import Session
from datetime import datetime
from models import User, Contact, Message
from config import get_db
import uuid

app = FastAPI()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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


# Password hashing function
def hash_password(password: str):
    return pwd_context.hash(password)


# Signup Route
@app.post("/signup")
def signup(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    # Check if the user already exists
    user_in_db = db.query(User).filter(User.email == user_data.email).first()
    if user_in_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Get IP and User-Agent info from the request
    ip_address = request.client.host
    user_agent = request.headers.get("User-Agent")
    os = request.headers.get("sec-ch-ua-platform")

    # Create a new user entry
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        ip_address=ip_address,
        user_agent=user_agent,
        os=os,
        registration_date=datetime.utcnow()
    )

    # Add user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user_id": new_user.id}


# Login Route
@app.post("/signin")
def signin(user_data: UserLogin, db: Session = Depends(get_db)):
    # Find the user in the database
    user_in_db = db.query(User).filter(User.username == user_data.username).first()

    if not user_in_db or not verify_password(user_data.password, user_in_db.password):
        raise HTTPException(status_code=400, detail="Invalid login credentials")

    return {"message": "Login successful", "user_id": user_in_db.id}


# Check if a user exists by username
@app.get("/check_user/{username}")
def check_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user:
        return {"message": f"User {username} exists."}
    else:
        raise HTTPException(status_code=404, detail=f"User {username} not found.")


# Pydantic model for adding a contact
class AddContactRequest(BaseModel):
    user_id: uuid.UUID
    contact_username: str


# Add contact route - Ensure proper validation for user_id and contact_username
@app.post("/add_contact")
def add_contact(request_data: AddContactRequest, db: Session = Depends(get_db)):
    # Check if user_id and contact_username are valid
    if not request_data.user_id or not request_data.contact_username:
        raise HTTPException(status_code=422, detail="User ID and contact username are required")

    # Find the contact in the Users table
    contact = db.query(User).filter(User.username == request_data.contact_username).first()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Check if contact already exists for this user
    existing_contact = db.query(Contact).filter_by(user_id=request_data.user_id, contact_id=contact.id).first()
    if existing_contact:
        raise HTTPException(status_code=400, detail="Contact already added")

    # Add the new contact
    new_contact = Contact(user_id=request_data.user_id, contact_id=contact.id, created_at=datetime.utcnow())
    db.add(new_contact)
    db.commit()

    return {"message": f"Contact {request_data.contact_username} added successfully"}


# Get contacts route - Ensure user_id is valid
@app.get("/get_contacts/{user_id}")
def get_contacts(user_id: uuid.UUID, db: Session = Depends(get_db)):
    if not user_id:
        raise HTTPException(status_code=422, detail="User ID is required")

    # Fetch contacts for the given user_id
    contacts = db.query(Contact).filter_by(user_id=user_id).all()

    if not contacts:
        return {"message": "No contacts found"}

    contact_list = []
    for contact in contacts:
        contact_user = db.query(User).filter_by(id=contact.contact_id).first()
        contact_list.append({"username": contact_user.username})

    return contact_list


# GraphQL route
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


# Pydantic model for sending a message
class SendMessageRequest(BaseModel):
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    content: str

# Route to send a message
@app.post("/send_message")
def send_message(request_data: SendMessageRequest, db: Session = Depends(get_db)):
    # Ensure both sender and receiver exist
    sender = db.query(User).filter(User.id == request_data.sender_id).first()
    receiver = db.query(User).filter(User.id == request_data.receiver_id).first()

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="Sender or receiver not found")

    # Save the message to the database
    new_message = Message(
        sender_id=request_data.sender_id,
        receiver_id=request_data.receiver_id,
        content=request_data.content,
        timestamp=datetime.utcnow()
    )
    db.add(new_message)
    db.commit()

    return {"message": "Message sent successfully"}


@app.get("/get_messages/{user_id}/{contact_id}")
def get_messages(user_id: uuid.UUID, contact_id: uuid.UUID, db: Session = Depends(get_db)):
    # Fetch all messages between the user and the contact
    messages = db.query(Message).filter(
        (Message.sender_id == user_id) & (Message.receiver_id == contact_id) |
        (Message.sender_id == contact_id) & (Message.receiver_id == user_id)
    ).order_by(Message.timestamp).all()

    if not messages:
        return {"messages": []}  # Return an empty array if no messages are found

    # Format the messages for the frontend
    formatted_messages = [
        {"sender": message.sender.username, "content": message.content, "timestamp": message.timestamp} for message in
        messages]

    return {"messages": formatted_messages}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8088)
