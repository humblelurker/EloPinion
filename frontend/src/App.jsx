import './App.css';                           // Importa estilos globales
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Fuse from 'fuse.js';
import Feed from './components/Feed.jsx';

function App() {
  /* ----------  ESTADO  ---------- */
  const [searchTerm, setSearchTerm] = useState('');
  const [reviewText, setReviewText]   = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [compareProduct,  setCompareProduct]  = useState(null);
  const [preferred,       setPreferred]       = useState(null);   // "A" o "B"
  const [status,          setStatus]          = useState('');

// ----------  DATA REAL  ----------
const [products, setProducts] = useState([]);

useEffect(() => {
  fetch("/api/products/", {
    credentials: "include",
  })
    .then((r) => r.json())
    .then(setProducts)
    .catch(console.error);
}, []);

  /* ----------  BÚSQUEDA DIFUSA  ---------- */
 const fuse = new Fuse(products, { keys: ['name'], threshold: 0.3 });
 const filteredBrands = searchTerm
   ? fuse.search(searchTerm).map(r => r.item)
   : products;

  /* ----------  ENVÍO AL BACKEND  ---------- */
  const handleSubmitReview = async () => {
    if (!selectedProduct || !compareProduct || !preferred) {
      setStatus('Debes elegir ambos productos y marcar tu preferido.');
      return;
    }

    const reviewData = {
      product_a_id: selectedProduct.id,
      product_b_id: compareProduct.id,
      preferred_id: preferred === 'A' ? selectedProduct.id : compareProduct.id,
      justification: reviewText,
    };
    console.log('Datos enviados:', reviewData);

    try {
      const resp  = await fetch('/api/submit-review/', {
        method: 'POST',
        credentials: 'include',            // incluye cookie de sesión
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reviewData),
      });
      if (resp.status === 401) {
        setStatus('🔒 Debes iniciar sesión para publicar.');
        return;
      }
      const data  = await resp.json();
      setStatus(data.status === 'ok' ? '✅ Reseña enviada' : '❌ Error');
    } catch (err) {
      console.error(err);
      setStatus('❌ Error al enviar la reseña');
    }
  };

  console.log('App render OK');

  /* ----------  UI  ---------- */
  return (
    <div className="card">   {/* Usa la clase .card de App.css para padding y text-align */}
      {/* ENLACE A REGISTRO / LOGIN */}
      <div className="read-the-docs">
        <Link to="/auth">Registrarse / Iniciar sesión</Link>
      </div>

      {/* FEED ALEATORIO */}
      <Feed />
      <hr className="divider" />

      {/* BUSCADOR */}
      <input
        className="search-input"
        type="text"
        placeholder="Buscar producto…"
        value={searchTerm}
        onChange={e => setSearchTerm(e.target.value)}
      />

      {/* LISTA DE PRODUCTOS */}
      <div className="card-list">
        {filteredBrands.map(brand => (
          <div
            key={brand.id}
            className="card"
            onClick={() => {
              setSelectedProduct(brand);
              setCompareProduct(null);
              setPreferred(null);
              setReviewText('');
              setStatus('');
            }}
          >
            <strong>{brand.name}</strong>
            <div>Elo: {brand.elo_score}</div>
            <div>Categoría: {brand.category}</div>
          </div>
        ))}
      </div>

      {/* FORMULARIO DE RESEÑA */}
      {selectedProduct && (
        <div className="card review-form">
          <h2>
            Comparar <em>{selectedProduct.name}</em> con otro producto y elegir favorito
          </h2>

          {/* SELECT DE PRODUCTO B */}
          <label>Comparar con:</label>
          <select
            value={compareProduct?.id || ''}
            onChange={e =>
              setCompareProduct(
                products.find(b => b.id === parseInt(e.target.value))
              )
            }
          >
            <option value="">-- Seleccionar --</option>
            {products
              .filter(b => b.id !== selectedProduct.id && b.category === selectedProduct.category)
              .map(b => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
          </select>

          {/* JUSTIFICACIÓN */}
          <textarea
            placeholder="Justificación (opcional)…"
            value={reviewText}
            onChange={e => setReviewText(e.target.value)}
            rows={3}
          />

          {/* PREFERENCIA */}
          {compareProduct && (
            <>
              <label>Prefiero:</label>
              <div className="radio-group">
                <label>
                  <input
                    type="radio"
                    name="preferred"
                    value="A"
                    checked={preferred === 'A'}
                    onChange={() => setPreferred('A')}
                  />{' '}
                  {selectedProduct.name}
                </label>
                <label>
                  <input
                    type="radio"
                    name="preferred"
                    value="B"
                    checked={preferred === 'B'}
                    onChange={() => setPreferred('B')}
                  />{' '}
                  {compareProduct.name}
                </label>
              </div>
            </>
          )}

          {/* BOTÓN Y ESTADO */}
          <button onClick={handleSubmitReview}>Enviar reseña</button>

          {status && <p>{status}</p>}
        </div>
      )}
    </div>
  );
}

export default App;
