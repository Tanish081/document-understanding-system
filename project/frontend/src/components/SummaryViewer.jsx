// Displays the extractive summary produced by nlp_service.
function SummaryViewer({ summary }) {
  if (!summary || !summary.trim()) return null;

  // Split on sentence boundaries to render each sentence on its own line.
  const sentences = summary
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter(Boolean);

  return (
    <div className="result-card">
      <p className="result-card-title">Summary</p>
      <p className="summary-note">
        Top {sentences.length} sentence{sentences.length !== 1 ? 's' : ''} extracted by keyword frequency
      </p>
      <ol className="summary-list">
        {sentences.map((sentence, i) => (
          <li key={i} className="summary-sentence">
            {sentence}
          </li>
        ))}
      </ol>
    </div>
  );
}

export default SummaryViewer;
