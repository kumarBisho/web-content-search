import React, { useState } from "react";
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
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: "#f8fafc",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: "Inter, Arial, sans-serif",
            padding: 0,
            width: "100vw",
            boxSizing: "border-box"
      }}
    >
      {/* ===== Main Container ===== */}
      <div
        style={{
          width: "100%",
          maxWidth: "960px",
          backgroundColor: "#ffffff",
          borderRadius: "16px",
          padding: "2rem 3rem",
          boxShadow: "0 4px 15px rgba(0,0,0,0.08)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          transition: "all 0.3s ease",
        }}
      >
        {/* ===== Header ===== */}
        <h1 style={{ fontSize: "2rem", fontWeight: 700, color: "#1e293b", marginBottom: "0.5rem" }}>
          Website Content Search
        </h1>
        <p style={{ color: "#64748b", marginBottom: "2rem", textAlign: "center", maxWidth: "600px" }}>
          Search through website content and find the most relevant sections instantly.
        </p>

        {/* ===== Search Form ===== */}
        <div
          style={{
            width: "100%",
            maxWidth: "600px",
            display: "flex",
            flexDirection: "column",
            gap: "1rem",
            alignItems: "center",
            marginBottom: "2rem",
          }}
        >
          <input
            type="text"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            style={{
              width: "100%",
              padding: "12px 16px",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              fontSize: "1rem",
              outline: "none",
              transition: "border-color 0.2s",
            }}
            onFocus={(e) => (e.currentTarget.style.borderColor = "#2563eb")}
            onBlur={(e) => (e.currentTarget.style.borderColor = "#cbd5e1")}
          />

          <input
            type="text"
            placeholder="Search query (e.g. AI, robotics, analytics...)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{
              width: "100%",
              padding: "12px 16px",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
              fontSize: "1rem",
              outline: "none",
              transition: "border-color 0.2s",
            }}
            onFocus={(e) => (e.currentTarget.style.borderColor = "#2563eb")}
            onBlur={(e) => (e.currentTarget.style.borderColor = "#cbd5e1")}
          />

          <button
            onClick={handleSearch}
            disabled={loading}
            style={{
              backgroundColor: loading ? "#1d4ed8" : "#2563eb",
              color: "#fff",
              border: "none",
              padding: "12px 24px",
              borderRadius: "8px",
              fontSize: "1rem",
              fontWeight: 600,
              cursor: loading ? "not-allowed" : "pointer",
              width: "100%",
              maxWidth: "200px",
              boxShadow: "0 2px 8px rgba(37,99,235,0.25)",
              transition: "background-color 0.2s",
            }}
            onMouseEnter={(e) => !loading && (e.currentTarget.style.backgroundColor = "#1d4ed8")}
            onMouseLeave={(e) => !loading && (e.currentTarget.style.backgroundColor = "#2563eb")}
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {/* ===== Error ===== */}
        {error && <p style={{ color: "red", marginBottom: "1rem" }}>{error}</p>}

        {/* ===== Results Section ===== */}
        <div
          style={{
            width: "100%",
            maxWidth: "800px",
            minHeight: "400px", // ✅ keeps layout static
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: results.length === 0 ? "center" : "flex-start",
          }}
        >
          {loading && (
            <p style={{ color: "#2563eb", fontSize: "1rem" }}>🔍 Searching, please wait...</p>
          )}

          {!loading && results.length === 0 && !error && (
            <p style={{ color: "#94a3b8" }}>No results yet. Try entering a URL and search query.</p>
          )}

          {results.length > 0 && (
            <div style={{ width: "100%", display: "grid", gap: "1rem" }}>
              {results.slice(0, 10).map((r, i) => (
                <div
                  key={i}
                  style={{
                    backgroundColor: "#ffffff",
                    border: "1px solid #e2e8f0",
                    borderRadius: "12px",
                    padding: "16px 20px",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
                    transition: "transform 0.2s",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: "8px",
                      alignItems: "center",
                    }}
                  >
                    <b style={{ color: "#1e293b" }}>Chunk #{i + 1}</b>
                    <span
                      style={{
                        backgroundColor:
                          r.score >= 85
                            ? "#dcfce7"
                            : r.score >= 60
                            ? "#fef9c3"
                            : "#f3f4f6",
                        color:
                          r.score >= 85
                            ? "#166534"
                            : r.score >= 60
                            ? "#854d0e"
                            : "#4b5563",
                        padding: "3px 10px",
                        borderRadius: "6px",
                        fontSize: "0.85rem",
                        fontWeight: 600,
                      }}
                    >
                      {r.score}% match
                    </span>
                  </div>

                  <p style={{ fontSize: "0.9rem", color: "#475569", marginBottom: "8px" }}>
                    <b>Path:</b> {r.path}
                  </p>

                  <div
                    style={{
                      backgroundColor: "#f9fafb",
                      border: "1px solid #f1f5f9",
                      borderRadius: "8px",
                      padding: "10px",
                      fontSize: "0.9rem",
                      color: "#334155",
                      wordBreak: "break-word",
                    }}
                  >
                    <div dangerouslySetInnerHTML={{ __html: r.html_snippet }} />
                  </div>
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
