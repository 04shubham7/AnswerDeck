/**
 * ThinkingSteps Component
 * Displays real-time status of different levels of LLM thinking.
 */
import React from 'react';
import './ThinkingSteps.css';

export interface StepInfo {
  status: 'pending' | 'active' | 'completed' | 'failed';
  message: string;
}

export interface ThinkingStepsProps {
  steps: {
    analyse: StepInfo;
    retrieve: StepInfo;
    execute: StepInfo;
    validation: StepInfo;
  };
}

const ThinkingSteps: React.FC<ThinkingStepsProps> = ({ steps }) => {
  const stepKeys: ('analyse' | 'retrieve' | 'execute' | 'validation')[] = [
    'analyse',
    'retrieve',
    'execute',
    'validation',
  ];

  const getStepLabel = (key: string) => {
    switch (key) {
      case 'analyse':
        return 'Analyse';
      case 'retrieve':
        return 'Retrieve';
      case 'execute':
        return 'Execute';
      case 'validation':
        return 'Validation';
      default:
        return '';
    }
  };

  const renderIcon = (status: 'pending' | 'active' | 'completed' | 'failed') => {
    switch (status) {
      case 'completed':
        return (
          <div className="step-icon step-icon-completed">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
        );
      case 'failed':
        return (
          <div className="step-icon step-icon-failed">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </div>
        );
      case 'active':
        return (
          <div className="step-icon step-icon-active">
            <div className="step-spinner"></div>
          </div>
        );
      case 'pending':
      default:
        return (
          <div className="step-icon step-icon-pending">
            <div className="step-dot"></div>
          </div>
        );
    }
  };

  return (
    <div className="thinking-steps-card">
      <div className="thinking-steps-header">
        <div className="thinking-steps-pulse-dot"></div>
        <span className="thinking-steps-title">RAG Engine Thinking Steps</span>
      </div>
      
      <div className="thinking-steps-list">
        {stepKeys.map((key) => {
          const step = steps[key];
          return (
            <div key={key} className={`thinking-step-row ${step.status}`}>
              <div className="step-icon-container">
                {renderIcon(step.status)}
                <div className="step-line-connector"></div>
              </div>
              <div className="step-content">
                <span className="step-name">{getStepLabel(key)}</span>
                <span className="step-desc">{step.message}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ThinkingSteps;
