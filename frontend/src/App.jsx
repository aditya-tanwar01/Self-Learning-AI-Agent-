import { useState } from "react";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const research = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("https://self-learning-ai-agent-eight.vercel.app/research", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: query.trim(),
        }),
      });

      const text = await response.text();

      console.log("Backend response:", text);

      if (!response.ok) {
        throw new Error(text || "Backend error");
      }

      let data;

      try {
        data = JSON.parse(text);
      } catch {
        throw new Error("Backend returned invalid JSON: " + text);
      }

      if (data.error) {
        throw new Error(data.error);
      }

      setResult(data);
    } catch (err) {
      console.error("Research error:", err);
      setError(err.message || "Could not connect to the AI backend.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      research();
    }
  };

  return (
    <div className="app">
      <div className="background-glow glow-one"></div>
      <div className="background-glow glow-two"></div>

      <header className="navbar">
        <div className="logo">
          <div className="logo-icon">AI</div>
          <span>Self Learning AI</span>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          AI Agent Online
        </div>
      </header>

      <main className="main">
        <section className="hero">
          <div className="badge">
            <span>✦</span>
            AI Research Agent
          </div>

          <h1>
            Research smarter.
            <br />
            <span>Learn faster.</span>
          </h1>

          <p>
            Ask anything and let your AI agent research the topic,
            find useful information, and organize the results for you.
          </p>
        </section>

        <section className="search-card">
          <div className="input-header">
            <span>What would you like to research?</span>
            <span className="shortcut">ENTER ↵</span>
          </div>

          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Example: Explain the population growth of Asia..."
            rows="4"
          />

          <div className="search-bottom">
            <span className="hint">
              Your AI agent can search and analyze information.
            </span>

            <button
              onClick={research}
              disabled={loading || !query.trim()}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Researching...
                </>
              ) : (
                <>
                  Research
                  <span>→</span>
                </>
              )}
            </button>
          </div>
        </section>

        {error && (
          <div className="error-box">
            <span>⚠</span>
            {error}
          </div>
        )}

        {loading && (
          <section className="loading-card">
            <div className="loading-icon">
              <div className="pulse"></div>
              AI
            </div>

            <div>
              <h3>Researching your topic...</h3>
              <p>
                Your AI agent is gathering and processing information.
              </p>
            </div>
          </section>
        )}

        {result && !loading && (
          <section className="result-section">
            <div className="result-title">
              <div>
                <span className="small-label">RESEARCH RESULT</span>
                <h2>{result.topic || "Research Result"}</h2>
              </div>

              <div className="result-check">✓ Complete</div>
            </div>

            <div className="summary-card">
              <h3>Summary</h3>
              <p>{result.summary || "No summary returned."}</p>
            </div>

            {result.sources && result.sources.length > 0 && (
              <div className="info-card">
                <div className="card-heading">
                  <span className="card-icon">◉</span>
                  <h3>Sources</h3>
                </div>

                <div className="source-list">
                  {result.sources.map((source, index) => (
                    <div className="source" key={index}>
                      <span>{index + 1}</span>
                      <p>{source}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.tools_used && result.tools_used.length > 0 && (
              <div className="info-card">
                <div className="card-heading">
                  <span className="card-icon">⚙</span>
                  <h3>Tools Used</h3>
                </div>

                <div className="tools">
                  {result.tools_used.map((tool, index) => (
                    <span className="tool" key={index}>
                      {tool}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

        {!result && !loading && !error && (
          <section className="features">
            <div className="feature">
              <div className="feature-icon">⌕</div>
              <h3>Research</h3>
              <p>
                Search for information across multiple sources.
              </p>
            </div>

            <div className="feature">
              <div className="feature-icon">✦</div>
              <h3>Analyze</h3>
              <p>
                Let the AI organize and summarize what it finds.
              </p>
            </div>

            <div className="feature">
              <div className="feature-icon">↓</div>
              <h3>Save</h3>
              <p>
                Save your research results for later use.
              </p>
            </div>
          </section>
        )}
      </main>

      <footer>
        <span>Self Learning AI</span>
        <span>Powered by AI Agent Technology</span>
      </footer>
    </div>
  );
}

export default App;