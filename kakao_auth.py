import os
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import requests
from dotenv import load_dotenv

load_dotenv()

REST_API_KEY = os.environ["KAKAO_REST_API_KEY"]
CLIENT_SECRET = os.environ["KAKAO_CLIENT_SECRET"]
REDIRECT_URI = os.environ["KAKAO_REDIRECT_URI"]
TOKEN_FILE = "kakao_token.json"

auth_code = {}


class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        if "code" in query:
            auth_code["code"] = query["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("인증 완료! 이 창은 닫으셔도 됩니다.".encode("utf-8"))
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def get_authorization_code():
    auth_url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={REST_API_KEY}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&scope=talk_message"
    )
    print(f"브라우저가 열리지 않으면 아래 URL을 직접 열어주세요:\n{auth_url}\n")
    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", 5000), OAuthHandler)
    while "code" not in auth_code:
        server.handle_request()
    return auth_code["code"]


def get_tokens(code):
    response = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": REST_API_KEY,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "code": code,
        },
    )
    if not response.ok:
        print(response.text)
    response.raise_for_status()
    return response.json()


def main():
    code = get_authorization_code()
    tokens = get_tokens(code)

    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        import json

        json.dump(tokens, f)

    print(f"토큰 저장 완료: {TOKEN_FILE}")


if __name__ == "__main__":
    main()
