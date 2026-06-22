import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from kakao_send import send_message

RSS_URL = "https://www.yna.co.kr/rss/economy.xml"
MAX_ITEMS = 5


def fetch_rss():
    fd, temp_path = tempfile.mkstemp(suffix=".xml")
    os.close(fd)
    try:
        subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-Command",
                "$ProgressPreference='SilentlyContinue'; "
                f"(Invoke-WebRequest -Uri '{RSS_URL}' -UseBasicParsing -TimeoutSec 10 "
                "-Headers @{ 'User-Agent' = 'Mozilla/5.0' }).Content "
                f"| Out-File -FilePath '{temp_path}' -Encoding utf8 -NoNewline",
            ],
            check=True,
        )
        with open(temp_path, "r", encoding="utf-8") as f:
            return f.read()
    finally:
        os.remove(temp_path)


def parse_titles(xml_text, limit=MAX_ITEMS):
    root = ET.fromstring(xml_text)
    titles = []
    for item in root.iter("item"):
        title_el = item.find("title")
        if title_el is not None and title_el.text:
            titles.append(title_el.text.strip())
        if len(titles) >= limit:
            break
    return titles


def build_message():
    titles = parse_titles(fetch_rss())
    lines = [f"{i}. {title}" for i, title in enumerate(titles, start=1)]
    return "오늘의 경제 뉴스\n" + "\n".join(lines)


def main():
    send_message(build_message())


if __name__ == "__main__":
    main()
