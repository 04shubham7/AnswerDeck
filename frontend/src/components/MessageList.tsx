/**
 * Message List Component
 */
'use client';

import React from 'react';
import Message from './Message';
import './MessageList.css';

interface MessageItem {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface MessageListProps {
  messages: MessageItem[];
  loading: boolean;
  error: string | null;
}

const MessageList: React.FC<MessageListProps> = ({ messages, loading, error }) => {
  return (
    <div className="message-list">
      {messages.length === 0 ? (
        <div className="empty-state">
          <h2>Welcome to AnswerDeck</h2>
          <p>Ask me anything about the documentation</p>
        </div>
      ) : (
        messages.map(msg => <Message key={msg.id} message={msg} />)
      )}
      {error && <div className="error-message">{error}</div>}
      {loading && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>Thinking...</p>
        </div>
      )}
    </div>
  );
};

export default MessageList;
