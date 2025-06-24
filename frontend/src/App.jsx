import "./App.css";
import { useState } from "react";
import Fuse from "fuse.js";
import logoImg from "./assets/logo.png";
import SideBar from "./components/SideBar.jsx";
import ImageGallery from "./components/ImageGallery.jsx";
import ReviewForm from "./components/ReviewForm.jsx";
import ProductFilters from "./components/ProductFilters.jsx";
import ProductSelector from "./components/ProductSelector.jsx";
import FeedSection from "./components/FeedSection.jsx";
import useAuth from "./hooks/useAuth.js";
import useProducts from "./hooks/useProducts.js";

export default function App() {
  const { user } = useAuth();
  const logged = !!user;
  const isAdmin = user?.is_admin ?? false;
  const { products, categories } = useProducts();

  const [cat, setCat] = useState("");
  const [term, setTerm] = useState("");

  const [a, setA] = useState(null);
  const [b, setB] = useState(null);

  const [pref, setPref] = useState(null);
  const [text, setText] = useState("");
  const [allowC, setAC] = useState(true);
  const [status, setStatus] = useState("");

  const available = products.filter((p) => !cat || p.category === cat);
  const filtered = term
    ? new Fuse(available, { keys: ["name"], threshold: 0.3 })
        .search(term)
        .map((r) => r.item)
    : available;

  const selectProd = (p) => {
    if (!a) setA(p);
    else if (!b && p.id !== a.id) setB(p);
  };

  const resetForm = () => {
    setA(null);
    setB(null);
    setPref(null);
    setText("");
    setAC(true);
    setStatus("");
  };

  async function handleSubmit() {
    if (!a || !b || !pref) {
      setStatus("Completa la selección y elige favorito.");
      return;
    }
    const body = {
      product_a_id: a.id,
      product_b_id: b.id,
      preferred_id: pref === "A" ? a.id : b.id,
      justification: text,
      allow_comments: allowC,
    };
    try {
      const resp = await fetch("/api/submit-review/", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (resp.status === 401) {
        setStatus("🔒 Inicia sesión.");
        return;
      }
      const { status: st } = await resp.json();
      setStatus(st === "ok" ? "✅ Enviada" : "❌ Error");
      if (st === "ok") resetForm();
    } catch {
      setStatus("❌ Error al enviar");
    }
  }

  return (
    <div id="root">
      <div className="layout">
        <SideBar
          logoImg={logoImg}
          logged={logged}
          isAdmin={isAdmin}
        />
        <main className="content">
          <ProductFilters
            categories={categories}
            selectedCat={cat}
            onCategoryChange={(val) => {
              setCat(val);
              resetForm();
            }}
            searchTerm={term}
            onSearchChange={setTerm}
          />

          <ImageGallery />

          <ProductSelector
            products={filtered.slice(0, 6)}
            selectedA={a}
            selectedB={b}
            onSelect={selectProd}
          />

          {(a || b) && (
            <button className="reset-btn" onClick={resetForm}>
              🔄 Reiniciar
            </button>
          )}

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

          <FeedSection logged={logged} />
        </main>
      </div>
    </div>
  );
}
