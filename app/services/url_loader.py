from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


URL_IMPORT_DIR = Path("data/raw/url_imports")


def _safe_filename_from_url(url: str) -> str:
    parsed = urlparse(url)

    domain = parsed.netloc.replace(".", "_")
    path = parsed.path.strip("/").replace("/", "_")

    if not path:
        path = "index"

    return f"{domain}_{path}.txt"


def fetch_url_to_text_file(url: str) -> str:
    URL_IMPORT_DIR.mkdir(parents=True, exist_ok=True)

    response = requests.get(
        url,
        timeout=10,
        headers={
            "User-Agent": "BusinessKnowledgeBaseAgent/0.1",
        },
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    lines = []
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned:
            lines.append(cleaned)

    cleaned_text = "\n".join(lines)

    file_path = URL_IMPORT_DIR / _safe_filename_from_url(url)
    file_path.write_text(cleaned_text, encoding="utf-8")

    return str(file_path)