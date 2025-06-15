/* Página: Mis reseñas
   Muestra únicamente las reseñas creadas por el usuario logeado.
   Reutiliza la misma sidebar / estilos de la pantalla principal. */

import "../App.css";                         // mismos estilos globales
import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import Feed from "../components/Feed.jsx";
import logoImg from "../assets/logo.png";

/* pequeña utilidad: ¿hay sesión? */
const fetchLogin = () =>
  fetch("/api/whoami/", { credentials: "include" })
    .then((r) => r.ok)
    .catch(() => false);

export default function MyReviewsPage() {
  const [logged, setLogged] = useState(false);
  const navigate = useNavigate();

  /* ─── verifica sesión al montar ─── */
  useEffect(() => {
    fetchLogin().then((ok) => {
      if (!ok) navigate("/auth");
      setLogged(ok);
    });
  }, []);

  if (!logged) return null;          // mientras redirige / comprueba

  return (
    <div id="root">
      <div className="layout">
        {/* ────────────── Sidebar ────────────── */}
        <aside className="sidebar">
          <img src={logoImg} alt="EloPinion" className="sidebar-logo" />

          <nav>
            <Link to="/">Inicio</Link>
          </nav>

          <nav>
            <Link to="/auth">Login / Registro</Link>
          </nav>

          <nav>
            <Link to="/my-reviews">Mis reseñas</Link>
          </nav>
        </aside>

        {/* ────────────── Contenido ───────────── */}
        <main className="content" style={{ width: "100%", maxWidth: 800 }}>
          <h1 style={{ textAlign: "center", marginBottom: "1rem" }}>
            Mis reseñas
          </h1>

          {/* Feed reutilizable apuntando a la nueva ruta API */}
          <Feed api="/api/my-reviews/" />
        </main>
      </div>
    </div>
  );
}
