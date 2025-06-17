import './App.css';
import { useState, useEffect } from 'react';
import Fuse from 'fuse.js';
import Feed from './components/Feed.jsx';
import logoImg from './assets/logo.png';
import SideBar from './components/SideBar.jsx';
import ReviewForm from './components/ReviewForm.jsx';

/* Comprueba sesión consultando al backend */
const fetchLogin = () =>
  fetch("/api/whoami/", { credentials: "include" })
    .then(r => r.ok ? r.json() : { is_admin:false })
    .catch(() => ({ is_admin:false }));

export default function App() {
  /* ---------- estado global: autenticación ---------- */
  const [logged,  setLogged]  = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  /* ---------- estado global: productos ---------- */
  const [products,   setProducts]   = useState([]);
  const [categories, setCategories] = useState([]);
  const [cat,        setCat]        = useState('');
  const [term,       setTerm]       = useState('');

  /* ---------- estado global: selección de productos ---------- */
  const [a,    setA]    = useState(null);
  const [b,    setB]    = useState(null);

  /* ---------- estado global: reseña ---------- */
  const [pref,  setPref]  = useState(null);
  const [text,  setText]  = useState('');
  const [allowC,setAC]    = useState(true);
  const [status,setStatus]= useState('');

  /* ---------- carga inicial ---------- */
  useEffect(() => {
    fetchLogin().then(({ user, is_admin }) => {
      setLogged(!!user);
      setIsAdmin(is_admin);
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

  /* ---------- handlers ---------- */
  const selectProd = p => {
    if (!a) setA(p);
    else if (!b && p.id !== a.id) setB(p);
  };

  const resetForm = () => {
    setA(null); setB(null); setPref(null);
    setText(''); setAC(true); setStatus('');
  };

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
        
        <SideBar logoImg={logoImg} logged={logged} isAdmin={isAdmin} />
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
            <ReviewForm
              a={a}
              b={b}
              pref={pref}
              setPref={setPref}
              text={text}
              setText={setText}
              allowC={allowC}
              setAC={setAC}
              handleSubmit={handleSubmit}
              status={status}
            />
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
