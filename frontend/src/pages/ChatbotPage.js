// frontend/src/pages/ChatbotPage.js
import React, { useState, useRef, useEffect } from 'react';
import { askChatbotStream } from '../services/api';

// Basic inline styles
const styles = {
    container: { maxWidth: '800px', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 100px)' }, // Adjust height as needed
    chatHistory: {
        flexGrow: 1,
        overflowY: 'auto',
        border: '1px solid #ccc',
        padding: '15px',
        marginBottom: '15px',
        borderRadius: '8px',
        background: '#f9f9f9'
    },
    message: { marginBottom: '10px', padding: '8px 12px', borderRadius: '15px', maxWidth: '80%' },
    userMessage: { background: '#007bff', color: 'white', alignSelf: 'flex-end', marginLeft: '20%' },
    botMessage: { background: '#e9ecef', color: '#333', alignSelf: 'flex-start', marginRight: '20%' },
    inputArea: { display: 'flex', gap: '10px' },
    input: { flexGrow: 1, padding: '10px', fontSize: '1rem', border: '1px solid #ccc', borderRadius: '4px' },
    button: { padding: '10px 15px', fontSize: '1rem', cursor: 'pointer', background: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }
};

function ChatbotPage() {
    const [messages, setMessages] = useState([]); // Stores { sender: 'user'/'bot', text: '...' }
    const [currentInput, setCurrentInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const chatHistoryRef = useRef(null); // Ref to scroll chat history

    // Scroll to bottom when messages change
    useEffect(() => {
        if (chatHistoryRef.current) {
            chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSendMessage = async () => {
        const userQuestion = currentInput.trim();
        if (!userQuestion || isLoading) return;

        // Add user message to history
        setMessages(prev => [...prev, { sender: 'user', text: userQuestion }]);
        setCurrentInput('');
        setIsLoading(true);

        // Add a placeholder for bot response
        setMessages(prev => [...prev, { sender: 'bot', text: '' }]);

        try {
            const response = await askChatbotStream(userQuestion);

            if (!response.ok || !response.body) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let accumulatedResponse = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                // Parse potentially multiple JSON objects in a chunk
                const lines = chunk.split('\n').filter(line => line.trim() !== '');
                for (const line of lines) {
                    try {
                        const data = JSON.parse(line);
                        if (data.error) {
                            throw new Error(data.error);
                        }
                        accumulatedResponse += data.response;
                        // Update the last message (the bot's placeholder)
                        setMessages(prev => {
                            const updatedMessages = [...prev];
                            updatedMessages[updatedMessages.length - 1] = { sender: 'bot', text: accumulatedResponse };
                            return updatedMessages;
                        });
                    } catch (e) {
                        console.error("Error parsing stream chunk:", e, line);
                        // Handle potential partial JSON objects if needed
                    }
                }
            }
        } catch (error) {
            console.error("Chatbot Error:", error);
            // Update the bot placeholder with an error message
             setMessages(prev => {
                const updatedMessages = [...prev];
                updatedMessages[updatedMessages.length - 1] = { sender: 'bot', text: `Error: ${error.message}` };
                return updatedMessages;
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Prevent newline in input
            handleSendMessage();
        }
    };


    return (
        <div style={styles.container}>
            <h2>Application Chatbot</h2>
            <p>Ask questions about the features and functionality of this application.</p>

            <div style={styles.chatHistory} ref={chatHistoryRef}>
                {messages.map((msg, index) => (
                    <div key={index} style={{ display: 'flex', justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start' }}>
                         <div style={{
                            ...styles.message,
                            ...(msg.sender === 'user' ? styles.userMessage : styles.botMessage)
                         }}>
                            {msg.text || (msg.sender === 'bot' && isLoading && index === messages.length - 1 ? '...' : '')} {/* Show loading dots */}
                         </div>
                    </div>
                ))}
            </div>

            <div style={styles.inputArea}>
                <input
                    type="text"
                    value={currentInput}
                    onChange={(e) => setCurrentInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask something about the app..."
                    style={styles.input}
                    disabled={isLoading}
                />
                <button onClick={handleSendMessage} disabled={isLoading} style={styles.button}>
                    Send
                </button>
            </div>
        </div>
    );
}

export default ChatbotPage;