import json
import os

LOGIN_FILE_PATH = "login.json"

if not os.path.exists(LOGIN_FILE_PATH):
    with open(LOGIN_FILE_PATH, 'w') as f:
        json.dump({"users": []}, f)

def load_users():
    if not os.path.exists(LOGIN_FILE_PATH):
        with open(LOGIN_FILE_PATH, "w") as file:
            json.dump({"users": []}, file)
        return {"users": []}

    try:
        with open(LOGIN_FILE_PATH, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {"users": []}

def save_users(data):
    with open(LOGIN_FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)