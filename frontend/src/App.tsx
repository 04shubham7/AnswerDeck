import React, { useState } from 'react';
import LandingPanel from './components/LandingPanel';
import ChatInterface from './components/ChatInterface';
import './App.css';

interface IngestionUpdate {
  source: string;
  timestamp: number;
}

function App() {
  const [lastIngested, setLastIngested] = useState<IngestionUpdate | null>(null);

  const handleIngestSuccess = (source: string) => {
    setLastIngested({
      source,
      timestamp: Date.now(),
    });
  };

  return (
    <div className="app">
      {/* Visual background gradient glowing blobs */}
      <div className="bg-blobs">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
        <div className="blob blob-3"></div>
      </div>
      
      <main className="app-main">
        <div className="left-panel-container">
          <LandingPanel onIngestSuccess={handleIngestSuccess} />
        </div>
        <div className="right-panel-container">
          <ChatInterface lastIngested={lastIngested} />
        </div>
      </main>
    </div>
  );
}

export default App;

