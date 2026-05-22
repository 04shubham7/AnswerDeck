/**
 * LandingPanel Component
 * Displays system overview, live status metrics, and handles document ingestion (Local PDF and Amazon S3).
 */
import React, { useState, useEffect } from 'react';
import './LandingPanel.css';

interface LandingPanelProps {
  onIngestSuccess: (source: string) => void;
}

interface SystemStatus {
  apiHealthy: boolean;
  apiVersion: string;
  environment: string;
  qdrantUrl: string;
  collectionName: string;
  loading: boolean;
}

const LandingPanel: React.FC<LandingPanelProps> = ({ onIngestSuccess }) => {
  const [activeTab, setActiveTab] = useState<'local' | 's3'>('local');
  const [status, setStatus] = useState<SystemStatus>({
    apiHealthy: false,
    apiVersion: 'N/A',
    environment: 'development',
    qdrantUrl: 'N/A',
    collectionName: 'N/A',
    loading: true,
  });

  // Local file upload states
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const [localCollection, setLocalCollection] = useState('');
  const [localForceRecreate, setLocalForceRecreate] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [uploadMessage, setUploadMessage] = useState('');

  // S3 upload states
  const [bucketName, setBucketName] = useState('');
  const [objectKey, setObjectKey] = useState('');
  const [awsAccessKey, setAwsAccessKey] = useState('');
  const [awsSecretKey, setAwsSecretKey] = useState('');
  const [awsRegion, setAwsRegion] = useState('');
  const [s3Collection, setS3Collection] = useState('');
  const [s3ForceRecreate, setS3ForceRecreate] = useState(false);
  const [s3Status, setS3Status] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [s3Message, setS3Message] = useState('');

  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

  // Fetch status metrics
  const fetchStatus = async () => {
    try {
      // Fetch health
      const healthRes = await fetch(`${apiUrl.replace('/api/v1', '')}/api/v1/health`);
      const healthData = await healthRes.json();
      
      // Fetch status
      const statusRes = await fetch(`${apiUrl.replace('/api/v1', '')}/api/v1/status`);
      const statusData = await statusRes.json();

      setStatus({
        apiHealthy: healthRes.ok && healthData.status === 'healthy',
        apiVersion: healthData.version || 'unknown',
        environment: healthData.environment || 'development',
        qdrantUrl: statusData.qdrant_url || 'N/A',
        collectionName: statusData.collection_name || 'N/A',
        loading: false,
      });
    } catch (err) {
      console.error('Error fetching system status:', err);
      setStatus(prev => ({
        ...prev,
        apiHealthy: false,
        loading: false,
      }));
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  // Handle drag events
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  // Handle drop event
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf" || file.name.endsWith('.pdf')) {
        setSelectedFile(file);
        setUploadStatus('idle');
        setUploadMessage('');
      } else {
        setUploadStatus('error');
        setUploadMessage('Only PDF files are supported.');
      }
    }
  };

  // Handle file select
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type === "application/pdf" || file.name.endsWith('.pdf')) {
        setSelectedFile(file);
        setUploadStatus('idle');
        setUploadMessage('');
      } else {
        setUploadStatus('error');
        setUploadMessage('Only PDF files are supported.');
      }
    }
  };

  // Handle local file upload submit
  const handleLocalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setUploadStatus('error');
      setUploadMessage('Please select or drag a PDF file first.');
      return;
    }

    setUploadStatus('loading');
    setUploadMessage('Processing and index-embedding local PDF...');
    setUploadProgress(20);

    const formData = new FormData();
    formData.append('file', selectedFile);
    if (localCollection) {
      formData.append('collection_name', localCollection);
    }
    formData.append('force_recreate', String(localForceRecreate));

    try {
      setUploadProgress(50);
      const response = await fetch(`${apiUrl}/ingest/file`, {
        method: 'POST',
        body: formData,
      });

      setUploadProgress(85);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to ingest file.');
      }

      setUploadProgress(100);
      setUploadStatus('success');
      setUploadMessage(data.message || 'File ingested and indexed successfully!');
      onIngestSuccess(data.source || selectedFile.name);
      
      // Clear file after brief delay
      setTimeout(() => {
        setSelectedFile(null);
        setUploadStatus('idle');
        setUploadMessage('');
      }, 3000);
    } catch (err) {
      setUploadStatus('error');
      setUploadMessage(err instanceof Error ? err.message : 'An error occurred during file ingestion.');
    }
  };

  // Handle S3 submit
  const handleS3Submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bucketName || !objectKey) {
      setS3Status('error');
      setS3Message('Bucket name and PDF key are required.');
      return;
    }

    setS3Status('loading');
    setS3Message('Fetching and indexing PDF document from Amazon S3...');

    try {
      const response = await fetch(`${apiUrl}/ingest/s3`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          bucket_name: bucketName,
          object_key: objectKey,
          aws_access_key_id: awsAccessKey || null,
          aws_secret_access_key: awsSecretKey || null,
          aws_region: awsRegion || null,
          collection_name: s3Collection || null,
          force_recreate: s3ForceRecreate,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to ingest document from S3.');
      }

      setS3Status('success');
      setS3Message(data.message || 'Document ingested and indexed successfully!');
      onIngestSuccess(data.source || `s3://${bucketName}/${objectKey}`);

      // Clear input fields after brief delay
      setTimeout(() => {
        setBucketName('');
        setObjectKey('');
        setAwsAccessKey('');
        setAwsSecretKey('');
        setAwsRegion('');
        setS3Status('idle');
        setS3Message('');
      }, 3000);
    } catch (err) {
      setS3Status('error');
      setS3Message(err instanceof Error ? err.message : 'An error occurred during S3 ingestion.');
    }
  };

  return (
    <div className="landing-panel">
      {/* Brand & Introduction */}
      <div className="brand-section">
        <div className="logo-container">
          <div className="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
          </div>
          <span className="logo-text">AnswerDeck</span>
        </div>
        <h1 className="landing-title">AI-Powered Deep Semantic Retrieval</h1>
        <p className="landing-subtitle">
          Ingest your PDF documents locally or directly from AWS S3, and query them with full transparency into the model's multi-tier cognitive process.
        </p>
      </div>

      {/* System Status Tracker */}
      <div className="status-tracker-card">
        <div className="tracker-header">
          <span className="tracker-title">System Status & Connectivity</span>
          <button className="refresh-status-btn" onClick={fetchStatus} disabled={status.loading}>
            <svg className={status.loading ? 'spinning' : ''} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67" />
            </svg>
          </button>
        </div>

        <div className="status-grid">
          <div className="status-item">
            <span className="status-label">RAG Engine Server</span>
            <div className="status-value-wrapper">
              <span className={`status-dot ${status.apiHealthy ? 'online' : 'offline'}`}></span>
              <span className="status-value">{status.apiHealthy ? 'Operational' : 'Offline'}</span>
            </div>
          </div>
          <div className="status-item">
            <span className="status-label">Environment</span>
            <span className="status-value capitalize">{status.environment}</span>
          </div>
          <div className="status-item full-width">
            <span className="status-label">Qdrant Node Endpoint</span>
            <span className="status-value code-text">{status.qdrantUrl}</span>
          </div>
          <div className="status-item full-width">
            <span className="status-label">Target Vector Collection</span>
            <span className="status-value code-text">{status.collectionName}</span>
          </div>
        </div>
      </div>

      {/* Ingestion Hub Workspace */}
      <div className="ingestion-hub-card">
        <div className="hub-header">
          <h3>Ingestion Control Hub</h3>
          <p>Index documents directly into the high-performance Qdrant cluster</p>
        </div>

        {/* Tab Controls */}
        <div className="tab-controls">
          <button 
            className={`tab-btn ${activeTab === 'local' ? 'active' : ''}`}
            onClick={() => setActiveTab('local')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
            </svg>
            Local PDF
          </button>
          <button 
            className={`tab-btn ${activeTab === 's3' ? 'active' : ''}`}
            onClick={() => setActiveTab('s3')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21.2 15c.7-1.2 1-2.5.7-3.9-.3-2-1.8-3.7-3.8-4-2.3-.4-4.4 1-5 3.1-1.3-.9-3.2-.8-4.4.3C7.5 11.6 7 13 7.3 14.4c.3 1.4 1.4 2.5 2.8 2.8H18c1.7 0 3.2-1 3.2-2.2z"/>
            </svg>
            Amazon S3 Ingest
          </button>
        </div>

        {/* Local Tab Panel */}
        {activeTab === 'local' && (
          <div className="tab-panel">
            <form onSubmit={handleLocalSubmit} onDragEnter={handleDrag}>
              <div 
                className={`drag-drop-zone ${isDragActive ? 'drag-active' : ''} ${selectedFile ? 'has-file' : ''}`}
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
              >
                <input 
                  type="file" 
                  id="local-file-input" 
                  accept=".pdf" 
                  onChange={handleFileChange}
                  className="hidden-file-input"
                />
                <label htmlFor="local-file-input" className="drag-drop-label">
                  <div className="upload-icon-wrapper">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                      <line x1="12" y1="18" x2="12" y2="12"/>
                      <polyline points="9 15 12 12 15 15"/>
                    </svg>
                  </div>
                  {selectedFile ? (
                    <div className="selected-file-details">
                      <span className="file-name">{selectedFile.name}</span>
                      <span className="file-size">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
                    </div>
                  ) : (
                    <div className="upload-prompt">
                      <span className="primary-prompt">Drag & drop your PDF file here</span>
                      <span className="secondary-prompt">or click to browse local files</span>
                    </div>
                  )}
                </label>
              </div>

              {/* Ingestion Parameters */}
              <div className="ingestion-params-grid">
                <div className="form-group">
                  <label htmlFor="local-collection">Target Collection (Optional)</label>
                  <input
                    id="local-collection"
                    type="text"
                    placeholder="e.g. documentation"
                    value={localCollection}
                    onChange={(e) => setLocalCollection(e.target.value)}
                  />
                </div>

                <div 
                  className="checkbox-group"
                  onClick={() => setLocalForceRecreate(!localForceRecreate)}
                >
                  <input
                    type="checkbox"
                    checked={localForceRecreate}
                    onChange={() => {}} // Handle state via group click
                  />
                  <span>Re-create collection (wipes existing indexes)</span>
                </div>
              </div>

              {/* Status Output */}
              {uploadStatus !== 'idle' && (
                <div className={`notification-banner ${uploadStatus}`}>
                  {uploadStatus === 'loading' && (
                    <div className="progress-bar-container">
                      <div className="progress-bar-fill" style={{ width: `${uploadProgress}%` }}></div>
                    </div>
                  )}
                  <span className="notification-message">{uploadMessage}</span>
                </div>
              )}

              <button 
                type="submit" 
                className="submit-ingest-btn" 
                disabled={!selectedFile || uploadStatus === 'loading'}
              >
                {uploadStatus === 'loading' ? (
                  <>
                    <span className="spinner-small"></span>
                    Indexing File...
                  </>
                ) : 'Submit Ingestion'}
              </button>
            </form>
          </div>
        )}

        {/* S3 Tab Panel */}
        {activeTab === 's3' && (
          <div className="tab-panel">
            <form onSubmit={handleS3Submit}>
              <div className="s3-fields-grid">
                <div className="form-group">
                  <label>S3 Bucket Name *</label>
                  <input
                    type="text"
                    placeholder="e.g. my-rag-bucket"
                    value={bucketName}
                    onChange={(e) => setBucketName(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>PDF Object Key (File Path) *</label>
                  <input
                    type="text"
                    placeholder="e.g. docs/architecture.pdf"
                    value={objectKey}
                    onChange={(e) => setObjectKey(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>AWS Access Key ID (Optional)</label>
                  <input
                    type="text"
                    placeholder="Leave blank for public buckets"
                    value={awsAccessKey}
                    onChange={(e) => setAwsAccessKey(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>AWS Secret Access Key (Optional)</label>
                  <input
                    type="password"
                    placeholder="Leave blank for public buckets"
                    value={awsSecretKey}
                    onChange={(e) => setAwsSecretKey(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>AWS Region (Optional)</label>
                  <input
                    type="text"
                    placeholder="e.g. us-west-2"
                    value={awsRegion}
                    onChange={(e) => setAwsRegion(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Collection Name (Optional)</label>
                  <input
                    type="text"
                    placeholder="e.g. s3_documents"
                    value={s3Collection}
                    onChange={(e) => setS3Collection(e.target.value)}
                  />
                </div>
              </div>

              <div 
                className="checkbox-group s3-checkbox"
                onClick={() => setS3ForceRecreate(!s3ForceRecreate)}
              >
                <input
                  type="checkbox"
                  checked={s3ForceRecreate}
                  onChange={() => {}} // Controlled by group click
                />
                <span>Re-create collection (wipes existing indexes)</span>
              </div>

              {/* Status Output */}
              {s3Status !== 'idle' && (
                <div className={`notification-banner ${s3Status}`}>
                  <span className="notification-message">{s3Message}</span>
                </div>
              )}

              <button 
                type="submit" 
                className="submit-ingest-btn" 
                disabled={s3Status === 'loading'}
              >
                {s3Status === 'loading' ? (
                  <>
                    <span className="spinner-small"></span>
                    Downloading & Indexing...
                  </>
                ) : 'Submit Ingestion'}
              </button>
            </form>
          </div>
        )}
      </div>

      {/* Feature / Concept Help */}
      <div className="engine-info-footer">
        <div className="info-badge">Engine Architecture</div>
        <ul className="info-bullets">
          <li><strong>Analyse:</strong> Parses natural query keywords and context intents.</li>
          <li><strong>Retrieve:</strong> Queries Qdrant dense vectors for high-similarity passages.</li>
          <li><strong>Execute:</strong> Generates highly grounded answers via Gemini.</li>
          <li><strong>Validation:</strong> cross-checks citations against source docs before display.</li>
        </ul>
      </div>
    </div>
  );
};

export default LandingPanel;
