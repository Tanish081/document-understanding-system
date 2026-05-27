const PDF_ICON = (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
    <path d="M4 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V5.5L9.5 0H4zm5.5 1.5v3h3L9.5 1.5z"/>
  </svg>
);

const IMG_ICON = (
  <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
    <path d="M6.002 5.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/>
    <path d="M2 1a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V3a2 2 0 0 0-2-2H2zm12 1a1 1 0 0 1 1 1v6.5l-3.777-1.947a.5.5 0 0 0-.577.093l-3.71 3.71-2.66-1.772a.5.5 0 0 0-.63.062L1 12V3a1 1 0 0 1 1-1h12z"/>
  </svg>
);


function Sidebar({ recentFiles }) {
  return (
    <aside className="sidebar">
      <h1 className="sidebar-title">Modular Document Workspace Dashboard</h1>

      <p className="sidebar-section-label">Recent Extractions</p>
      <ul className="recent-list">
        {recentFiles.length === 0 ? (
          <li className="recent-empty">No files yet</li>
        ) : (
          recentFiles.map((file, i) => (
            <li key={i} className={`recent-item ${i === 0 ? 'active' : ''}`}>
              <span className={`recent-icon ${file.type}`}>
                {file.type === 'image' ? IMG_ICON : PDF_ICON}
              </span>
              <span className="recent-name" title={file.name}>{file.name}</span>
            </li>
          ))
        )}
      </ul>

    </aside>
  );
}

export default Sidebar;
