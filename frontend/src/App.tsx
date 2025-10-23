import React, { useState } from "react";
import "./App.css";
import axios from "axios";

interface SearchResult {
  html_snippet: string;
  text: string;
  score: number;
  path: string;
}

const App: React.FC = () => {
  const [url, setUrl] = useState<string>("");
  const [query, setQuery] = useState<string>("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  const handleSearch = async () => {
    if (!url || !query) {
      setError("Please enter both Website URL and Search Query.");
      return;
    }

    setError("");
    setLoading(true);
    setResults([]);

    try {
      const response = await axios.post("http://127.0.0.1:8000/search", { url, query });
      setResults(response.data.results);
    } catch (err) {
      console.error(err);
      setError("⚠️ Failed to fetch results. Check backend connection or URL.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
    <div className="app-main">
        {/* ===== Header ===== */}
  <h1 className="app-header">
          Website Content Search
        </h1>
  <p className="app-desc">
          Search through website content and find the most relevant sections instantly.
        </p>

        {/* ===== Search Form ===== */}
        <div className="app-form">
          <input
            type="text"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="app-input"
          />
          <input
            type="text"
            placeholder="Search query (e.g. AI, robotics, analytics...)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="app-input"
          />
          <button
            onClick={handleSearch}
            disabled={loading}
            className="app-button app-button-fixed"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {/* ===== Error ===== */}
  {error && <p className="app-error">{error}</p>}

        {/* ===== Results Section ===== */}
        <div className={`app-results${results.length > 0 ? ' has-results' : ''}`}> 
          {loading && (
            <p style={{ color: "#2563eb", fontSize: "1rem" }}>🔍 Searching, please wait...</p>
          )}

          {!loading && results.length === 0 && !error && (
            <p style={{ color: "#94a3b8" }}>No results yet. Try entering a URL and search query.</p>
          )}

          {results.length > 0 && (
            <div className="app-result-list">
              {results.slice(0, 10).map((r, i) => (
                <div key={i} className="app-chunk card">
                  <div className="app-chunk-title" style={{marginBottom: '4px', textAlign: 'left'}}>
                    Chunk #{i + 1}
                  </div>
                  <div className="app-chunk-header-row">
                    <span className="app-chunk-path"><b>Path:</b> {r.path}</span>
                    <span className="app-chunk-score special-green">{r.score}% match</span>
                  </div>
                  <div className="app-chunk-info">
                    <p className="app-chunk-text"><b>Text:</b> {r.text}</p>
                  </div>
                  {/* <div className="app-chunk-html">
                    <b>HTML Snippet:</b>
                    <div dangerouslySetInnerHTML={{ __html: r.html_snippet }} />
                  </div> */}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
