// Renders images extracted from the PDF in a responsive grid.
function ImageViewer({ images }) {
  if (!images || images.length === 0) return null;

  return (
    <div className="result-card">
      <p className="result-card-title">Images ({images.length})</p>
      <div className="images-grid">
        {images.map((img, idx) => (
          <div key={idx} className="image-card">
            <img
              src={img.data}
              alt={`Page ${img.page} image ${img.image_index + 1}`}
              className="extracted-image"
            />
            <p className="image-meta">
              Page {img.page} · {img.width}×{img.height}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ImageViewer;
