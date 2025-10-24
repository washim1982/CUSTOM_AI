// frontend/src/components/ChatWindow.js
import React, { useState, useRef, useEffect } from 'react';
import { askChatbotStream } from '../services/api';

function ChatWindow({ onClose }) {
  const [messages, setMessages] = useState([{ sender: 'bot', text: 'Hi! Ask me about this application.' }]); // Initial greeting
  const [currentInput, setCurrentInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatHistoryRef = useRef(null);

  // Scroll to bottom effect
  useEffect(() => {
    if (chatHistoryRef.current) {
        chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [messages]);

  // handleSendMessage function
  const handleSendMessage = async () => {
    const userQuestion = currentInput.trim();
    if (!userQuestion || isLoading) return;
    setMessages(prev => [...prev, { sender: 'user', text: userQuestion }]);
    setCurrentInput('');
    setIsLoading(true);
    setMessages(prev => [...prev, { sender: 'bot', text: '' }]); // Placeholder

    try {
        const response = await askChatbotStream(userQuestion);
        if (!response.ok || !response.body) throw new Error(`HTTP error! status: ${response.status}`);
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let accumulatedResponse = '';
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n').filter(line => line.trim() !== '');
            for (const line of lines) {
                try {
                    const data = JSON.parse(line);
                    if (data.error) throw new Error(data.error);
                    accumulatedResponse += data.response;
                    setMessages(prev => {
                        const updated = [...prev];
                        updated[updated.length - 1] = { sender: 'bot', text: accumulatedResponse };
                        return updated;
                    });
                } catch (e) { console.error("Stream parse error:", e, line); }
            }
        }
    } catch (error) {
        console.error("Chatbot Error:", error);
         setMessages(prev => {
            const updated = [...prev];
            updated[updated.length - 1] = { sender: 'bot', text: `Error: ${error.message}` };
            return updated;
        });
    } finally {
        setIsLoading(false);
    }
  };

  // handleKeyPress
   const handleKeyPress = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSendMessage();
        }
    };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <span>Application Chatbot</span>
        <button onClick={onClose} className="chat-close-button">×</button>
      </div>
      <div className="chat-history" ref={chatHistoryRef}>
        {messages.map((msg, index) => (
           <div 
             key={index} 
             className="chat-message-container"
             style={{ justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start' }}
           >
               <div className={`chat-message ${msg.sender === 'user' ? 'user-message' : 'bot-message'}`}>
                    {msg.text || (msg.sender === 'bot' && isLoading && index === messages.length - 1 ? '...' : '')}
               </div>
          </div>
        ))}
      </div>
      <div className="chat-input-area">
        <input
          type="text"
          value={currentInput}
          onChange={(e) => setCurrentInput(e.target.value)} // <-- THIS IS THE FIX
          onKeyPress={handleKeyPress}
          placeholder="Ask something..."
          disabled={isLoading}
        />
        <button onClick={handleSendMessage} disabled={isLoading}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;