// frontend/src/pages/ModelManagementPage.js
import React, { useState, useEffect } from 'react';
import { getModels, loadModel, runPromptStream, listLoras } from '../services/api';

function ModelManagementPage() {
  const [models, setModels] = useState([]);
  const [loras, setLoras] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedLora, setSelectedLora] = useState('');
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingModel, setIsLoadingModel] = useState(false);
  const [loadedModelName, setLoadedModelName] = useState('');

  useEffect(() => {
    getModels()
        .then(res => setModels(res.data))
        .catch(err => console.error("Error fetching models:", err));
  }, []);

  useEffect(() => {
    listLoras()
        .then(res => setLoras(res.data))
        .catch(err => console.error("Error fetching LoRAs:", err));
  }, []);

  const handleLoadCombination = () => {
    if (!selectedModel) {
      alert("Please select a base model.");
      return;
    }
    setIsLoadingModel(true);
    setResponse('');
    setLoadedModelName('');

    loadModel(selectedModel, selectedLora || null)
      .then(res => {
        setLoadedModelName(res.data.loaded);
      })
      .catch(err => {
        setResponse(`Error: ${err.response?.data?.detail || 'Could not load model/adapter.'}`);
      })
      .finally(() => {
        setIsLoadingModel(false);
      });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!loadedModelName) {
      alert("Please load a model (and optional adapter) first.");
      return;
    }
    if (!prompt) {
      alert("Please enter a prompt.");
      return;
    }
    
    setIsLoading(true);
    setResponse('');
    
    try {
      const res = await runPromptStream(loadedModelName, prompt);
      if (!res.body) throw new Error("Response body is empty.");
      
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        try {
          const lines = chunk.split('\n').filter(line => line.trim() !== '');
          for (const line of lines) {
            const data = JSON.parse(line);
            if (data.error) throw new Error(data.error);
            setResponse(prev => prev + data.response);
          }
        } catch (e) {
          console.error("Error parsing stream chunk:", e, chunk);
        }
      }
    } catch (err) {
      console.error("Error running prompt:", err);
      setResponse(`Error: ${err.message || "Could not get a response from the model."}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="page-container">
      <h2>Model Management & Prompting</h2>
      
      <div style={{ display: 'flex', gap: '15px', marginBottom: '15px', alignItems: 'center' }}>
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="form-input"
          style={{ flexGrow: 1 }}
          disabled={isLoadingModel}
        >
          <option value="" disabled>-- Select Base Model --</option>
          {models.map(model => (
            <option key={model.name} value={model.name}>{model.name}</option>
          ))}
        </select>

        <select
          value={selectedLora}
          onChange={(e) => setSelectedLora(e.target.value)}
          className="form-input"
          style={{ flexGrow: 1 }}
          disabled={isLoadingModel}
        >
          <option value="">-- No LoRA Adapter --</option>
          {loras.map(lora => (
            <option key={lora} value={lora}>{lora}</option>
          ))}
        </select>

        <button onClick={handleLoadCombination} disabled={isLoadingModel || !selectedModel} className="btn btn-primary">
          {isLoadingModel ? 'Loading...' : 'Load Selection'}
        </button>
      </div>
      
      {loadedModelName && <p>Currently loaded: <strong>{loadedModelName}</strong></p>}

      <form onSubmit={handleSubmit} className="form-layout">
        <textarea
          placeholder="Enter your prompt here..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="form-input textarea"
          style={{ fontFamily: 'sans-serif' }} /* Override monospace */
          disabled={!loadedModelName}
        />
        <button type="submit" disabled={isLoading || isLoadingModel || !loadedModelName} className="btn btn-primary">
          {isLoading ? 'Generating...' : 'Run Prompt'}
        </button>
      </form>

      { (response || isLoading) && (
        <div>
          <h3>Model Response:</h3>
          <div className="content-box">
            {response}
            {isLoading && <span style={{ color: 'var(--link-color)', fontWeight: 'bold' }}>...</span>}
          </div>
        </div>
      )}
    </div>
  );
}

export default ModelManagementPage;