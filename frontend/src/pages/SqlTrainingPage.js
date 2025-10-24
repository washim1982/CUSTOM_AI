// frontend/src/pages/SqlTrainingPage.js
import React, { useState, useEffect } from 'react';
import { generateSqlData, getModels, trainSqlModel } from '../services/api';

const placeholderSchema = `{
  "employees": ["employee_id", "first_name", "last_name", "department_id", "salary"],
  "departments": ["department_id", "department_name"]
}`;

function SqlTrainingPage() {
  const [schema, setSchema] = useState(placeholderSchema);
  const [numExamples, setNumExamples] = useState(50);
  const [qaPairs, setQaPairs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [models, setModels] = useState([]);
  const [selectedBaseModel, setSelectedBaseModel] = useState('');
  const [newModelName, setNewModelName] = useState('');
  const [isTraining, setIsTraining] = useState(false);
  const [trainingStatus, setTrainingStatus] = useState({ message: '', type: '' });
  
  useEffect(() => {
    getModels()
      .then(res => {
        setModels(res.data);
        if (res.data.length > 0) {
          setSelectedBaseModel(res.data[0].name);
        }
      })
      .catch(err => console.error("Error fetching models:", err));
  }, []);
  
  const handleSubmit = (event) => {
    event.preventDefault();
    setError('');
    setIsLoading(true);
    setQaPairs([]);
    let parsedSchema;
    try {
      parsedSchema = JSON.parse(schema);
    } catch (e) {
      setError('Invalid JSON format for schema. Please check your syntax.');
      setIsLoading(false);
      return;
    }
    generateSqlData(parsedSchema, numExamples)
      .then(res => {
        setQaPairs(res.data);
      })
      .catch(err => {
        setError(err.response?.data?.detail || 'Failed to generate training data.');
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  const handleTrainModel = (event) => {
    event.preventDefault();
    if (!selectedBaseModel || !newModelName || qaPairs.length === 0) {
      alert("Please select a base model, provide a name for the new model, and generate data first.");
      return;
    }
    setIsTraining(true);
    setTrainingStatus({ message: '', type: '' });

    trainSqlModel(selectedBaseModel, newModelName, qaPairs)
      .then(res => {
        setTrainingStatus({ message: `Successfully simulated training. SQL Adapter file: '${res.data.adapter_filename}'`, type: 'success' });
      })
      .catch(err => {
        setTrainingStatus({ message: `Error: ${err.response?.data?.detail || 'Failed to start training.'}`, type: 'error' });
      })
      .finally(() => {
        setIsTraining(false);
      });
  };
  
  return (
    <div className="page-container">
      <h2>SQL Training Data Generation</h2>
      <p>Provide a database schema as a JSON object to generate synthetic question-answer pairs for training a SQL model.</p>
      
      <form onSubmit={handleSubmit} className="form-layout">
        <div className="form-group">
          <label htmlFor="schema-input" className="form-label">Database Schema (JSON format):</label>
          <textarea
            id="schema-input"
            value={schema}
            onChange={(e) => setSchema(e.target.value)}
            className="form-input textarea"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="num-examples-input" className="form-label">Number of Examples:</label>
          <input
            id="num-examples-input"
            type="number"
            value={numExamples}
            onChange={(e) => setNumExamples(parseInt(e.target.value, 10))}
            min="1"
            max="1000"
            className="form-input"
          />
        </div>
        
        <button type="submit" disabled={isLoading} className="btn btn-primary">
          {isLoading ? 'Generating...' : 'Generate Training Data'}
        </button>
      </form>

      {error && <p className="status-message status-error">{error}</p>}

      {qaPairs.length > 0 && (
        <>
          <h3>Generated Data:</h3>
          <div className="content-box" style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {qaPairs.map((pair, index) => (
              <div key={index} style={{ padding: '10px', borderBottom: '1px solid var(--box-border)' }}>
                <p style={{ fontWeight: 'bold' }}>Q: {pair.question}</p>
                <p style={{ fontFamily: 'monospace', color: 'var(--link-color)', marginTop: '5px' }}>A: {pair.answer}</p>
              </div>
            ))}
          </div>

          <div style={{ marginTop: '30px' }}>
             <h3 style={{ borderBottom: '1px solid var(--box-border)', paddingBottom: '10px' }}>Train Custom SQL Model</h3>
             <p>Select a base model and provide a name to create a new model customized with the generated SQL data.</p>
             <form onSubmit={handleTrainModel} className="form-layout">
                <div className="form-group">
                  <label htmlFor="base-model-select" className="form-label">Select Base Model:</label>
                  <select
                     id="base-model-select"
                     value={selectedBaseModel}
                     onChange={(e) => setSelectedBaseModel(e.target.value)}
                     className="form-input"
                  >
                     {models.map(model => (
                         <option key={model.name} value={model.name}>{model.name}</option>
                     ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="new-model-name-input" className="form-label">New Model Name:</label>
                  <input
                     id="new-model-name-input"
                     type="text"
                     placeholder="e.g., my-sql-model"
                     value={newModelName}
                     onChange={(e) => setNewModelName(e.target.value)}
                     className="form-input"
                  />
                </div>
                
                <button type="submit" disabled={isTraining} className="btn btn-success">
                  {isTraining ? 'Training Adapter...' : 'Train SQL Adapter'}
                </button>
             </form>
             {trainingStatus.message && (
                 <div className={`status-message ${trainingStatus.type === 'success' ? 'status-success' : 'status-error'}`}>
                     {trainingStatus.message}
                 </div>
             )}
            </div>
        </>
      )}
    </div>
  );
}

export default SqlTrainingPage;