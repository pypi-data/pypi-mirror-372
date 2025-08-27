import os
import requests
from datetime import datetime
import asyncio
import json
import logging


dir_path = os.path.dirname(os.path.realpath(__file__))
conf_file = os.path.join(dir_path, "../conf/default.json")
with open(conf_file, "r") as f:
    config = json.load(f)

login_address = os.getenv("VU_LINKAGE_LOGIN_SERVICE", config.get("linkage", {}).get("VU_LINKAGE_LOGIN_SERVICE"))
user_address = os.getenv("VU_LINKAGE_USER_SERVICE", config.get("linkage", {}).get("VU_LINKAGE_USER_SERVICE"))

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

