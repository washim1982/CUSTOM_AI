// frontend/src/services/api.js
import axios from "axios";

// ✅ Unified API Base
//const API_BASE = process.env.REACT_APP_API_BASE || "/api"; ---for PROD
//const API_BASE = process.env.REACT_APP_API_BASE || "/api"; //---for DEV localhost

const isDev = !process.env.NODE_ENV || process.env.NODE_ENV === "development";

export const API_BASE = isDev
  ? "http://localhost:8001/api" // ✅ backend dev server
  : process.env.REACT_APP_API_BASE || "/api";

// ✅ Axios client for non-stream endpoints
const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

// -------------------- 🧠 CHAT HISTORY --------------------
export const listChats = () => apiClient.get("/chat-history");

export const loadChat = async (chatId) => {
  return apiClient.get(`/chat-history/${chatId}`);
};

export const getChatHistory = async () => {
  return apiClient.get("/chat-history");
};

export const saveChat = async (chatData) => {
  return apiClient.post("/chat-history", chatData);
};

export const deleteChat = async (chatId) => {
  return apiClient.delete(`/chat-history/${chatId}`);
};

// -------------------- 🤖 CHATBOT --------------------
export const askChatbotStream = (question) => {
  return fetch(`${API_BASE}/chatbot/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
};

// -------------------- 🖼️ OCR --------------------
export const performOcr = (formData, mode = "describe") => {
  return apiClient.post(`/ocr/process-image?mode=${mode}`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

// -------------------- 🔐 AUTH --------------------
export const registerUser = (userData) => {
  return apiClient.post("/auth/register", {
    email: userData.email,
    password: userData.password,
  });
};

export const loginUser = (email, password) => {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);
  return apiClient.post("/auth/token", formData, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
};

// -------------------- 🧩 MODEL MANAGEMENT --------------------
export const getModels = async () => {
  return apiClient.get("/models/");
};

export const loadModel = async (modelName, loraName = null) => {
  return apiClient.post("/models/load", {
    model: modelName,
    lora: loraName,
  });
};

// -------------------- 💬 PROMPT STREAM --------------------
export const runPromptStream = async (data, onChunk) => {
  const payload = {
    model_name: data.model,       // ✅ correct key
    prompt_text: data.prompt,     // ✅ correct key
    max_tokens: data.max_tokens,  // ✅ same
  };
  const response = await fetch(`${API_BASE}/models/prompt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok || !response.body) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    const lines = chunk.split("\n").filter((line) => line.trim() !== "");

    for (const line of lines) {
      try {
        const parsed = JSON.parse(line);
        if (parsed.error) throw new Error(parsed.error);
        if (parsed.response) onChunk(parsed.response);
      } catch (err) {
        console.error("Stream parse error:", err, line);
      }
    }
  }
};

// -------------------- 🎚️ LoRA MANAGEMENT --------------------
export const listLoras = async () => {
  return apiClient.get("/loras/");
};

export const uploadLora = (formData) => {
  return apiClient.post("/loras/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const downloadLora = (loraName) => {
  return `${API_BASE}/loras/download/${loraName}`;
};

// -------------------- 🧠 CUSTOM MODEL TRAINING --------------------
export const trainCustomModel = (baseModel, customModelName, trainingFile) => {
  const formData = new FormData();
  formData.append("base_model", baseModel);
  formData.append("custom_model_name", customModelName);
  formData.append("training_file", trainingFile);

  return apiClient.post("/training/create-custom-model", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

// -------------------- 🧩 SQL TRAINING --------------------
export const generateSqlData = (schema, num_examples) => {
  const formData = new FormData();
  formData.append("schema", JSON.stringify(schema));
  formData.append("num_examples", num_examples);

  return apiClient.post("/training/generate-sql-data", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const trainSqlModel = (baseModel, customModelName, qaData) => {
  return apiClient.post(
    "/training/create-sql-model",
    {
      base_model: baseModel,
      custom_model_name: customModelName,
      qa_data: qaData,
    },
    { headers: { "Content-Type": "application/json" } }
  );
};

// -------------------- 📊 EXCEL ANALYSIS --------------------
export const uploadExcel = (formData) => {
  return apiClient.post("/analysis/upload-excel", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const generateChart = (x_axis_col, y_axis_col) => {
  const formData = new FormData();
  formData.append("x_axis_col", x_axis_col);
  formData.append("y_axis_col", y_axis_col);

  return apiClient.post("/analysis/generate-chart", formData, {
    responseType: "blob",
  });
};
