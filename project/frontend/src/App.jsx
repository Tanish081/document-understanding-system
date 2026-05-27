import { useState } from 'react';
import Sidebar from './components/Sidebar';
import UploadSection from './components/UploadSection';
import TextViewer from './components/TextViewer';
import TableViewer from './components/TableViewer';
import ImageViewer from './components/ImageViewer';
import EntitiesViewer from './components/EntitiesViewer';
import SummaryViewer from './components/SummaryViewer';

const CAPABILITIES = [
  {
    key: 'text', colorClass: 'blue', name: 'Text Extraction',
    desc: 'Extract text from digital and scanned PDFs',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="16" y1="13" x2="8" y2="13"/>
        <line x1="16" y1="17" x2="8" y2="17"/>
        <polyline points="10 9 9 9 8 9"/>
      </svg>
    ),
  },
  {
    key: 'table', colorClass: 'green', name: 'Table Extraction',
    desc: 'Detect and extract tables with structure preserved',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <line x1="3" y1="9" x2="21" y2="9"/>
        <line x1="3" y1="15" x2="21" y2="15"/>
        <line x1="9" y1="9" x2="9" y2="21"/>
      </svg>
    ),
  },
  {
    key: 'summary', colorClass: 'purple', name: 'Summary Generation',
    desc: 'Extractive summarization using keyword frequency ranking',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
    ),
  },
  {
    key: 'ner', colorClass: 'orange', name: 'Named Entities',
    desc: 'People, organizations, locations, dates and more',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
        <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>
        <line x1="7" y1="7" x2="7.01" y2="7"/>
      </svg>
    ),
  },
];

function App() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [recentFiles, setRecentFiles] = useState([]);

  const handleResult = (data) => {
    setError(null);
    setResult(data);
    if (data.file_name) {
      const ext = data.file_name.split('.').pop().toLowerCase();
      const type = ext === 'pdf' ? 'pdf' : 'image';
      setRecentFiles((prev) =>
        [{ name: data.file_name, type }, ...prev.filter((f) => f.name !== data.file_name)].slice(0, 6)
      );
    }
  };

  const handleError = (message) => {
    setResult(null);
    setError(message);
  };

  return (
    <div className="app-layout">
      <Sidebar recentFiles={recentFiles} />

      <div className="main-area">
        {error && <div className="error-banner">{error}</div>}

        {!result ? (
          <div className="upload-layout">
            {/* Centre — upload drop zone */}
            <div className="card upload-card">
              <UploadSection onResult={handleResult} onError={handleError} />
            </div>

            {/* Right — capabilities panel */}
            <div className="card">
              <p className="capabilities-title">Capabilities</p>
              <div className="cap-list">
                {CAPABILITIES.map((cap) => (
                  <div key={cap.key} className="cap-item">
                    <div className={`cap-icon ${cap.colorClass}`}>{cap.icon}</div>
                    <div>
                      <p className="cap-name">{cap.name}</p>
                      <p className="cap-desc">{cap.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="results-grid">
            {/* Top bar with filename + new upload */}
            <div className="results-topbar">
              <span>
                <span className="results-file-name">{result.file_name}</span>
                <span className="results-file-type">
                  {result.document_type === 'scanned' ? '· Scanned PDF'
                    : result.document_type === 'image' ? '· Image'
                    : '· Digital PDF'}
                </span>
              </span>
              <button className="new-upload-btn" onClick={() => { setResult(null); setError(null); }}>
                + New Upload
              </button>
            </div>

            <SummaryViewer summary={result.summary} />
            <EntitiesViewer entities={result.entities} />
            <TextViewer
              text={result.text}
              pages={result.pages}
              metadata={result.metadata}
              pageCount={result.page_count}
              ocrUsed={result.ocr_used}
              documentType={result.document_type}
            />
            <TableViewer tables={result.tables} />
            <ImageViewer images={result.images} />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
