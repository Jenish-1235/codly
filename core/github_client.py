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
