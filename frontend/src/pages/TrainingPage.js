// frontend/src/pages/TrainingPage.js
import React, { useState, useEffect } from 'react';
import { getModels, trainCustomModel } from '../services/api';

function TrainingPage() {
  const [models, setModels] = useState([]);
  const [baseModel, setBaseModel] = useState('');
  const [customModelName, setCustomModelName] = useState('');
  const [trainingFile, setTrainingFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState({ message: '', type: '' });

  useEffect(() => {
    getModels()
      .then(res => {
        setModels(res.data);
        if (res.data.length > 0) {
          setBaseModel(res.data[0].name);
        }
      })
      .catch(err => console.error("Error fetching models:", err));
  }, []);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!baseModel || !customModelName || !trainingFile) {
      alert("Please fill out all fields and select a file.");
      return;
    }

    setIsLoading(true);
    setStatus({ message: '', type: '' });

    trainCustomModel(baseModel, customModelName, trainingFile)
      .then(res => {
        setStatus({ message: `Successfully simulated training. Adapter file: '${res.data.adapter_filename}'`, type: 'success' });
      })
      .catch(err => {
        setStatus({ message: `Error: ${err.response?.data?.detail || 'Failed to start training.'}`, type: 'error' });
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  return (
    <div className="page-container" style={{ maxWidth: '600px' }}>
      <h2>Custom Model Training</h2>
      <p>Select a base model, name your new model, and upload a training data file (e.g., PDF, DOCX, XLSX).</p>
      
      <form onSubmit={handleSubmit} className="form-layout">
        <div className="form-group">
          <label htmlFor="base-model" className="form-label">Base Model:</label>
          <select id="base-model" value={baseModel} onChange={(e) => setBaseModel(e.target.value)} className="form-input">
            {models.map(model => (
              <option key={model.name} value={model.name}>{model.name}</option>
            ))}
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
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="file-upload" className="form-label">Training File:</label>
          <input
            id="file-upload"
            type="file"
            onChange={(e) => setTrainingFile(e.target.files[0])}
            className="form-input"
          />
        </div>
        
        <button type="submit" disabled={isLoading} className="btn btn-success">
           {isLoading ? 'Training Adapter...' : 'Start Training Adapter'}
       </button>
      </form>

      {status.message && (
        <div className={`status-message ${status.type === 'success' ? 'status-success' : 'status-error'}`}>
          {status.message}
        </div>
      )}
    </div>
  );
}

export default TrainingPage;