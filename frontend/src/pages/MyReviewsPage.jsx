/* Página: Mis reseñas – muestra únicamente las reseñas propias */
import "../App.css";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Feed from "../components/Feed.jsx";
import SideBar from "../components/SideBar.jsx";
import logoImg from "../assets/logo.png";

/* Comprueba sesión consultando al backend */
const fetchLogin = () =>
  fetch("/api/whoami/", { credentials: "include" })
    .then((r) => (r.ok ? r.json() : { is_admin: false }))
    .catch(() => ({ is_admin: false }));

export default function MyReviewsPage() {
  const [logged, setLogged] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const navigate = useNavigate();

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
        <SideBar logoImg={logoImg} logged={logged} isAdmin={isAdmin} />

        <main className="content" style={{ width: "100%", maxWidth: 800 }}>
          <h1 style={{ textAlign: "center", marginBottom: "1rem" }}>
            Mis reseñas
          </h1>

          {/* Feed reutilizable – permite eliminar, no reportar */}
          <Feed api="/api/my-reviews/" canDelete={true} allowReport={false} />
        </main>
      </div>
    </div>
  );
}
