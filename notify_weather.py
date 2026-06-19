import os
import subprocess
import tempfile
from urllib.parse import quote

from kakao_send import send_message

CITY = "Seoul"


def fetch_weather():
    fmt = quote("%l: %C, 온도 %t (체감 %f), 습도 %h, 강수량 %p")
    url = f"https://wttr.in/{CITY}?format={fmt}"

    fd, temp_path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    try:
        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                "$ProgressPreference='SilentlyContinue'; "
                f"(Invoke-WebRequest -Uri '{url}' -UseBasicParsing -TimeoutSec 10 "
                "-Headers @{ 'User-Agent' = 'curl' }).Content "
                f"| Out-File -FilePath '{temp_path}' -Encoding utf8 -NoNewline",
            ],
            check=True,
        )
        with open(temp_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    finally:
        os.remove(temp_path)


def build_message():
    weather_line = fetch_weather()
    return f"오늘의 날씨\n{weather_line}"


def main():
    message = build_message()
    send_message(message)


if __name__ == "__main__":
    main()
