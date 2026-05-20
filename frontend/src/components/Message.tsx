/**
 * Message Component
 */
'use client';

import React from 'react';
import './Message.css';

interface MessageProps {
  message: {
    id: string;
    type: 'user' | 'assistant';
    content: string;
    timestamp: Date;
  };
}

const Message: React.FC<MessageProps> = ({ message }) => {
  return (
    <div className={`message message-${message.type}`}>
      <div className="message-avatar">
        {message.type === 'user' ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        <p>{message.content}</p>
        <span className="message-time">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
};

export default Message;
