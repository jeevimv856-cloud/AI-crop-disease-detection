// App.jsx — Redesigned Crop Disease Detector
import { useState, useRef } from "react";

const API = "http://localhost:8000";

const severityColor = {
  "None":      { bg: "#dcfce7", text: "#15803d", dot: "#22c55e" },
  "Medium":    { bg: "#fef9c3", text: "#a16207", dot: "#eab308" },
  "High":      { bg: "#fee2e2", text: "#b91c1c", dot: "#ef4444" },
  "Very High": { bg: "#f3e8ff", text: "#7e22ce", dot: "#a855f7" },
};

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'DM Sans', sans-serif;
    background: #0a1f0e;
    min-height: 100vh;
    color: #1a1a1a;
  }

  .app {
    min-height: 100vh;
    background:
      radial-gradient(ellipse at 20% 20%, rgba(34,197,94,0.12) 0%, transparent 60%),
      radial-gradient(ellipse at 80% 80%, rgba(5,150,105,0.10) 0%, transparent 60%),
      linear-gradient(160deg, #0a1f0e 0%, #0d2b14 40%, #071a0b 100%);
    padding: 0 16px 60px;
  }

  /* ── Header ── */
  .header {
    text-align: center;
    padding: 48px 20px 32px;
    position: relative;
  }
  .header::after {
    content: '';
    display: block;
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, #22c55e, #059669);
    margin: 16px auto 0;
    border-radius: 2px;
  }
  .header-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.25);
    color: #86efac;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 100px;
    margin-bottom: 18px;
  }
  .header-badge::before {
    content: '';
    width: 6px; height: 6px;
    background: #22c55e;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.5; transform: scale(0.8); }
  }
  .header h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(28px, 5vw, 42px);
    font-weight: 700;
    color: #ffffff;
    line-height: 1.15;
    letter-spacing: -0.5px;
  }
  .header h1 span { color: #4ade80; }
  .header p {
    margin-top: 10px;
    color: #6b9e78;
    font-size: 14px;
    font-weight: 300;
    letter-spacing: 0.03em;
  }

  /* ── Card ── */
  .card {
    background: #ffffff;
    border-radius: 24px;
    padding: 28px;
    max-width: 500px;
    margin: 0 auto;
    box-shadow:
      0 0 0 1px rgba(255,255,255,0.05),
      0 24px 48px rgba(0,0,0,0.35),
      0 8px 16px rgba(0,0,0,0.2);
  }

  /* ── Drop Zone ── */
  .drop-zone {
    border: 2px dashed #bbf7d0;
    border-radius: 16px;
    background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
    cursor: pointer;
    overflow: hidden;
    transition: border-color 0.2s, background 0.2s;
    position: relative;
    min-height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .drop-zone:hover {
    border-color: #4ade80;
    background: linear-gradient(135deg, #dcfce7, #d1fae5);
  }
  .drop-zone img {
    width: 100%;
    max-height: 260px;
    object-fit: cover;
    border-radius: 14px;
    display: block;
  }
  .drop-prompt {
    text-align: center;
    padding: 32px 20px;
  }
  .drop-icon {
    width: 56px; height: 56px;
    background: linear-gradient(135deg, #dcfce7, #d1fae5);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 14px;
    font-size: 26px;
    box-shadow: 0 4px 12px rgba(34,197,94,0.2);
  }
  .drop-prompt h3 {
    font-size: 15px;
    font-weight: 600;
    color: #166534;
    margin-bottom: 4px;
  }
  .drop-prompt p {
    font-size: 12px;
    color: #6b9e78;
    font-weight: 300;
  }

  /* ── Buttons ── */
  .btn-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 14px;
  }
  .btn-outline {
    padding: 12px;
    border: 1.5px solid #d1fae5;
    background: #f0fdf4;
    color: #059669;
    border-radius: 12px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.2s;
  }
  .btn-outline:hover {
    background: #dcfce7;
    border-color: #6ee7b7;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(5,150,105,0.15);
  }
  .btn-detect {
    width: 100%;
    margin-top: 12px;
    padding: 15px;
    border: none;
    border-radius: 14px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 15px;
    cursor: pointer;
    transition: all 0.25s;
    position: relative;
    overflow: hidden;
  }
  .btn-detect.active {
    background: linear-gradient(135deg, #059669, #047857);
    color: white;
    box-shadow: 0 6px 20px rgba(5,150,105,0.4);
  }
  .btn-detect.active:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 28px rgba(5,150,105,0.45);
  }
  .btn-detect.active:active { transform: translateY(0); }
  .btn-detect.inactive {
    background: #f3f4f6;
    color: #9ca3af;
    cursor: not-allowed;
  }
  .btn-detect.loading {
    background: linear-gradient(135deg, #059669, #047857);
    color: white;
  }
  .spinner {
    display: inline-block;
    width: 16px; height: 16px;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    margin-right: 8px;
    vertical-align: middle;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  .error-msg {
    margin-top: 10px;
    padding: 10px 14px;
    background: #fff1f2;
    border: 1px solid #fecdd3;
    border-radius: 10px;
    color: #be123c;
    font-size: 13px;
    font-weight: 500;
  }

  /* ── Result Card ── */
  .result-card {
    background: #ffffff;
    border-radius: 24px;
    max-width: 500px;
    margin: 16px auto 0;
    overflow: hidden;
    box-shadow:
      0 0 0 1px rgba(255,255,255,0.05),
      0 24px 48px rgba(0,0,0,0.35);
    animation: slideUp 0.4s cubic-bezier(0.16,1,0.3,1);
  }
  @keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .result-header {
    padding: 24px 28px 20px;
    border-bottom: 1px solid #f3f4f6;
  }
  .result-crop-tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #059669;
    background: #f0fdf4;
    padding: 4px 10px;
    border-radius: 100px;
    margin-bottom: 10px;
  }
  .result-disease {
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    font-weight: 700;
    color: #111827;
    line-height: 1.2;
    margin-bottom: 10px;
  }
  .result-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }
  .confidence-bar-wrap {
    flex: 1;
    min-width: 140px;
  }
  .confidence-label {
    font-size: 11px;
    color: #6b7280;
    font-weight: 500;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
  }
  .confidence-bar-bg {
    height: 6px;
    background: #f3f4f6;
    border-radius: 100px;
    overflow: hidden;
  }
  .confidence-bar-fill {
    height: 100%;
    border-radius: 100px;
    background: linear-gradient(90deg, #059669, #34d399);
    transition: width 1s cubic-bezier(0.16,1,0.3,1);
  }
  .severity-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 600;
  }
  .severity-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
  }

  .result-body { padding: 20px 28px 28px; }
  .result-desc {
    font-size: 13px;
    color: #6b7280;
    line-height: 1.6;
    margin-bottom: 20px;
    padding: 12px 16px;
    background: #f9fafb;
    border-radius: 10px;
    border-left: 3px solid #d1fae5;
  }

  .result-section { margin-bottom: 20px; }
  .result-section-title {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 10px;
  }
  .treatment-list { list-style: none; }
  .treatment-list li {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 9px 0;
    border-bottom: 1px solid #f9fafb;
    font-size: 13px;
    color: #374151;
    line-height: 1.5;
  }
  .treatment-list li:last-child { border-bottom: none; }
  .treatment-num {
    width: 22px; height: 22px;
    background: linear-gradient(135deg, #059669, #047857);
    color: white;
    border-radius: 50%;
    font-size: 11px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
  }
  .prevention-list { display: flex; flex-wrap: wrap; gap: 8px; }
  .prevention-tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 6px 12px;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 500;
    color: #166534;
  }
  .prevention-tag::before { content: '✓'; font-weight: 700; color: #22c55e; }
`;

export default function App() {
  const [img, setImg]         = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const fileRef = useRef();

  const handleFile = (f) => {
    if (!f) return;
    setImg(f);
    setPreview(URL.createObjectURL(f));
    setResult(null); setError(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    handleFile(e.dataTransfer.files[0]);
  };

  const detect = async () => {
    if (!img) return;
    setLoading(true); setError(null);
    try {
      const fd = new FormData();
      fd.append("file", img);
      const res = await fetch(API + "/predict", { method: "POST", body: fd });
      if (!res.ok) throw new Error("Server error. Is backend running?");
      setResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const sev = result ? severityColor[result.severity] || severityColor["None"] : null;

  return (
    <>
      <style>{styles}</style>
      <div className="app">

        {/* ── Header ── */}
        <div className="header">
          <div className="header-badge">AI Powered · Live Detection</div>
          <h1>Crop <span>Disease</span> Detector</h1>
          <p>Arecanut &amp; Tomato — Upload a leaf image for instant diagnosis</p>
        </div>

        {/* ── Upload Card ── */}
        <div className="card">
          <div
            className="drop-zone"
            onDrop={handleDrop}
            onDragOver={e => e.preventDefault()}
            onClick={() => fileRef.current.click()}
          >
            {preview
              ? <img src={preview} alt="Uploaded leaf" />
              : (
                <div className="drop-prompt">
                  <div className="drop-icon">🌿</div>
                  <h3>Upload a Leaf Image</h3>
                  <p>Tap to browse or drag &amp; drop here</p>
                </div>
              )
            }
          </div>

          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            capture="environment"
            style={{ display: "none" }}
            onChange={e => handleFile(e.target.files[0])}
          />

          <div className="btn-row">
            <button className="btn-outline" onClick={() => fileRef.current.click()}>
              🖼️ Gallery
            </button>
            <button className="btn-outline" onClick={() => fileRef.current.click()}>
              📷 Camera
            </button>
          </div>

          <button
            className={`btn-detect ${loading ? "loading" : img ? "active" : "inactive"}`}
            onClick={detect}
            disabled={!img || loading}
          >
            {loading
              ? <><span className="spinner" />Analyzing leaf...</>
              : "🔍 Detect Disease"
            }
          </button>

          {error && <div className="error-msg">⚠️ {error}</div>}
        </div>

        {/* ── Result Card ── */}
        {result && (
          <div className="result-card">
            <div className="result-header">
              <div className="result-crop-tag">🌱 {result.crop}</div>
              <div className="result-disease">{result.disease_name}</div>
              <div className="result-meta">
                <div className="confidence-bar-wrap">
                  <div className="confidence-label">
                    <span>Confidence</span>
                    <span style={{ fontWeight: 700, color: "#059669" }}>{result.confidence}%</span>
                  </div>
                  <div className="confidence-bar-bg">
                    <div
                      className="confidence-bar-fill"
                      style={{ width: `${result.confidence}%` }}
                    />
                  </div>
                </div>
                <div
                  className="severity-badge"
                  style={{ background: sev.bg, color: sev.text }}
                >
                  <span className="severity-dot" style={{ background: sev.dot }} />
                  {result.severity} Risk
                </div>
              </div>
            </div>

            <div className="result-body">
              <p className="result-desc">{result.description}</p>

              <div className="result-section">
                <div className="result-section-title">Treatment Steps</div>
                <ol className="treatment-list">
                  {result.treatment.map((t, i) => (
                    <li key={i}>
                      <span className="treatment-num">{i + 1}</span>
                      {t}
                    </li>
                  ))}
                </ol>
              </div>

              <div className="result-section">
                <div className="result-section-title">Prevention</div>
                <div className="prevention-list">
                  {result.prevention.map((p, i) => (
                    <span className="prevention-tag" key={i}>{p}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
