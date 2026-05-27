import { useRef, useState } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const CLOUD_ICON = (
  <svg width="38" height="38" viewBox="0 0 24 24" fill="none"
    stroke="#63B3ED" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="16 16 12 12 8 16" />
    <line x1="12" y1="12" x2="12" y2="21" />
    <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" />
  </svg>
);

const SPINNER_ICON = (
  <svg width="36" height="36" viewBox="0 0 24 24" fill="none"
    stroke="#4F79E5" strokeWidth="2" strokeLinecap="round">
    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83">
      <animateTransform attributeName="transform" type="rotate"
        from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
    </path>
  </svg>
);

function UploadSection({ onResult, onError }) {
  const inputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const uploadFile = async (file) => {
    if (!file) return;
    setSelectedFile(file);
    setIsUploading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) {
        onError?.(data.error || 'Upload failed.');
      } else {
        onResult?.(data);
      }
    } catch {
      onError?.('Could not reach the backend. Make sure Flask is running on port 5000.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    uploadFile(e.dataTransfer.files?.[0]);
  };

  return (
    <div
      className={`drop-zone ${isDragging ? 'drop-zone-active' : ''}`}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => !isUploading && inputRef.current?.click()}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click(); }}
    >
      <div className="upload-icon-bg">
        {isUploading ? SPINNER_ICON : CLOUD_ICON}
      </div>

      {isUploading ? (
        <>
          <p className="drop-title">Processing…</p>
          <p className="drop-subtitle">{selectedFile?.name}</p>
        </>
      ) : (
        <>
          <p className="drop-title">Drop here</p>
          <p className="drop-subtitle">
            {selectedFile
              ? `Last: ${selectedFile.name}`
              : 'PDF, scanned PDF, PNG, JPG, JPEG'}
          </p>
          <button
            type="button"
            className="choose-btn"
            onClick={(e) => { e.stopPropagation(); inputRef.current?.click(); }}
          >
            Choose file
          </button>
        </>
      )}

      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.png,.jpg,.jpeg"
        className="hidden-input"
        onChange={(e) => uploadFile(e.target.files?.[0])}
      />
    </div>
  );
}

export default UploadSection;
