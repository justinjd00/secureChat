from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from models import User, Contact, Message
from config import get_db
import uuid
import sys
import os
from auth.authentication import pwd_context, verify_password

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


# Pydantic model for signup
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


# Pydantic model for login
class UserLogin(BaseModel):
    username: str
    password: str


# Password hashing function
def hash_password(password: str):
    return pwd_context.hash(password)


# Signup route
@app.post("/signup")
def signup(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    # Check if user already exists
    user_in_db = db.query(User).filter(User.email == user_data.email).first()
    if user_in_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Collect IP and User-Agent info
    ip_address = request.client.host
    user_agent = request.headers.get("User-Agent")
    os_info = request.headers.get("sec-ch-ua-platform")

    # Create a new user entry
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        ip_address=ip_address,
        user_agent=user_agent,
        os=os_info,
        registration_date=datetime.utcnow()
    )

    # Add to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user_id": new_user.id}


# Login route
@app.post("/signin")
def signin(user_data: UserLogin, db: Session = Depends(get_db)):
    # Find user by username
    user_in_db = db.query(User).filter(User.username == user_data.username).first()

    if not user_in_db or not verify_password(user_data.password, user_in_db.password):
        raise HTTPException(status_code=400, detail="Invalid login credentials")

    return {"message": "Login successful", "user_id": user_in_db.id}


# Check if user exists
@app.get("/check_user/{username}")
def check_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user:
        return {"message": f"User {username} exists."}
    else:
        raise HTTPException(status_code=404, detail="User not found")


# Model for adding a contact
class AddContactRequest(BaseModel):
    user_id: uuid.UUID
    contact_username: str


# Add contact route
@app.post("/add_contact")
def add_contact(request_data: AddContactRequest, db: Session = Depends(get_db)):
    # Validate user_id and contact_username
    if not request_data.user_id or not request_data.contact_username:
        raise HTTPException(status_code=422, detail="User ID and contact username are required")

    # Find contact by username
    contact = db.query(User).filter(User.username == request_data.contact_username).first()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Check if contact already exists
    existing_contact = db.query(Contact).filter_by(user_id=request_data.user_id, contact_id=contact.id).first()
    if existing_contact:
        raise HTTPException(status_code=400, detail="Contact already added")

    # Add the new contact
    new_contact = Contact(user_id=request_data.user_id, contact_id=contact.id, created_at=datetime.utcnow())
    db.add(new_contact)
    db.commit()

    return {"message": "Contact added successfully"}


# Get contacts route
@app.get("/get_contacts/{user_id}")
def get_contacts(user_id: uuid.UUID, db: Session = Depends(get_db)):
    if not user_id:
        raise HTTPException(status_code=422, detail="User ID is required")

    # Fetch contacts
    contacts = db.query(Contact).filter_by(user_id=user_id).all()

    if not contacts:
        return {"message": "No contacts found"}

    contact_list = [{"username": db.query(User).filter_by(id=contact.contact_id).first().username} for contact in contacts]
    return contact_list


# Pydantic model for sending a message
class SendMessageRequest(BaseModel):
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    content: str


# Route to send message
@app.post("/send_message")
def send_message(request_data: SendMessageRequest, db: Session = Depends(get_db)):
    # Verify sender and receiver exist
    sender = db.query(User).filter(User.id == request_data.sender_id).first()
    receiver = db.query(User).filter(User.id == request_data.receiver_id).first()

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="Sender or receiver not found")

    # Save message to database
    new_message = Message(
        sender_id=request_data.sender_id,
        receiver_id=request_data.receiver_id,
        content=request_data.content,
        timestamp=datetime.utcnow()
    )
    db.add(new_message)
    db.commit()

    return {"message": "Message sent successfully"}


# Route to get messages
@app.get("/get_messages/{user_id}/{contact_id}")
def get_messages(user_id: uuid.UUID, contact_id: uuid.UUID, db: Session = Depends(get_db)):
    # Fetch all messages between the user and the contact
    messages = db.query(Message).filter(
        (Message.sender_id == user_id) & (Message.receiver_id == contact_id) |
        (Message.sender_id == contact_id) & (Message.receiver_id == user_id)
    ).order_by(Message.timestamp).all()

    if not messages:
        return {"messages": []}  # Return an empty list if no messages

    formatted_messages = [{"sender": message.sender.username, "content": message.content, "timestamp": message.timestamp}
                          for message in messages]

    return {"messages": formatted_messages}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8091)
