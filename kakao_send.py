import json
import os
import subprocess
import tempfile

from dotenv import load_dotenv

load_dotenv()

REST_API_KEY = os.environ["KAKAO_REST_API_KEY"]
CLIENT_SECRET = os.environ["KAKAO_CLIENT_SECRET"]
TOKEN_FILE = "kakao_token.json"

_POST_SCRIPT = """
$ProgressPreference = 'SilentlyContinue'
$payload = Get-Content -Raw -Encoding UTF8 '__PAYLOAD__' | ConvertFrom-Json
$headers = @{}
foreach ($p in $payload.headers.PSObject.Properties) { $headers[$p.Name] = $p.Value }
$body = @{}
foreach ($p in $payload.data.PSObject.Properties) { $body[$p.Name] = $p.Value }
try {
    $resp = Invoke-WebRequest -Uri $payload.url -Method Post -Headers $headers -Body $body -UseBasicParsing -TimeoutSec 10
    $result = @{ status_code = [int]$resp.StatusCode; content = $resp.Content }
} catch {
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $content = $reader.ReadToEnd()
        $result = @{ status_code = [int]$_.Exception.Response.StatusCode; content = $content }
    } else {
        $result = @{ status_code = 0; content = $_.Exception.Message }
    }
}
$result | ConvertTo-Json -Compress | Out-File -FilePath '__RESULT__' -Encoding utf8 -NoNewline
"""


def _post(url, data, headers=None):
    """POST via PowerShell's Invoke-WebRequest (schannel) instead of Python's
    ssl module, which gets ConnectionResetError against kapi.kakao.com /
    kauth.kakao.com when the server requests TLS renegotiation."""
    fd, payload_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    fd, result_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        with open(payload_path, "w", encoding="utf-8") as f:
            json.dump({"url": url, "data": data, "headers": headers or {}}, f)

        script = _POST_SCRIPT.replace("__PAYLOAD__", payload_path).replace(
            "__RESULT__", result_path
        )
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", script], check=True
        )

        with open(result_path, "r", encoding="utf-8-sig") as f:
            result = json.load(f)
        return result["status_code"], result["content"]
    finally:
        os.remove(payload_path)
        os.remove(result_path)


def load_tokens():
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tokens(tokens):
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f)


def refresh_access_token(tokens):
    status, content = _post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "refresh_token",
            "client_id": REST_API_KEY,
            "client_secret": CLIENT_SECRET,
            "refresh_token": tokens["refresh_token"],
        },
    )
    if status >= 400:
        raise RuntimeError(f"Kakao token refresh failed ({status}): {content}")
    new_tokens = json.loads(content)

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
    data = {"template_object": json.dumps(template_object)}

    status, content = _post(
        "https://kapi.kakao.com/v2/api/talk/memo/default/send",
        data=data,
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    if status == 401:
        tokens = refresh_access_token(tokens)
        status, content = _post(
            "https://kapi.kakao.com/v2/api/talk/memo/default/send",
            data=data,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )

    if status >= 400:
        raise RuntimeError(f"Kakao send failed ({status}): {content}")
    return json.loads(content)


if __name__ == "__main__":
    result = send_message("테스트 메시지입니다!")
    print(result)
