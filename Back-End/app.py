
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from strawberry.fastapi import GraphQLRouter
from schema import schema
from auth.authentication import register_user  # Make sure this imports correctly
import sys
import os
import logging

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
class User(BaseModel):
    username: str
    email: str
    password: str

@app.post("/signup")
async def signup(user: User):
    # Deine Logik zur Registrierung des Nutzers
    # Beispielhafte Rückgabe nach erfolgreicher Registrierung
    return {"message": "User registered successfully", "username": user.username}

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8073)


