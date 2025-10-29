// frontend/src/pages/ModelManagementPage.js
import React, { useState, useEffect, useRef } from "react";
import {
  getModels,
  listLoras,
  loadModel,
  runPromptStream,
  saveChat,
} from "../services/api";
import { FiCpu, FiSend, FiLoader } from "react-icons/fi";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import remarkGfm from "remark-gfm";
import "./ModelManagementPage.css";

/* -------------------------------
   🧠 Modal: Model + LoRA Selection
--------------------------------- */
const ModelSelectionModal = ({ onClose, onSelect, models, loras }) => {
  const [localModel, setLocalModel] = useState("");
  const [localLora, setLocalLora] = useState("");

  const handleLoad = () => {
    if (!localModel) {
      alert("Please select a base model before proceeding.");
      return;
    }
    onSelect(localModel, localLora);
    onClose();
  };

  return (
    <div className="model-modal-backdrop" onClick={onClose}>
      <div className="model-modal-content" onClick={(e) => e.stopPropagation()}>
        <h3>Load Model & Adapter</h3>

        <label>Select Base Model</label>
        <select
          value={localModel}
          onChange={(e) => setLocalModel(e.target.value)}
        >
          <option value="">-- Select Base Model --</option>
          {models.map((model) => (
            <option key={model.name} value={model.name}>
              {model.name}
            </option>
          ))}
        </select>

        <label>Select LoRA Adapter</label>
        <select
          value={localLora}
          onChange={(e) => setLocalLora(e.target.value)}
        >
          <option value="">-- No LoRA Adapter --</option>
          {loras.map((lora) => (
            <option key={lora.name} value={lora.name}>
              {lora.name}
            </option>
          ))}
        </select>

        <button onClick={handleLoad}>Load Selection</button>
      </div>
    </div>
  );
};

/* -------------------------------
   💬 Main Page: Model Management
--------------------------------- */
const ModelManagementPage = () => {
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState("");
  const [models, setModels] = useState([]);
  const [loras, setLoras] = useState([]);
  const [loadedModel, setLoadedModel] = useState("granite4:tiny-h");
  const [isLoading, setIsLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentChatId] = useState(null); // ✅ defined
  const outputAreaRef = useRef(null);

  // === Fetch Models and LoRAs ===
  useEffect(() => {
    const fetchData = async () => {
      try {
        const modelRes = await getModels();
        setModels(modelRes.data || []);
      } catch (err) {
        console.error("Failed to fetch models:", err);
        setModels([]);
      }

      try {
        const loraRes = await listLoras();
        setLoras(loraRes.map((name) => ({ name })));
      } catch (err) {
        console.error("Failed to fetch LoRAs:", err);
      }

      // Initial welcome message
      setMessages((prev) =>
        prev.length === 0
          ? [{ sender: "model", text: "Welcome! to Model Hub" }]
          : prev
      );
    };
    fetchData();
  }, []);

  // === Auto-scroll messages ===
  useEffect(() => {
    if (outputAreaRef.current) {
      outputAreaRef.current.scrollTop = outputAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // === Load Model / LoRA ===
  const handleLoadSelection = async (modelName, loraName) => {
    if (!modelName) {
      alert("Please select a base model.");
      return;
    }

    setIsLoading(true);
    setMessages((prev) => [
      ...prev,
      { sender: "model", text: `Loading ${modelName}...` },
    ]);

    try {
      await loadModel(modelName, loraName || null);
      setLoadedModel(modelName);
      setMessages((prev) => [
        ...prev,
        { sender: "model", text: `✅ Successfully loaded ${modelName}!` },
      ]);
    } catch (err) {
      console.error("Failed to load model:", err);
      setMessages((prev) => [
        ...prev,
        { sender: "model", text: `❌ Error: Failed to load ${modelName}.` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // === Run Prompt ===
  const handleRunPrompt = async (e) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;

    if (!loadedModel) {
      alert("Please load a model first using the 🧠 icon.");
      return;
    }

    const userMessage = { sender: "user", text: prompt };
    const modelMessage = { sender: "model", text: "" };
    setMessages((prev) => [...prev, userMessage, modelMessage]);
    setPrompt("");
    setIsLoading(true);

    // Save chat
    const chatToSave = {
      id: currentChatId,
      title: messages[1]?.text?.slice(0, 30) || "New Chat",
      messages,
    };
    try {
      await saveChat(chatToSave);
    } catch (err) {
      console.warn("Could not save chat:", err);
    }

    // Stream response
    let accumulatedText = "";
    try {
      await runPromptStream(
        { model: loadedModel, prompt: userMessage.text },
        (chunk) => {
          accumulatedText += chunk;
          setMessages((prevMessages) => {
            const updated = [...prevMessages];
            const lastIndex = updated.length - 1;
            if (lastIndex >= 0 && updated[lastIndex].sender === "model") {
              updated[lastIndex].text = accumulatedText.trim();
            }
            return updated;
          });
        }
      );
    } catch (err) {
      console.error("Error running prompt stream:", err);
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { sender: "model", text: "❌ Error: Could not get a response." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  /* -------------------------------
     🖼️ Render
  --------------------------------- */
  return (
    <div className="chat-page-container">
      {/* Chat Output */}
      <div className="chat-output-area" ref={outputAreaRef}>
        {messages.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.sender}`}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || "");
                  const codeText = String(children).replace(/\n$/, "");
                  return inline ? (
                    <code className="inline-code" {...props}>
                      {children}
                    </code>
                  ) : (
                    <div className="code-block-container">
                      <button
                        className="copy-button"
                        onClick={() => navigator.clipboard.writeText(codeText)}
                      >
                        📋 Copy
                      </button>
                      <SyntaxHighlighter
                        style={oneDark}
                        language={match ? match[1] : "python"}
                        PreTag="div"
                        {...props}
                      >
                        {codeText}
                      </SyntaxHighlighter>
                    </div>
                  );
                },
              }}
            >
              {msg.text}
            </ReactMarkdown>
          </div>
        ))}
        {isLoading && (
          <div className="chat-message model">
            <FiLoader className="loading-spinner" />
          </div>
        )}
      </div>

      {/* Prompt Bar */}
      <div className="prompt-footer">
        <div className="model-warning">
           Imaginarium AI can make mistakes. Double-check important information.
        </div>
        <form className="prompt-bar-container" onSubmit={handleRunPrompt}>
          <button
            type="button"
            className="prompt-bar-icon-button"
            onClick={() => setIsModalOpen(true)}
            title="Change Model"
          >
            <FiCpu />
          </button>

          <input
            type="text"
            placeholder="Enter your prompt here..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isLoading}
          />

          <button
            type="submit"
            className="prompt-bar-icon-button"
            disabled={isLoading}
            title="Run Prompt"
          >
            <FiSend />
          </button>
        </form>

        
      </div>

      {/* Modal */}
      {isModalOpen && (
        <ModelSelectionModal
          models={models}
          loras={loras}
          onClose={() => setIsModalOpen(false)}
          onSelect={handleLoadSelection}
        />
      )}
    </div>
  );
};

export default ModelManagementPage;
