from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from strawberry.fastapi import GraphQLRouter
from schema import schema
from auth.authentication import register_user  # Make sure this imports correctly
import sys
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend address
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers
)


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()

# Set up CORS to allow frontend requests if they're on a different port (e.g., Vite on port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for validating signup requests
class UserRegister(BaseModel):
    username: str
    password: str
    email: str

# Define a signup API route for registration
@app.post("/api/signup")
async def signup(user: UserRegister, request: Request):
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")
    os = request.headers.get("sec-ch-ua-platform")

    try:
        # Call your register_user function to register and store the user in DB and JSON
        result = register_user(user.username, user.password, user.email, ip_address, user_agent, os)
        return {"message": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Existing GraphQL setup
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8060)
