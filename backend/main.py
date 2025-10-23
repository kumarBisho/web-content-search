from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import SearchRequest
from db.milvus import connect_milvus, create_new_collection
from utils.html import clean_html, chunk_text, get_internal_links, fetch_html, normalize_url
from sentence_transformers import SentenceTransformer
import nltk
from config import MODEL_NAME, MAX_CHUNK_LEN

# ======================================================
# 🌐 FASTAPI INITIALIZATION
# ======================================================
app = FastAPI(title="Smart HTML Semantic Search (Refactored)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# 🧠 LOAD MODEL
# ======================================================
nltk.download("punkt", quiet=True)
model = SentenceTransformer(MODEL_NAME)
connect_milvus()


# ======================================================
# 🔍 SEARCH ENDPOINT
# ======================================================
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