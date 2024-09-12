from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from models import User, Contact, Message, GroupMessage, GroupMember,Group
from config import get_db
import uuid
import sys
import os
from auth.authentication import pwd_context, verify_password
from mutations import Mutation
from fastapi.responses import JSONResponse
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
@app.options("/{path:path}")
async def preflight_handler():
    return JSONResponse({"message": "Preflight request allowed"}, headers={
        "Access-Control-Allow-Origin": "*",  # or specify the allowed origin
        "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
        "Access-Control-Allow-Headers": "Authorization, Content-Type",
    })

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

@app.get("/get_contacts/{user_id}")
def get_contacts(user_id: uuid.UUID, db: Session = Depends(get_db)):
    # Fetch contacts for the given user_id
    contacts = db.query(Contact).filter_by(user_id=user_id).all()

    if not contacts:
        return {"message": "No contacts found"}

    contact_list = []
    for contact in contacts:
        contact_user = db.query(User).filter_by(id=contact.contact_id).first()
        contact_list.append({
            "username": contact_user.username,
            "id": contact_user.id  # Ensure you're sending the contact's ID
        })

    return contact_list

# Pydantic model for sending a message
class SendMessageRequest(BaseModel):
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    content: str

@app.post("/send_message")
async def send_message(request_data: SendMessageRequest, db: Session = Depends(get_db)):
    # Fetch sender and receiver by their IDs
    sender = db.query(User).filter(User.id == request_data.sender_id).first()
    receiver = db.query(User).filter(User.id == request_data.receiver_id).first()

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="Sender or receiver not found")

    # Create an instance of the Mutation class
    mutation = Mutation()

    # Call the send_message mutation from your mutations.py
    try:
        # Replace info={'request': None} with None, since you don’t need it here
        result = mutation.send_message(
            sender_username=sender.username,
            receiver_username=receiver.username,
            content=request_data.content,
            info=None  # Remove the problematic info passing
        )
        return {"message": "Message sent successfully", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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



# Delete contact route
@app.delete("/delete_contact/{user_id}/{contact_id}")
def delete_contact(user_id: uuid.UUID, contact_id: uuid.UUID, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(user_id=user_id, contact_id=contact_id).first()

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()

    return {"message": "Contact deleted successfully"}

class GroupCreate(BaseModel):
    group_name: str

class GroupMemberAdd(BaseModel):
    group_id: int
    user_id: str

class MessageCreate(BaseModel):
    group_id: int
    sender_id: str
    content: str


@app.post("/groups")
async def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    try:
        db_group = Group(group_name=group.group_name)
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        return {"message": "Group created successfully", "group_id": db_group.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/groups/{group_id}/members/", response_model=GroupMemberAdd)
def add_member_to_group(group_id: int, user_id: str, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")

    db_member = GroupMember(group_id=group_id, user_id=user_id)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@app.post("/groups/{group_id}/messages/", response_model=MessageCreate)
def send_message_to_group(group_id: int, message: MessageCreate, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")

    db_message = GroupMessage(
        group_id=group_id,
        sender_id=message.sender_id,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8109)
