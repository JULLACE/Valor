import riot_auth, asyncio
import os, dotenv, sys
import urllib

import requests

async def load_cred():
    dotenv.load_dotenv()

    current_version = requests.get("https://valorant-api.com/v1/version").json()["data"]["riotClientBuild"]

    from riot_auth import RiotAuth
    RiotAuth.RIOT_CLIENT_USER_AGENT = f"RiotClient/{current_version} rso-auth (Windows;10;;Professional, x64)"
    CREDS = os.getenv('USER'), os.getenv('PASS')

    auth = riot_auth.RiotAuth()
    await auth.authorize(*CREDS)

    # print(f"Access Token Type: {auth.token_type}\n")
    # print(f"Access Token: {auth.access_token}\n")
    # print(f"Entitlements Token: {auth.entitlements_token}\n")
    # print(f"User ID: {auth.user_id}")

    return auth
