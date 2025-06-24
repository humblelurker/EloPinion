// ejemplo base
import './ImageGallery.css'; // Asegúrate de crear este archivo para los estilos    

export default function ImageGallery() {
  const dummyImages = Array.from({ length: 15 }, (_, idx) => idx);

  return (
    <div className="gallery-grid">
      {dummyImages.map((idx) => (
        <div key={idx} className="gallery-item">
          <img
            src={`https://picsum.photos/300/200?random=${idx}`}
            alt={`Producto ${idx + 1}`}
          />
          <p>Producto {idx + 1}</p>
        </div>
      ))}
    </div>
  );
}