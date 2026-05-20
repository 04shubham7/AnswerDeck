/**
 * Main App Component
 */
'use client';

import React from 'react';
import ChatInterface from './components/ChatInterface';
import './App.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>AnswerDeck RAG Chat</h1>
        <p>Semantic Search Powered by AI</p>
      </header>
      <main className="app-main">
        <ChatInterface />
      </main>
    </div>
  );
}

export default App;
