/**
 * Context Panel Component
 */
'use client';

import React from 'react';
import './ContextPanel.css';

interface ContextItem {
  content: string;
  metadata: Record<string, any>;
  page: string | number;
  source: string;
}

interface ContextPanelProps {
  context: ContextItem[];
}

const ContextPanel: React.FC<ContextPanelProps> = ({ context }) => {
  return (
    <div className="context-panel">
      <h3>📚 Retrieved Context</h3>
      <div className="context-list">
        {context.map((item, idx) => (
          <div key={idx} className="context-item">
            <div className="context-header">
              <span className="source-badge">{item.source}</span>
              <span className="page-badge">Page {item.page}</span>
            </div>
            <p className="context-content">{item.content.substring(0, 150)}...</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ContextPanel;
