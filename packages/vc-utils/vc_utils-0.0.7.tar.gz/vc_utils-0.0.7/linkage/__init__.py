import os
import requests
from datetime import datetime
import asyncio
import json
import logging
from vc_config import get_config


login_address = os.getenv("VU_LINKAGE_LOGIN_SERVICE", get_config("linkage", {}).get("VU_LINKAGE_LOGIN_SERVICE"))
user_address = os.getenv("VU_LINKAGE_USER_SERVICE", get_config("linkage", {}).get("VU_LINKAGE_USER_SERVICE"))

async def login(username: str, password: str):
    # return (email, is_admin)
    if login_address and user_address:
        r = requests.post(login_address, data={'username': username, 'password': password})
        if r.status_code < 400:
            data = r.json()
            headers = {
                "Authorization": "Bearer " + data["access_token"]
            }
            response = requests.get(user_address, headers=headers)
            try:
                response.raise_for_status()
                data = response.json()
                data["email"] = data["email"].strip().lower()
                if "performanceManager" in data["claims"]:
                    return {'email': data['email'], 'is_admin': True}
                return {'email': data['email'], 'is_admin': False}
            except requests.exceptions.HTTPError as exc:
                logging.warning("Login failed", exc)

    raise Exception("Login failed")

