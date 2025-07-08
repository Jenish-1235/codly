from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
import os
import httpx
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
OAUTH_CALLBACK_URL = os.getenv("OAUTH_CALLBACK_URL")

# Temporary in-memory store (use DB later)
OAUTH_SESSIONS = {}


@router.get("/start_auth")
async def start_auth(telegram_user_id: int):
    state = str(telegram_user_id)  # Later use UUID + DB mapping
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": OAUTH_CALLBACK_URL,
        "scope": "repo",
        "state": state
    }
    url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/callback")
async def github_callback(code: str, state: str):
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://github.com/login/oauth/access_token", data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": OAUTH_CALLBACK_URL,
            "state": state
        }, headers={"Accept": "application/json"})

        data = resp.json()
        access_token = data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="GitHub authentication failed.")

        # Fetch GitHub username for reference
        user_resp = await client.get("https://api.github.com/user", headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        })
        gh_user = user_resp.json()
        github_username = gh_user.get("login")

    # Store token (replace with DB call)
    OAUTH_SESSIONS[state] = {
        "access_token": access_token,
        "github_username": github_username
    }

    return HTMLResponse(f"<h3>✅ GitHub Connected as {github_username}. You may return to Telegram.</h3>")
