import { useState } from 'react';
import Fuse from 'fuse.js';

function App() {
  const [searchTerm, setSearchTerm] = useState("");
  const [reviewText, setReviewText] = useState("");
  const [rating, setRating] = useState(3);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [compareProduct, setCompareProduct] = useState(null);
  const [status, setStatus] = useState("");

  const brandsWithScores = [
    { id: 1, name: "Coca Cola", elo: 1500, reviews: "/reviews/coca-cola" },
    { id: 2, name: "Pepsi", elo: 1450, reviews: "/reviews/pepsi" },
    { id: 3, name: "Dr Pepper", elo: 1420, reviews: "/reviews/dr-pepper" },
  ];

  const fuse = new Fuse(brandsWithScores, {
    keys: ['name'],
    threshold: 0.3,
  });

  const filteredBrands = searchTerm
    ? fuse.search(searchTerm).map(result => result.item)
    : brandsWithScores;

  const handleSubmitReview = async () => {
    if (!selectedProduct || !compareProduct) {
      setStatus("Debes seleccionar el producto y el de comparación.");
      return;
    }

    const reviewData = {
      product_id: selectedProduct.id,
      compare_product_id: compareProduct.id,
      review_text: reviewText,
      rating: rating,
    };

    // Depuración: Verificar los datos que estamos enviando
    console.log("Datos de reseña que se envían:", reviewData);

    try {
      const response = await fetch('http://localhost:8000/api/submit-review/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(reviewData),
      });

      const data = await response.json();
      console.log("Respuesta del backend:", data);

      if (data.status === 'reseña procesada') {
        setStatus("✅ Reseña procesada y moderada");
      } else {
        setStatus("❌ Error en el envío");
      }
    } catch (error) {
      console.error("Error al enviar la reseña:", error);
      setStatus("❌ Error al enviar la reseña");
    }
  };

  return (
    <div className="container">
      <h1 className="text-3xl font-bold">EloPinion</h1>

      <input
        type="text"
        className="search-bar"
        placeholder="Buscar..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />

      <div className="rectangles">
        {filteredBrands.map((brand) => (
          <div
            key={brand.id}
            className="rectangle"
            onClick={() => setSelectedProduct(brand)}
          >
            <div>{brand.name}</div>
            <div>Puntos: {brand.elo}</div>
            <a href={brand.reviews}>Ver historial de reseñas</a>
          </div>
        ))}
      </div>

      {selectedProduct && (
        <div className="review-form">
          <h2>Escribir reseña para {selectedProduct.name}</h2>
          <label>Comparar con:</label>
          <select
            value={compareProduct?.id || ""}
            onChange={(e) => {
              const brand = brandsWithScores.find(b => b.id === parseInt(e.target.value));
              setCompareProduct(brand);
            }}
          >
            <option value="">-- Seleccionar --</option>
            {brandsWithScores
              .filter(b => b.id !== selectedProduct.id)
              .map(b => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
          </select>

          <textarea
            placeholder="Escribe tu reseña aquí..."
            value={reviewText}
            onChange={(e) => setReviewText(e.target.value)}
          />

          <div className="rating-container">
            <label>Calificación (1 a 5):</label>
            <input
              type="number"
              min={1}
              max={5}
              value={rating}
              onChange={(e) => setRating(Number(e.target.value))}
            />
          </div>

          <button className="submit-button" onClick={handleSubmitReview}>
            Enviar reseña
          </button>

          {status && <p>{status}</p>}
        </div>
      )}
    </div>
  );
}

export default App;