// frontend/src/pages/OcrPage.js
import React, { useState } from 'react';
import { performOcr } from '../services/api';

function OcrPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [extractedText, setExtractedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setExtractedText('');
    setError('');
  };

  const handleOcrSubmit = () => {
    if (!selectedFile) {
      setError('Please select an image file first.');
      return;
    }
    setError('');
    setIsLoading(true);
    setExtractedText('');

    const formData = new FormData();
    formData.append('file', selectedFile);

    performOcr(formData)
      .then(res => {
        setExtractedText(res.data.extracted_text);
      })
      .catch(err => {
        setError(err.response?.data?.detail || 'Failed to perform OCR.');
        console.error("OCR Error:", err);
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  return (
    <div className="page-container" style={{ maxWidth: '700px' }}>
      <h2>Image OCR</h2>
      <p>Upload an image (e.g., PNG, JPG) to extract text using the LLaVA model.</p>
      
      <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '20px' }}>
        <input
          type="file"
          onChange={handleFileChange}
          accept="image/png, image/jpeg, image/webp"
          className="form-input"
          style={{ flexGrow: 1 }}
        />
        <button
          onClick={handleOcrSubmit}
          disabled={isLoading || !selectedFile}
          className="btn btn-primary"
        >
          {isLoading ? 'Processing...' : 'Extract Text'}
        </button>
      </div>

      {error && <p className="status-message status-error">{error}</p>}

      {(extractedText || isLoading) && (
        <div>
          <h3>Extracted Text:</h3>
          <div className="content-box">
            {extractedText}
            {isLoading && <p style={{ color: 'var(--link-color)' }}>Processing image...</p>}
          </div>
        </div>
      )}
    </div>
  );
}

export default OcrPage;