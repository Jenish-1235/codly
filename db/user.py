from tinydb import TinyDB, Query
import os

# Ensure the db directory exists
os.makedirs("db/data", exist_ok=True)

db = TinyDB("db/data/users.json")
User = Query()

def save_user_token(telegram_id: int, access_token: str, github_username: str):
    existing = db.search(User.telegram_id == telegram_id)
    if existing:
        db.update(
            {"access_token": access_token, "github_username": github_username},
            User.telegram_id == telegram_id
        )
    else:
        db.insert({
            "telegram_id": telegram_id,
            "access_token": access_token,
            "github_username": github_username
        })

def get_user_token(telegram_id: int):
    result = db.search(User.telegram_id == telegram_id)
    if result:
        return {
            "access_token": result[0]["access_token"],
            "github_username": result[0]["github_username"]
        }
    return None
