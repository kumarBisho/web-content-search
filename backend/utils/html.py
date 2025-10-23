# utils/html.py
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import nltk
import requests

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    normalized_path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme, parsed.netloc, normalized_path, "", "", ""))

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "meta", "svg", "img"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)

def chunk_text(text: str, max_tokens: int = 500):
    words = nltk.word_tokenize(text)
    for i in range(0, len(words), max_tokens):
        yield " ".join(words[i:i + max_tokens])

def get_internal_links(base_url: str, html: str, limit: int = 3):
    soup = BeautifulSoup(html, "html.parser")
    domain = urlparse(base_url).netloc
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("#") or href.lower().startswith("javascript:"):
            continue
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc == domain:
            links.add(full_url)
        if len(links) >= limit:
            break
    return list(links)

def fetch_html(url: str) -> str:
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if resp.status_code == 200:
            return resp.text
        else:
            return ""
    except Exception:
        return ""
