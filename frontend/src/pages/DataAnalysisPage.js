// frontend/src/pages/DataAnalysisPage.js
import React, { useState } from 'react';
import { uploadExcel, generateChart } from '../services/api';

function DataAnalysisPage() {
  const [file, setFile] = useState(null);
  const [excelData, setExcelData] = useState(null);
  const [xAxis, setXAxis] = useState('');
  const [yAxis, setYAxis] = useState('');
  const [chartImage, setChartImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setExcelData(null);
    setChartImage(null);
    setError('');
  };

  const handleFileUpload = () => {
    if (!file) {
      setError('Please select a file first.');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    
    setIsLoading(true);
    uploadExcel(formData)
      .then(res => {
        setExcelData(res.data);
        if (res.data.columns.length >= 2) {
          setXAxis(res.data.columns[0]);
          setYAxis(res.data.columns[1]);
        }
      })
      .catch(err => setError('Failed to upload or parse Excel file.'))
      .finally(() => setIsLoading(false));
  };

  const handleChartGeneration = () => {
    if (!xAxis || !yAxis) {
      setError('Please select both an X and a Y axis.');
      return;
    }
    setIsLoading(true);
    setError('');
    generateChart(xAxis, yAxis)
      .then(res => {
        const imageUrl = URL.createObjectURL(res.data);
        setChartImage(imageUrl);
      })
      .catch(err => setError('Failed to generate chart.'))
      .finally(() => setIsLoading(false));
  };

  return (
    <div className="page-container">
      <h2>Excel Upload & Charting</h2>
      
      <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '20px' }}>
        <input type="file" onChange={handleFileChange} accept=".xlsx, .xls" className="form-input" style={{ flexGrow: 1 }} />
        <button onClick={handleFileUpload} disabled={isLoading || !file} className="btn btn-primary">
          {isLoading ? 'Uploading...' : 'Upload and Display'}
        </button>
      </div>

      {error && <p className="status-message status-error">{error}</p>}
      
      {excelData && (
        <>
          <h3>Data Preview</h3>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  {excelData.columns.map(col => <th key={col}>{col}</th>)}
                </tr>
              </thead>
              <tbody>
                {excelData.data.map((row, index) => (
                  <tr key={index}>
                    {excelData.columns.map(col => <td key={col}>{row[col]}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ margin: '20px 0', display: 'flex', gap: '10px', alignItems: 'center' }}>
            <label htmlFor="x-axis" className="form-label">X-Axis:</label>
            <select id="x-axis" value={xAxis} onChange={(e) => setXAxis(e.target.value)} className="form-input">
              {excelData.columns.map(col => <option key={col} value={col}>{col}</option>)}
            </select>
            <label htmlFor="y-axis" className="form-label">Y-Axis:</label>
            <select id="y-axis" value={yAxis} onChange={(e) => setYAxis(e.target.value)} className="form-input">
              {excelData.columns.map(col => <option key={col} value={col}>{col}</option>)}
            </select>
            <button onClick={handleChartGeneration} disabled={isLoading} className="btn btn-primary">Generate Chart</button>
          </div>
        </>
      )}

      {chartImage && (
        <div>
          <h3>Generated Chart</h3>
          <img src={chartImage} alt="Generated chart from Excel data" style={{ border: '1px solid var(--box-border)', borderRadius: '4px', maxWidth: '100%' }} />
        </div>
      )}
    </div>
  );
}

export default DataAnalysisPage;