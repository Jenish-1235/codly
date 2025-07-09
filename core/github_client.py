import httpx

GITHUB_API_URL = "https://api.github.com"

async def get_user_repos(access_token: str) -> list:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{GITHUB_API_URL}/user/repos", headers=headers)

        if response.status_code != 200:
            raise Exception(f"GitHub API error: {response.status_code} {response.text}")

        return response.json()

async def create_github_issue(token: str, repo: str, title: str, body: str):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    payload = {
        "title": title,
        "body": body,
        "labels": ["codly"]  # Automatically tag Codly-created issues
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{GITHUB_API_URL}/repos/{repo}/issues",
            headers=headers,
            json=payload
        )
        if response.status_code != 201:
            raise Exception(f"GitHub issue creation failed: {response.status_code} {response.text}")
        return response.json()