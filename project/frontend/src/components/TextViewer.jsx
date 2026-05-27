// Renders extracted text and document metadata returned by the backend.
function TextViewer({ text, pages, metadata, pageCount, ocrUsed, documentType }) {
  if (!text && !pageCount) return null;

  const metaEntries = [
    { label: 'Pages', value: pageCount },
    { label: 'Type', value: documentType === 'scanned' ? 'Scanned PDF' : documentType === 'image' ? 'Image' : 'Digital PDF' },
    { label: 'Title', value: metadata?.title || '—' },
    { label: 'Author', value: metadata?.author || '—' },
  ];

  return (
    <div className="viewer-stack">
      {/* Document metadata row */}
      <div className="result-card">
        <p className="result-card-title">
          Document Info
          {ocrUsed && <span className="ocr-badge">OCR</span>}
        </p>
        <div className="metadata-grid">
          {metaEntries.map(({ label, value }) => (
            <div key={label} className="metadata-item">
              <p className="metadata-label">{label}</p>
              <p className="metadata-value">{value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Full extracted text */}
      <div className="result-card">
        <p className="result-card-title">Extracted Text</p>
        {text ? (
          <pre className="text-content">{text}</pre>
        ) : (
          <p className="text-empty">No text could be extracted from this document.</p>
        )}
      </div>

      {/* Per-page breakdown — only shown for multi-page documents */}
      {pages?.length > 1 && (
        <div className="result-card">
          <p className="result-card-title">Pages ({pages.length})</p>
          <div className="pages-list">
            {pages.map(({ page_number, text: pageText }) => (
              <details key={page_number} className="page-item">
                <summary className="page-summary">Page {page_number}</summary>
                <pre className="text-content page-text">{pageText || '(no text on this page)'}</pre>
              </details>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default TextViewer;
