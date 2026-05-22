/**
 * Message List Component
 */
'use client';

import React from 'react';
import Message from './Message';
import ThinkingSteps, { StepInfo } from './ThinkingSteps';
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
  thinkingSteps?: {
    analyse: StepInfo;
    retrieve: StepInfo;
    execute: StepInfo;
    validation: StepInfo;
  } | null;
}

const MessageList: React.FC<MessageListProps> = ({ messages, loading, error, thinkingSteps = null }) => {
  return (
    <div className="message-list">
      {messages.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </div>
          <h2>Welcome to AnswerDeck</h2>
          <p>Select a PDF upload method or connect your AWS S3 bucket on the left control deck, then query document context here.</p>
        </div>
      ) : (
        messages.map(msg => <Message key={msg.id} message={msg} />)
      )}
      {error && <div className="error-message">{error}</div>}
      {loading && (
        <div className="loading-indicator-container">
          {thinkingSteps ? (
            <ThinkingSteps steps={thinkingSteps} />
          ) : (
            <div className="loading-indicator">
              <div className="spinner"></div>
              <p>Thinking...</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MessageList;
