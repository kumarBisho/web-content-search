from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import requests
import nltk
from sentence_transformers import SentenceTransformer
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility,
)
import time

# ======================================================
# 🌐 FASTAPI INITIALIZATION
# ======================================================
app = FastAPI(title="Smart HTML Semantic Search (Fresh Mode with Cosine Similarity)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# ⚙️ CONFIG
# ======================================================
COLLECTION_NAME = "web_chunks"
MAX_CHUNK_LEN = 9000
EMBEDDING_DIM = 384
MODEL_NAME = "all-MiniLM-L6-v2"

# ======================================================
# 🧠 LOAD MODEL
# ======================================================
nltk.download("punkt", quiet=True)
model = SentenceTransformer(MODEL_NAME)

# ======================================================
# 🧱 CONNECT TO MILVUS
# ======================================================
connections.connect(alias="default", host="localhost", port="19530")


def create_new_collection():
    """Drops old collection and creates a fresh one for each new search."""
    if utility.has_collection(COLLECTION_NAME):
        print("🧹 Dropping old Milvus collection...")
        utility.drop_collection(COLLECTION_NAME)

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="chunk_text", dtype=DataType.VARCHAR, max_length=10000),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
        FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=1000),
    ]
    schema = CollectionSchema(fields=fields, description="Website HTML content chunks")
    collection = Collection(name=COLLECTION_NAME, schema=schema)
    print(f"✅ Created new Milvus collection: {COLLECTION_NAME}")
    return collection


# ======================================================
# 🧹 UTILITIES
# ======================================================

def normalize_url(url: str) -> str:
    """Normalize URL by removing fragments, query params, and trailing slashes."""
    parsed = urlparse(url)
    # Keep scheme and netloc always
    normalized_path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme, parsed.netloc, normalized_path, "", "", ""))

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "meta", "svg", "img"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def chunk_text(text: str, max_tokens: int = 500):
    """Split text into smaller word-based chunks."""
    words = nltk.word_tokenize(text)
    for i in range(0, len(words), max_tokens):
        yield " ".join(words[i:i + max_tokens])


def get_internal_links(base_url: str, html: str, limit: int = 3):
    """Extract limited internal links safely within same domain."""
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
    """Fetch HTML safely with headers."""
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if resp.status_code == 200:
            return resp.text
        else:
            print(f"⚠️ Failed to fetch {url}: {resp.status_code}")
            return ""
    except Exception as e:
        print(f"⚠️ Error fetching {url}: {e}")
        return ""


# ======================================================
# 🔍 SEARCH ENDPOINT
# ======================================================
class SearchRequest(BaseModel):
    url: str
    query: str


@app.post("/search")
def search(req: SearchRequest):
    try:
        base_url = req.url

        # 1️⃣ Create a new Milvus collection for each request
        collection = create_new_collection()

        # 2️⃣ Fetch the main page
        main_html = fetch_html(base_url)
        if not main_html:
            raise HTTPException(status_code=400, detail="Unable to fetch URL")

        # 3️⃣ Crawl internal links (optional)
        pages = [base_url] + get_internal_links(base_url, main_html)
        
        normalized_pages = []
        seen = set()
        for p in pages:
            n = normalize_url(p)
            if n not in seen:
                seen.add(n)
                normalized_pages.append(n)

        pages = normalized_pages

        # 4️⃣ Clean and chunk text
        all_chunks = []
        for page in pages:
            html = fetch_html(page)
            if not html:
                continue
            text = clean_html(html)
            for chunk in chunk_text(text):
                all_chunks.append({"chunk": chunk[:MAX_CHUNK_LEN], "url": page})

        if not all_chunks:
            raise HTTPException(status_code=400, detail="No readable text content found")

        # 5️⃣ Embed and insert data
        texts = [c["chunk"] for c in all_chunks]
        urls = [c["url"] for c in all_chunks]
        embeddings = model.encode(texts, normalize_embeddings=True).tolist()  # ✅ normalize for cosine

        collection.insert([texts, embeddings, urls])
        collection.flush()

        # 6️⃣ Create vector index (COSINE)
        collection.create_index(
            field_name="embedding",
            index_params={
                "metric_type": "COSINE",  # ✅ use cosine similarity
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128},
            },
        )
        print("✅ Cosine index created successfully.")

        # 7️⃣ Load into memory
        collection.load()

        # 8️⃣ Perform semantic search
        query_vec = model.encode([req.query], normalize_embeddings=True).tolist()
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}

        results = collection.search(
            data=query_vec,
            anns_field="embedding",
            param=search_params,
            limit=10,
            output_fields=["chunk_text", "url"],
        )

        # 9️⃣ Format output with positive match scores
        formatted = []
        for hits in results:
            for hit in hits:
                # ✅ Cosine distance ∈ [0, 2] => similarity = 1 - distance
                score = round((1 - hit.distance) * 100, 2)
                if score < 0:
                    score = 0.0
                formatted.append({
                    "html_snippet": hit.entity.get("chunk_text")[:500],
                    "text": hit.entity.get("chunk_text")[:500],
                    "score": score,
                    "path": hit.entity.get("url"),
                })

        formatted = sorted(formatted, key=lambda x: x["score"], reverse=True)
        return {"results": formatted[:10]}

    except Exception as e:
        print(f"❌ Error during search: {e}")
        raise HTTPException(status_code=500, detail=str(e))