# Web Content Search

A full-stack web application for semantic search and chunked retrieval of website content. The frontend is built with React (Vite, TypeScript), and the backend uses FastAPI, BeautifulSoup, NLTK, sentence-transformers, FAISS, and Milvus for vector search.

## Features
- Enter a website URL and search query to find the most relevant content chunks.
- Semantic search using transformer embeddings and vector similarity.
- Results are displayed in styled cards with match scores and chunk details.
- Modern, responsive UI with clear chunk grouping and search form.

---

## Prerequisites
- **Node.js** (v18+ recommended)
- **Python** (v3.9+ recommended)
- **pip** (Python package manager)
- **Milvus** (vector database, can run locally via Docker)

---

## Local Setup Instructions

### 1. Clone the Repository
```sh
git clone https://github.com/kumarBisho/web-content-search.git
cd web-content-search
```

### 2. Backend Setup
```sh
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### Milvus Setup (Vector Database)
- **Option 1: Docker (Recommended)**
	- Install Docker: https://docs.docker.com/get-docker/
	- Run Milvus:
		```sh
		docker run -d --name milvus-standalone -p 19530:19530 -p 9091:9091 milvusdb/milvus:v2.3.9
		```
- **Option 2: Local Install**
	- See Milvus docs: https://milvus.io/docs/install_standalone-docker.md

#### Backend Configuration
- Edit `.env` in `backend/` if needed (see `.env.example`).
- Default Milvus connection: `localhost:19530`

#### Run Backend
```sh
uvicorn main:app --reload
```

---


### 3. Frontend Setup
```sh
cd ../frontend
# Install Node.js dependencies
npm install
# (Optional) Install Python requirements if using Python scripts in frontend
pip install -r requirements.txt
```

#### Frontend Configuration
- Default backend API URL: `http://127.0.0.1:8000`

#### Run Frontend
```sh
npm run dev
```

---

## Usage
1. Start Milvus (vector DB) and backend server.
2. Start frontend dev server.
3. Open the frontend in your browser (usually http://localhost:5173).
4. Enter a website URL and search query, then click "Search".
5. View top matching content chunks with semantic relevance scores.

---

## Dependencies
### Backend
- fastapi
- uvicorn
- beautifulsoup4
- nltk
- sentence-transformers
- faiss-cpu
- pymilvus
- python-dotenv

### Frontend
- react
- vite
- typescript
- axios

---

## Additional Notes
- Ensure Milvus is running before starting the backend.
- You may need to download NLTK data (handled automatically in code).
- For production, set proper CORS and environment variables.
- See `.env.example` files for configuration templates.

---

## License
MIT