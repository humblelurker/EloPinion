import { useState, useEffect } from "react";
import RegisterForm from "../components/RegisterForm";
import LoginForm from "../components/LoginForm";
import SideBar from "../components/SideBar.jsx";

import "./AuthPage.css";
import logoImg from "../assets/logo.png";

/* Utilidad: consulta sesión */
const fetchWhoami = () =>
  fetch("/api/whoami/", { credentials: "include" })
    .then((r) => (r.ok ? r.json() : {}))
    .catch(() => ({}));

export default function AuthPage() {
  const [user, setUser] = useState(null);
  const [logged, setLogged] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  /* ¿Ya había sesión iniciada? */
  useEffect(() => {
    fetchWhoami().then(({ user, is_admin }) => {
      if (user) {
        setUser(user);
        setLogged(true);
        setIsAdmin(is_admin);
      }
    });
  }, []);

  /* callback desde LoginForm */
  const handleLoginSuccess = (username) => {
    setUser(username);
    setLogged(true);
    /* Si quieres: volver a pedir /whoami/ para conocer isAdmin */
    fetchWhoami().then(({ is_admin }) => setIsAdmin(is_admin));
  };

  return (
    <div id="root">
      <div className="layout">
        {/* barra lateral reutilizada */}
        <SideBar logoImg={logoImg} logged={logged} isAdmin={isAdmin} />

        <main className="content">
          <div className="auth-wrapper">
            <div className="auth-card">
              {!user ? (
                <>
                  <img
                    src={logoImg}
                    alt="EloPinion"
                    style={{ width: "100%", marginBottom: "1rem" }}
                  />
                  <RegisterForm />
                  <hr style={{ margin: "1.5rem 0", opacity: 0.2 }} />
                  <LoginForm onSuccess={handleLoginSuccess} />
                </>
              ) : (
                <h2>Sesión iniciada como {user}</h2>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
