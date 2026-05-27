// Renders tables extracted from the PDF, grouped by page.
function TableViewer({ tables }) {
  if (!tables || tables.length === 0) return null;

  // Group tables by page number for cleaner display.
  const byPage = tables.reduce((acc, table) => {
    const key = table.page;
    if (!acc[key]) acc[key] = [];
    acc[key].push(table);
    return acc;
  }, {});

  return (
    <div className="result-card">
      <p className="result-card-title">Tables ({tables.length})</p>
      <div className="tables-stack">
        {Object.entries(byPage).map(([page, pageTables]) =>
          pageTables.map((table, i) => {
            const [headerRow, ...bodyRows] = table.rows;
            return (
              <div key={`${page}-${i}`} className="table-block">
                <p className="table-meta">
                  Page {page}{pageTables.length > 1 ? ` · Table ${i + 1}` : ''}
                </p>
                <div className="table-scroll">
                  <table className="data-table">
                    {headerRow && (
                      <thead>
                        <tr>
                          {headerRow.map((cell, ci) => (
                            <th key={ci}>{cell}</th>
                          ))}
                        </tr>
                      </thead>
                    )}
                    <tbody>
                      {bodyRows.map((row, ri) => (
                        <tr key={ri}>
                          {row.map((cell, ci) => (
                            <td key={ci}>{cell}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default TableViewer;
