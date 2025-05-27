import './App.css';
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Fuse from 'fuse.js';
import Feed from './components/Feed.jsx';
import logoImg from './assets/logo.png';

function App() {
  const [products, setProducts]         = useState([]);
  const [categories, setCategories]     = useState([]);
  const [selectedCategory, setCategory] = useState('');
  const [searchTerm, setSearchTerm]     = useState('');
  const [selectedA, setA]      = useState(null);
  const [selectedB, setB]      = useState(null);
  const [preferred, setPref]   = useState(null);
  const [reviewText, setText]  = useState('');
  const [status, setStatus]    = useState('');

  useEffect(() => {
    fetch('/api/products/', { credentials: 'include' })
      .then(r => r.json())
      .then(data => {
        setProducts(data);
        setCategories([...new Set(data.map(p => p.category))]);
      })
      .catch(console.error);
  }, []);

  const available = products.filter(p => !selectedCategory || p.category === selectedCategory);
  const fuse      = new Fuse(available, { keys: ['name'], threshold: 0.3 });
  const filtered  = searchTerm ? fuse.search(searchTerm).map(r=>r.item) : available;

  function handleSelect(p) {
    if (!selectedA)       setA(p);
    else if (!selectedB && p.id!==selectedA.id) setB(p);
  }
  function resetAll() {
    setA(null); setB(null); setPref(null); setText(''); setStatus('');
  }
  async function handleSubmit() {
    if (!selectedA||!selectedB||!preferred) {
      setStatus('Completa selección y marca tu favorito.');
      return;
    }
    const body = {
      product_a_id: selectedA.id,
      product_b_id: selectedB.id,
      preferred_id: preferred==='A'?selectedA.id:selectedB.id,
      justification: reviewText,
    };
    try {
      const resp = await fetch('/api/submit-review/', {
        method:'POST',
        credentials:'include',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(body),
      });
      if (resp.status===401) { setStatus('🔒 Debes iniciar sesión.'); return; }
      const { status:st } = await resp.json();
      setStatus(st==='ok'?'✅ Enviada':'❌ Error');
    } catch {
      setStatus('❌ Error al enviar');
    }
  }

  return (
    <div id="root">
      <div className="layout">
        <aside className="sidebar">
          <img src={logoImg} alt="logo" className="sidebar-logo"/>
          <nav><Link to="/auth">Login / Registro</Link></nav>
        </aside>

        <main className="content">
          {/* 1) Dropdown categoría */}
          <select
            className="category-select"
            value={selectedCategory}
            onChange={e => {
              setCategory(e.target.value);
              resetAll();
            }}
          >
            <option value="">— Elige categoría —</option>
            {categories.map(c=>(
              <option key={c} value={c}>{c}</option>
            ))}
          </select>

          {/* 2) Barra de búsqueda */}
          <input
            className="search-input"
            type="text"
            placeholder="Buscar producto…"
            value={searchTerm}
            onChange={e=>setSearchTerm(e.target.value)}
          />

          {/* 3) Cuadros de productos (máx 4) */}
          <div className="card-list">
            {filtered.slice(0,4).map(p=>(
              <div
                key={p.id}
                className={
                  `card product-card
                   ${selectedA?.id===p.id?'sel-a':''}
                   ${selectedB?.id===p.id?'sel-b':''}`
                }
                onClick={()=>handleSelect(p)}
              >
                <strong>{p.name}</strong>
                <div>Elo: {p.elo_score}</div>
                <div>Cat: {p.category}</div>
              </div>
            ))}
          </div>

          {/* 4) Botón Reiniciar */}
          {(selectedA||selectedB) && (
            <button className="reset-btn" onClick={resetAll}>
              🔄 Reiniciar selección
            </button>
          )}

          {/* 5) Formulario de reseña */}
          {selectedA && selectedB && (
            <div className="card review-form">
              <h2>
                Prefiero…
                <span className="choice-a">
                  <input
                    type="radio"
                    name="pref"
                    value="A"
                    checked={preferred==='A'}
                    onChange={()=>setPref('A')}
                  /> {selectedA.name}
                </span>
                <span className="choice-b">
                  <input
                    type="radio"
                    name="pref"
                    value="B"
                    checked={preferred==='B'}
                    onChange={()=>setPref('B')}
                  /> {selectedB.name}
                </span>
              </h2>
              <textarea
                rows={3}
                placeholder="Justificación (opcional)…"
                value={reviewText}
                onChange={e=>setText(e.target.value)}
              />
              <button onClick={handleSubmit}>Enviar reseña</button>
              {status && <p className="status-msg">{status}</p>}
            </div>
          )}

          {/* 6) Feed */}
          <section className="feed-section">
            <Feed />
          </section>
        </main>
      </div>
    </div>
  );
}

export default App;
