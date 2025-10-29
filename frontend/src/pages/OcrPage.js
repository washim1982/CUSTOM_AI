// frontend/src/pages/OcrPage.js
import React, { useState } from "react";
import { performOcr } from "../services/api";

function OcrPage() {
  const [file, setFile] = useState(null);
  const [mode, setMode] = useState("ocr"); // "ocr" or "describe"
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState("");

  const handleOcr = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setResult("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      // 👇 Pass selected mode to backend
      const response = await performOcr(formData, mode);
      setResult(response.data.extracted_text);
    } catch (error) {
      console.error("OCR error:", error);
      setResult("❌ Failed to process image.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "40px auto", textAlign: "center" }}>
      <h2>Image OCR / Description</h2>

      <form onSubmit={handleOcr}>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files[0])}
          style={{ marginBottom: "12px" }}
        />

        <div style={{ marginBottom: "12px" }}>
          <label htmlFor="ocrMode" style={{ marginRight: "8px" }}>
            Mode:
          </label>
          <select
            id="ocrMode"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
            style={{ padding: "6px 12px" }}
          >
            <option value="ocr">Extract Text Only</option>
            <option value="describe">Detailed Description</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={!file || loading}
          style={{
            padding: "10px 20px",
            background: "#007bff",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          {loading ? "Processing..." : "Upload & Process"}
        </button>
      </form>

      {/* Display the result */}
      <div
        style={{ marginTop: "20px", textAlign: "left", whiteSpace: "pre-wrap" }}
      >
        {loading && <p>Processing image ({mode} mode)...</p>}
        {!loading && result && (
          <>
            <h3>
              Result ({mode === "ocr" ? "Extracted Text" : "Description"}):
            </h3>
            <p>{result}</p>
          </>
        )}
      </div>
    </div>
  );
}

export default OcrPage;
