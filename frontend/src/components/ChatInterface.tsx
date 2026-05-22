/**
 * Chat Interface Component
 */
'use client';

import React, { useState, useRef, useEffect } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import ContextPanel from './ContextPanel';
import { StepInfo } from './ThinkingSteps';
import './ChatInterface.css';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ContextItem {
  content: string;
  metadata: Record<string, any>;
  page: string | number;
  source: string;
}

interface ChatInterfaceProps {
  lastIngested?: { source: string; timestamp: number } | null;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ lastIngested }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [context, setContext] = useState<ContextItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [thinkingSteps, setThinkingSteps] = useState<{
    analyse: StepInfo;
    retrieve: StepInfo;
    execute: StepInfo;
    validation: StepInfo;
  } | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, thinkingSteps]);

  // Listen for ingestion success events from the landing panel
  useEffect(() => {
    if (lastIngested) {
      const systemMessage: Message = {
        id: `system-${lastIngested.timestamp}`,
        type: 'assistant',
        content: `Successfully ingested new documents: "${lastIngested.source}". Qdrant vector database updated! You can now ask questions about the new document context.`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, systemMessage]);
    }
  }, [lastIngested]);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setError(null);

    // Initialize thinking steps state
    setThinkingSteps({
      analyse: { status: 'active', message: 'Analyzing question and identifying core topics...' },
      retrieve: { status: 'pending', message: 'Searching Qdrant vector database...' },
      execute: { status: 'pending', message: 'Synthesizing response using Gemini...' },
      validation: { status: 'pending', message: 'Validating response references...' },
    });

    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
      const response = await fetch(`${apiUrl}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API error: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('Streaming response body not available');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let done = false;
      let buffer = '';

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          buffer += decoder.decode(value, { stream: !done });
          
          // Split buffer by SSE newline pairs
          const parts = buffer.split('\n\n');
          // Keep the last part (it might be incomplete)
          buffer = parts.pop() || '';

          for (const part of parts) {
            const lines = part.split('\n');
            for (const line of lines) {
              const trimmed = line.trim();
              if (trimmed.startsWith('data: ')) {
                const jsonStr = trimmed.slice(6).trim();
                if (!jsonStr) continue;
                
                try {
                  const data = JSON.parse(jsonStr);
                  if (data.step === 'done') {
                    // Update assistant message and context
                    const assistantMessage: Message = {
                      id: (Date.now() + 1).toString(),
                      type: 'assistant',
                      content: data.response,
                      timestamp: new Date(),
                    };
                    setMessages(prev => [...prev, assistantMessage]);
                    setContext(data.context || []);
                    setThinkingSteps(null);
                  } else if (data.step === 'error') {
                    throw new Error(data.message || 'Stream processing failed');
                  } else if (data.step) {
                    // Update specific step status
                    setThinkingSteps(prev => {
                      if (!prev) return null;
                      
                      const updated = { ...prev };
                      const stepsOrder: ('analyse' | 'retrieve' | 'execute' | 'validation')[] = [
                        'analyse', 'retrieve', 'execute', 'validation'
                      ];
                      const currentIdx = stepsOrder.indexOf(data.step);
                      
                      // Auto-complete preceding steps
                      if (currentIdx !== -1) {
                        for (let i = 0; i < currentIdx; i++) {
                          const stepKey = stepsOrder[i];
                          if (updated[stepKey].status === 'pending' || updated[stepKey].status === 'active') {
                            updated[stepKey] = {
                              status: 'completed',
                              message: updated[stepKey].message || 'Done.'
                            };
                          }
                        }
                      }

                      updated[data.step as keyof typeof prev] = {
                        status: data.status,
                        message: data.message || prev[data.step as keyof typeof prev].message,
                      };
                      return updated;
                    });
                  }
                } catch (e) {
                  console.error('Error parsing SSE data:', e, jsonStr);
                }
              }
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
      setThinkingSteps(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-container">
        <div className="chat-header">
          <div className="chat-header-info">
            <h3 className="chat-header-title">AnswerDeck Assistant</h3>
            <span className="chat-header-status">
              <span className="status-dot"></span>
              Online
            </span>
          </div>
        </div>

        <MessageList messages={messages} loading={loading} error={error} thinkingSteps={thinkingSteps} />
        <div ref={messagesEndRef} />
        <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
      </div>
      {context.length > 0 && <ContextPanel context={context} />}
    </div>
  );
};

export default ChatInterface;
