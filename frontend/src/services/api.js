// frontend/src/services/api.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',  //for dev use http://localhost:8000/api
});

// --- Chatbot ---
export const askChatbotStream = (question) => {
    return fetch('/api/chatbot/ask', { // Use correct backend address for dev use http://localhost:8000/api/chatbot/ask
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // Add Authorization header if needed later
        },
        body: JSON.stringify({ question })
    });
};

// --- OCR ---
export const performOcr = (formData) => {
    return apiClient.post('/ocr/process-image', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
};


// --- Authentication ---
export const registerUser = (userData) => {
  return apiClient.post('/auth/register', {
    email: userData.email,
    password: userData.password,
  });
};

export const loginUser = (email, password) => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  return apiClient.post('/auth/token', formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
};

// --- Model Management ---
export const getModels = () => {
  return apiClient.get('/models/');
};

export const loadModel = (model_name, adapter_name = null) => {
  return apiClient.post('/models/load', { model_name, adapter_name });
};

export const runPromptStream = (model_name, prompt_text) => {
  return fetch('/api/models/prompt/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      // 'Authorization': `Bearer ${localStorage.getItem('token')}` // Add if needed
    },
    body: JSON.stringify({
      model_name,
      prompt_text,
      max_tokens: 512
    })
  });
};

// --- LoRA Management ---
export const listLoras = () => {
  return apiClient.get('/loras/');
};

export const uploadLora = (formData) => {
  return apiClient.post('/loras/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const downloadLora = (lora_name) => {
  return `${apiClient.defaults.baseURL}/loras/download/${lora_name}`;
};

// --- Custom Model/Adapter Training ---
export const trainCustomModel = (base_model, custom_model_name, training_file) => {
  const formData = new FormData();
  formData.append('base_model', base_model);
  formData.append('custom_model_name', custom_model_name);
  formData.append('training_file', training_file);
  return apiClient.post('/training/create-custom-model', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// --- SQL Training Data Generation ---
export const generateSqlData = (schema, num_examples) => {
  const formData = new FormData();
  formData.append('schema', JSON.stringify(schema));
  formData.append('num_examples', num_examples);
  return apiClient.post('/training/generate-sql-data', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// --- SQL Adapter Training ---
// THIS FUNCTION MUST BE AT THE TOP LEVEL
export const trainSqlModel = (base_model, custom_model_name, qa_data) => {
    return apiClient.post('/training/create-sql-model', {
      base_model,
      custom_model_name,
      qa_data
    }, {
      headers: { 'Content-Type': 'application/json' },
    });
};

// --- Excel File Analysis ---
export const uploadExcel = (formData) => {
  return apiClient.post('/analysis/upload-excel', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const generateChart = (x_axis_col, y_axis_col) => {
  const formData = new FormData();
  formData.append('x_axis_col', x_axis_col);
  formData.append('y_axis_col', y_axis_col);
  return apiClient.post('/analysis/generate-chart', formData, {
    responseType: 'blob',
  });
};