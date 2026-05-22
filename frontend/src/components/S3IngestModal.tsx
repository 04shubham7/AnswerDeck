/**
 * S3 PDF Ingest Modal Component
 */
import React, { useState } from 'react';
import './S3IngestModal.css';

interface S3IngestModalProps {
  isOpen: boolean;
  onClose: () => void;
  onIngestSuccess?: (source: string) => void;
}

const S3IngestModal: React.FC<S3IngestModalProps> = ({ isOpen, onClose, onIngestSuccess }) => {
  const [bucketName, setBucketName] = useState('');
  const [objectKey, setObjectKey] = useState('');
  const [awsAccessKey, setAwsAccessKey] = useState('');
  const [awsSecretKey, setAwsSecretKey] = useState('');
  const [awsRegion, setAwsRegion] = useState('');
  const [collectionName, setCollectionName] = useState('');
  const [forceRecreate, setForceRecreate] = useState(false);

  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [statusMsg, setStatusMsg] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bucketName || !objectKey) {
      setStatus('error');
      setStatusMsg('Bucket Name and PDF File Key are required.');
      return;
    }

    setStatus('loading');
    setStatusMsg('Downloading and indexing PDF file from S3...');

    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
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
          collection_name: collectionName || null,
          force_recreate: forceRecreate,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to ingest document from S3.');
      }

      setStatus('success');
      setStatusMsg(data.message || 'Document indexed successfully!');
      if (onIngestSuccess) {
        onIngestSuccess(data.source || `s3://${bucketName}/${objectKey}`);
      }
    } catch (err) {
      setStatus('error');
      setStatusMsg(err instanceof Error ? err.message : 'An error occurred during S3 ingestion.');
    }
  };

  const handleReset = () => {
    setStatus('idle');
    setStatusMsg('');
  };

  return (
    <div className="s3-modal-overlay" onClick={onClose}>
      <div className="s3-modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="s3-modal-header">
          <h2>Ingest PDF from Amazon S3</h2>
          <button className="s3-modal-close-btn" onClick={onClose}>&times;</button>
        </div>

        {status === 'loading' && (
          <div className="s3-status-view">
            <div className="s3-spinner"></div>
            <p className="s3-status-title">Ingesting Document</p>
            <p className="s3-status-message">{statusMsg}</p>
          </div>
        )}

        {status === 'success' && (
          <div className="s3-status-view">
            <div className="s3-success-icon">&#10004;</div>
            <p className="s3-status-title">Ingestion Success</p>
            <p className="s3-status-message">{statusMsg}</p>
            <div className="s3-modal-actions">
              <button className="s3-btn s3-btn-primary" onClick={onClose}>Close</button>
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="s3-status-view">
            <div className="s3-error-icon">&#9888;</div>
            <p className="s3-status-title">Ingestion Failed</p>
            <p className="s3-status-message">{statusMsg}</p>
            <div className="s3-modal-actions">
              <button className="s3-btn s3-btn-secondary" onClick={handleReset}>Try Again</button>
              <button className="s3-btn s3-btn-primary" onClick={onClose}>Close</button>
            </div>
          </div>
        )}

        {status === 'idle' && (
          <form onSubmit={handleSubmit}>
            <div className="s3-form-row">
              <div className="s3-form-group">
                <label>S3 Bucket Name *</label>
                <input
                  type="text"
                  placeholder="e.g. my-documents-bucket"
                  value={bucketName}
                  onChange={(e) => setBucketName(e.target.value)}
                  required
                />
              </div>
              <div className="s3-form-group">
                <label>PDF File Key (Path in Bucket) *</label>
                <input
                  type="text"
                  placeholder="e.g. manuals/setup.pdf"
                  value={objectKey}
                  onChange={(e) => setObjectKey(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="s3-form-row">
              <div className="s3-form-group">
                <label>AWS Access Key ID (Optional)</label>
                <input
                  type="text"
                  placeholder="Leave empty for public bucket"
                  value={awsAccessKey}
                  onChange={(e) => setAwsAccessKey(e.target.value)}
                />
              </div>
              <div className="s3-form-group">
                <label>AWS Secret Access Key (Optional)</label>
                <input
                  type="password"
                  placeholder="Leave empty for public bucket"
                  value={awsSecretKey}
                  onChange={(e) => setAwsSecretKey(e.target.value)}
                />
              </div>
            </div>

            <div className="s3-form-row">
              <div className="s3-form-group">
                <label>AWS Region (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. us-east-1"
                  value={awsRegion}
                  onChange={(e) => setAwsRegion(e.target.value)}
                />
              </div>
              <div className="s3-form-group">
                <label>Collection Name (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. learning_vectors"
                  value={collectionName}
                  onChange={(e) => setCollectionName(e.target.value)}
                />
              </div>
            </div>

            <div className="s3-checkbox-group" onClick={() => setForceRecreate(!forceRecreate)}>
              <input
                type="checkbox"
                checked={forceRecreate}
                onChange={() => {}} // Controlled by group click
              />
              <label>Recreate Vector Collection (clears existing indexing)</label>
            </div>

            <div className="s3-modal-actions">
              <button type="button" className="s3-btn s3-btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="s3-btn s3-btn-primary">
                Start Ingestion
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default S3IngestModal;
