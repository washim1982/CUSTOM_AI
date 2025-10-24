// src/pages/DataAnalysis.js
import React, { useState } from 'react';
import { uploadExcel, generateChart } from '../services/api';

function DataAnalysis() {
  const [file, setFile] = useState(null);
  const [columns, setColumns] = useState([]); // Assume this is populated after upload
  const [chartImage, setChartImage] = useState(null);
  
  const handleFileUpload = async (event) => {
    const uploadedFile = event.target.files[0];
    setFile(uploadedFile);
    // In a real app, you would upload the file and get column names back
  };

  const handleChartGeneration = async () => {
    // Assume user has selected 'Year' and 'Profit Ratio' columns
    const selectedColumns = { xAxis: 'Year', yAxis: 'Profit Ratio' };
    
    try {
        const response = await generateChart(selectedColumns);
        const imageUrl = URL.createObjectURL(response.data);
        setChartImage(imageUrl);
    } catch (error) {
        console.error("Error generating chart:", error);
    }
  };

  return (
    <div>
      <h2>Excel Data Analysis</h2>
      <input type="file" onChange={handleFileUpload} accept=".xlsx, .xls" />
      {/* UI to select columns would go here */}
      <button onClick={handleChartGeneration}>Generate Chart</button>
      {chartImage && <img src={chartImage} alt="Generated Chart" />}
    </div>
  );
}

export default DataAnalysis;
