// Shows all extracted named entities as a flat chip cloud — no type labels.
// Chips cycle through a small palette so the list has visual variety without
// implying any semantic meaning from the color.
const CHIP_STYLES = [
  { bg: 'rgba(66,  153, 225, 0.10)', border: 'rgba(66,  153, 225, 0.28)', text: '#2B6CB0' },
  { bg: 'rgba(56,  161, 105, 0.10)', border: 'rgba(56,  161, 105, 0.28)', text: '#276749' },
  { bg: 'rgba(128,  90, 213, 0.10)', border: 'rgba(128,  90, 213, 0.28)', text: '#6B46C1' },
  { bg: 'rgba(221, 107,  32, 0.10)', border: 'rgba(221, 107,  32, 0.28)', text: '#C05621' },
  { bg: 'rgba(49,  151, 149, 0.10)', border: 'rgba(49,  151, 149, 0.28)', text: '#2C7A7B' },
  { bg: 'rgba(229,  62,  62, 0.10)', border: 'rgba(229,  62,  62, 0.25)', text: '#C53030' },
];

function EntitiesViewer({ entities }) {
  if (!entities || entities.length === 0) return null;

  return (
    <div className="result-card">
      <p className="result-card-title">Key Entities ({entities.length})</p>
      <div className="entity-chips">
        {entities.map((ent, i) => {
          const style = CHIP_STYLES[i % CHIP_STYLES.length];
          return (
            <span
              key={i}
              className="entity-chip"
              style={{
                background: style.bg,
                border: `1px solid ${style.border}`,
                color: style.text,
              }}
            >
              {ent.text}
            </span>
          );
        })}
      </div>
    </div>
  );
}

export default EntitiesViewer;
