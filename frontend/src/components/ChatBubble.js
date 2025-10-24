// frontend/src/components/ChatBubble.js
import React from 'react';

function ChatBubble({ onClick }) {
  return (
    <div className="chat-bubble" onClick={onClick} title="Ask Chatbot">
      {/* CHANGED: Replaced icon */}
      🤖
    </div>
  );
}

export default ChatBubble;