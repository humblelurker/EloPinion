/* frontend/src/App.jsx */
import { useState } from 'react';
import { Link } from 'react-router-dom';   // ← nuevo
import Fuse from 'fuse.js';

function App() {
  /* ----------  ESTADO  ---------- */
  const [searchTerm, setSearchTerm] = useState('');
  const [reviewText, setReviewText]   = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [compareProduct,  setCompareProduct]  = useState(null);
  const [preferred,       setPreferred]       = useState(null);   // "A" o "B"
  const [status,          setStatus]          = useState('');

  /* ----------  DATA DE EJEMPLO  ---------- */
  const brandsWithScores = [
    { id: 1, name: 'Coca Cola', elo: 1500, reviews: '/reviews/coca-cola' },
    { id: 2, name: 'Pepsi',      elo: 1450, reviews: '/reviews/pepsi'     },
    { id: 3, name: 'Dr Pepper',  elo: 1420, reviews: '/reviews/dr-pepper' },
  ];

  /* ----------  BÚSQUEDA DIFUSA  ---------- */
  const fuse = new Fuse(brandsWithScores, { keys: ['name'], threshold: 0.3 });
  const filteredBrands = searchTerm
    ? fuse.search(searchTerm).map(r => r.item)
    : brandsWithScores;

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
      const resp  = await fetch('http://localhost:8000/api/submit-review/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reviewData),
      });
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
    <div className="container" style={{ padding: '1rem', fontFamily: 'sans-serif' }}>
      {/* ENLACE A REGISTRO / LOGIN */}
      <div style={{ marginBottom: '1rem' }}>
        <Link to="/auth">Registrarse / Iniciar sesión</Link>
      </div>
      {/* BUSCADOR */}
      <input
        type="text"
        placeholder="Buscar producto…"
        value={searchTerm}
        onChange={e => setSearchTerm(e.target.value)}
        style={{ padding: '.5rem', width: '100%', maxWidth: '400px' }}
      />

      {/* LISTA DE PRODUCTOS */}
      <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap' }}>
        {filteredBrands.map(brand => (
          <div
            key={brand.id}
            style={{
              border: '1px solid #ccc',
              borderRadius: '4px',
              padding: '0.75rem',
              cursor: 'pointer',
              minWidth: '140px',
            }}
            onClick={() => {
              setSelectedProduct(brand);
              setCompareProduct(null);
              setPreferred(null);
              setReviewText('');
              setStatus('');
            }}
          >
            <strong>{brand.name}</strong>
            <div>Elo: {brand.elo}</div>
          </div>
        ))}
      </div>

      {/* FORMULARIO DE RESEÑA */}
      {selectedProduct && (
        <div className="review-form" style={{ marginTop: '2rem', maxWidth: '500px' }}>
          <h2>
            Comparar <em>{selectedProduct.name}</em> con otro producto y elegir favorito
          </h2>

          {/* SELECT DE PRODUCTO B */}
          <label style={{ display: 'block', marginTop: '1rem' }}>Comparar con:</label>
          <select
            value={compareProduct?.id || ''}
            onChange={e =>
              setCompareProduct(
                brandsWithScores.find(b => b.id === parseInt(e.target.value))
              )
            }
            style={{ padding: '.4rem', width: '100%' }}
          >
            <option value="">-- Seleccionar --</option>
            {brandsWithScores
              .filter(b => b.id !== selectedProduct.id)
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
            style={{ width: '100%', marginTop: '1rem', padding: '.5rem' }}
          />

          {/* PREFERENCIA */}
          {compareProduct && (
            <>
              <label style={{ display: 'block', marginTop: '1rem' }}>Prefiero:</label>
              <div style={{ display: 'flex', gap: '2rem', marginTop: '.5rem' }}>
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
          <button
            onClick={handleSubmitReview}
            style={{
              marginTop: '1rem',
              padding: '.6rem 1.2rem',
              background: '#2563eb',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            Enviar reseña
          </button>

          {status && <p style={{ marginTop: '.75rem' }}>{status}</p>}
        </div>
      )}
    </div>
  );
}

export default App;
