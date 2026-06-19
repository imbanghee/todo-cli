import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

REST_API_KEY = os.environ["KAKAO_REST_API_KEY"]
TOKEN_FILE = "kakao_token.json"


def load_tokens():
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tokens(tokens):
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f)


def refresh_access_token(tokens):
    response = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "refresh_token",
            "client_id": REST_API_KEY,
            "refresh_token": tokens["refresh_token"],
        },
    )
    response.raise_for_status()
    new_tokens = response.json()

    tokens["access_token"] = new_tokens["access_token"]
    if "refresh_token" in new_tokens:
        tokens["refresh_token"] = new_tokens["refresh_token"]
    save_tokens(tokens)
    return tokens


def send_message(text):
    tokens = load_tokens()
    template_object = {
        "object_type": "text",
        "text": text,
        "link": {},
    }

    response = requests.post(
        "https://kapi.kakao.com/v2/api/talk/memo/default/send",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        data={"template_object": json.dumps(template_object)},
    )

    if response.status_code == 401:
        tokens = refresh_access_token(tokens)
        response = requests.post(
            "https://kapi.kakao.com/v2/api/talk/memo/default/send",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            data={"template_object": json.dumps(template_object)},
        )

    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    result = send_message("테스트 메시지입니다!")
    print(result)
