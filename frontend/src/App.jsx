import './App.css';
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Fuse from 'fuse.js';
import Feed from './components/Feed.jsx';
import logoImg from './assets/logo.png';

/* Comprueba sesión consultando al backend */
const fetchLogin = () =>
  fetch("/api/whoami/", { credentials: "include" })
    .then(r => r.ok ? r.json() : { is_admin:false })
    .catch(() => ({ is_admin:false }));

export default function App() {
  /* ---------- estado global ---------- */
  const [logged,      setLogged]      = useState(false);
  const [isAdmin,     setIsAdmin]     = useState(false);
  const [products,    setProducts]    = useState([]);
  const [categories,  setCategories]  = useState([]);
  const [cat,         setCat]         = useState('');
  const [term,        setTerm]        = useState('');

  /* selección */
  const [a, setA]      = useState(null);
  const [b, setB]      = useState(null);
  const [pref, setPref]= useState(null);
  const [text, setText]= useState('');
  const [allowC, setAC]= useState(true);
  const [status, setStatus] = useState('');

  /* ---------- carga inicial ---------- */
  useEffect(() => {
  fetchLogin().then(({ user, is_admin }) => {
  setLogged(!!user);
  setIsAdmin(is_admin);          // crea estado nuevo
 });

    fetch('/api/products/')
      .then(r => r.json())
      .then(data => {
        setProducts(data);
        setCategories([...new Set(data.map(p => p.category))]);
      })
      .catch(console.error);
  }, []);

  /* ---------- helpers ---------- */
  const available = products.filter(p => !cat || p.category === cat);
  const filtered  = term
    ? new Fuse(available, { keys: ['name'], threshold: 0.3 })
        .search(term).map(r => r.item)
    : available;

  const selectProd = p => {
    if (!a) setA(p);
    else if (!b && p.id !== a.id) setB(p);
  };

  const resetForm = () => {
    setA(null); setB(null); setPref(null);
    setText(''); setAC(true); setStatus('');
  };

  /* ---------- submit ---------- */
  async function handleSubmit() {
    if (!a || !b || !pref) {
      setStatus('Completa la selección y elige favorito.');
      return;
    }
    const body = {
      product_a_id : a.id,
      product_b_id : b.id,
      preferred_id : pref==='A' ? a.id : b.id,
      justification: text,
      allow_comments: allowC
    };
    try {
      const resp = await fetch('/api/submit-review/', {
        method:'POST',
        credentials:'include',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify(body)
      });
      if (resp.status===401) { setStatus('🔒 Inicia sesión.'); return; }
      const { status: st } = await resp.json();
      setStatus(st==='ok' ? '✅ Enviada' : '❌ Error');
      if (st==='ok') resetForm();
    } catch { setStatus('❌ Error al enviar'); }
  }

  /* ---------- UI ---------- */
  return (
    <div id="root">
      <div className="layout">
        <aside className="sidebar">
          <img src={logoImg} alt="EloPinion" className="sidebar-logo" />
          <nav><Link to="/">Inicio</Link></nav>
          <nav><Link to="/auth">Login / Registro</Link></nav>
              {/* link visible sólo logeado */}
          <nav>{logged && <Link to="/my-reviews">Mis reseñas</Link>}</nav>
          {isAdmin && <nav><Link to="/moderate">Moderar reportes</Link></nav>}
        </aside>

        <main className="content">
          {/* categoría */}
          <select className="category-select"
                  value={cat}
                  onChange={e => { setCat(e.target.value); resetForm(); }}>
            <option value="">— Elige categoría —</option>
            {categories.map(c => <option key={c} value={c}>{c}</option>)}
          </select>

          {/* búsqueda */}
          <input className="search-input"
                 placeholder="Buscar producto…"
                 value={term}
                 onChange={e => setTerm(e.target.value)} />

          {/* lista de productos */}
          <div className="card-list">
            {filtered.slice(0,6).map(p => (
              <div key={p.id}
                   className={`card product-card ${a?.id===p.id?'sel-a':''} ${b?.id===p.id?'sel-b':''}`}
                   onClick={() => selectProd(p)}>
                <strong>{p.name}</strong>
                <div>Elo {p.elo_score}</div>
                <div>{p.category}</div>
              </div>
            ))}
          </div>

          {(a||b) && <button className="reset-btn" onClick={resetForm}>🔄 Reiniciar</button>}

          {/* formulario (solo logeado) */}
          {logged && a && b && (
            <div className="card review-form">
              <h2>Prefiero…</h2>

              <label className="radio-group">
                <span><input type="radio" name="pref" value="A"
                              checked={pref==='A'} onChange={()=>setPref('A')} /> {a.name}</span>
                <span><input type="radio" name="pref" value="B"
                              checked={pref==='B'} onChange={()=>setPref('B')} /> {b.name}</span>
              </label>

              <label style={{margin:".5rem 0", display:"block"}}>
                <input type="checkbox" checked={allowC}
                       onChange={e=>setAC(e.target.checked)} /> Permitir comentarios
              </label>

              <textarea rows={3} placeholder="Justificación (opcional)…"
                        value={text} onChange={e=>setText(e.target.value)} />

              <button onClick={handleSubmit}>Enviar reseña</button>
              {status && <p className="status-msg">{status}</p>}
            </div>
          )}

          {/* feed */}
          <section className="feed-section">
            <Feed logged={logged}/>
          </section>
        </main>
      </div>
    </div>
  );
}
