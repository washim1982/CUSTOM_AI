// frontend/src/pages/ModelManagementPage.js
import React, { useState, useEffect, useRef } from "react";
import { getModels, loadModel, runPromptStream } from "../services/api";
import { FiCpu, FiSend, FiLoader } from "react-icons/fi";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./ModelManagementPage.css";
import { useAuth0 } from "@auth0/auth0-react";


const ModelManagementPage = () => {
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState("");
  //const [models, setModels] = useState([]);
  const [loadedModel, setLoadedModel] = useState("granite4:tiny-h");
  const [isLoading, setIsLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const outputRef = useRef(null);
  const [models, setModels] = useState([{ name: "minimax:m2 (cloud)" }]);

  

  const { isAuthenticated } = useAuth0();

  useEffect(() => {
  if (isAuthenticated) {
    setLoadedModel("minimax:m2");
  } else {
    setLoadedModel("granite4:tiny-h");
  }
}, [isAuthenticated]);


  // useEffect(() => {
  //   (async () => {
  //     try {
  //       const modelRes = await getModels();
  //       setModels(modelRes.data || []);
  //       setMessages([{ sender: "model", text: "Welcome to Model Hub" }]);
  //     } catch (err) {
  //       console.error("Error loading models:", err);
  //     }
  //   })();
  // }, []);

   useEffect(() => {
  (async () => {
    try {
      const res = await getModels();
      const combined = [{ name: "minimax:m2 (cloud)" }, ...(res.data || [])];
      setModels(combined);
    } catch (err) {
      console.error("Failed to load models:", err);
    }
  })();
}, []);


  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [messages]);

  const handleRunPrompt = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    const userMessage = { sender: "user", text: prompt };
    const modelMessage = { sender: "model", text: "" };
    setMessages((prev) => [...prev, userMessage, modelMessage]);
    setPrompt("");
    setIsLoading(true);

    try {
      await runPromptStream(
        { model: loadedModel, prompt: userMessage.text },
        (chunk) => {
          setMessages((prevMessages) => {
            const updated = [...prevMessages];
            updated[updated.length - 1].text += chunk;
            return updated;
          });
        }
      );
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { sender: "model", text: "❌ Error: Could not get a response." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-page-container">
      <div className="chat-output-area" ref={outputRef}>
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message ${msg.sender} ${msg.model?.includes("minimax") ? "minimax" : ""}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
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

      {/* Prompt Footer */}
      <div className="prompt-footer">
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

        <div className="model-warning">
           Model Hub can make mistakes. Double-check important information.
        </div>
      </div>
    </div>
  );
};

export default ModelManagementPage;
