/* Página: Mis reseñas
   Muestra únicamente las reseñas creadas por el usuario logeado.
   Reutiliza la misma sidebar / estilos de la pantalla principal. */

import "../App.css";
import { useState, useEffect } from "react";
import { Link, useNavigate }   from "react-router-dom";
import Feed                    from "../components/Feed.jsx";
import logoImg                 from "../assets/logo.png";

/* Comprueba sesión consultando al backend */
const fetchLogin = () =>
  fetch("/api/whoami/", { credentials: "include" })
    .then((r) => (r.ok ? r.json() : { is_admin: false }))
    .catch(() => ({ is_admin: false }));

export default function MyReviewsPage() {
  const [logged,   setLogged]   = useState(false);
  const [isAdmin,  setIsAdmin]  = useState(false);
  const navigate               = useNavigate();

  /* ─── verifica sesión al montar ─── */
  useEffect(() => {
    fetchLogin().then(({ user, is_admin }) => {
      setLogged(!!user);
      setIsAdmin(is_admin);
      if (!user) navigate("/auth");
    });
  }, [navigate]);

  if (!logged) return null; // mientras redirige / comprueba

  return (
    <div id="root">
      <div className="layout">
        {/* ────────────── Sidebar ────────────── */}
        <aside className="sidebar">
          <img src={logoImg} alt="EloPinion" className="sidebar-logo" />

          <nav><Link to="/">Inicio</Link></nav>
          <nav><Link to="/auth">Login / Registro</Link></nav>
          <nav><Link to="/my-reviews">Mis reseñas</Link></nav>
          {isAdmin && (
            <nav><Link to="/moderate">Moderar reportes</Link></nav>
          )}
        </aside>

        {/* ────────────── Contenido ───────────── */}
        <main className="content" style={{ width: "100%", maxWidth: 800 }}>
          <h1 style={{ textAlign: "center", marginBottom: "1rem" }}>
            Mis reseñas
          </h1>

          {/* Feed reutilizable – permite eliminar, no reportar */}
          <Feed
            api="/api/my-reviews/"
            canDelete={true}
            allowReport={false}
          />
        </main>
      </div>
    </div>
  );
}
