// frontend/src/pages/TrainingPage.js
import React, { useState, useEffect } from "react";
import { getModels, trainCustomModel } from "../services/api";

function TrainingPage() {
  const [models, setModels] = useState([]);
  const [baseModel, setBaseModel] = useState("");
  const [customModelName, setCustomModelName] = useState("");
  const [trainingFile, setTrainingFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState({ message: "", type: "" });

  // Fetch available models
  useEffect(() => {
    getModels()
      .then((res) => {
        const data = Array.isArray(res.data) ? res.data : [];
        setModels(data);
        if (data.length > 0) setBaseModel(data[0].name);
      })
      .catch((err) => console.error("Error fetching models:", err));
  }, []);

  // Handle training file selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const allowedTypes = ["application/pdf", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"];
      if (!allowedTypes.includes(file.type)) {
        alert("Please upload a valid file (PDF, DOCX, XLSX).");
        e.target.value = "";
        return;
      }
      setTrainingFile(file);
    }
  };

  // Handle form submit
  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!baseModel || !customModelName || !trainingFile) {
      setStatus({ message: "Please fill out all fields and select a file.", type: "error" });
      return;
    }

    setIsLoading(true);
    setStatus({ message: "", type: "" });

    try {
      const res = await trainCustomModel(baseModel, customModelName, trainingFile);
      setStatus({
        message: `✅ Successfully trained model '${customModelName}'. Adapter: ${res.data?.adapter_filename || "N/A"}`,
        type: "success",
      });
    } catch (err) {
      console.error(err);
      setStatus({
        message: `❌ Error: ${err.response?.data?.detail || "Training failed. Please try again."}`,
        type: "error",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="page-content" style={{ maxWidth: "700px", margin: "0 auto", textAlign: "center" }}>
      <h2>Custom Model Training</h2>
      <p className="page-description">
        Select a base model, name your new model, and upload a training data file (e.g., PDF, DOCX, XLSX).
      </p>

      <form onSubmit={handleSubmit} className="form-layout">
        <div className="form-group">
          <label htmlFor="base-model" className="form-label">Base Model:</label>
          <select
            id="base-model"
            value={baseModel}
            onChange={(e) => setBaseModel(e.target.value)}
            className="form-input"
          >
            {models.length > 0 ? (
              models.map((model) => (
                <option key={model.name} value={model.name}>
                  {model.name}
                </option>
              ))
            ) : (
              <option disabled>No models found</option>
            )}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="model-name" className="form-label">New Model Name:</label>
          <input
            id="model-name"
            type="text"
            placeholder="e.g., my-custom-model"
            value={customModelName}
            onChange={(e) => setCustomModelName(e.target.value)}
            className="form-input"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="file-upload" className="form-label">Training File:</label>
          <input
            id="file-upload"
            type="file"
            accept=".pdf,.docx,.xlsx"
            onChange={handleFileChange}
            className="form-input"
            required
          />
        </div>

        <button type="submit" disabled={isLoading} className="btn btn-success" style={{ marginTop: "10px" }}>
          {isLoading ? "Training Adapter..." : "Start Training Adapter"}
        </button>
      </form>

      {/* Status feedback */}
      {status.message && (
        <div
          className={`status-message ${status.type === "success" ? "status-success" : "status-error"}`}
          style={{
            marginTop: "15px",
            padding: "10px",
            borderRadius: "6px",
            color: status.type === "success" ? "#00ff99" : "#ff5555",
            fontWeight: 500,
          }}
        >
          {status.message}
        </div>
      )}
    </div>
  );
}

export default TrainingPage;
