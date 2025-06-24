import { useState } from "react";
import LoginForm from "../components/LoginForm";
import SideBar from "../components/SideBar.jsx";

import "./AuthPage.css";
import logoImg from "../assets/logo.png";

// No session check needed for login-only page

export default function AuthPage() {
  const [email, setEmail] = useState(null);

  /* callback desde LoginForm */
  const handleLoginSuccess = (email) => setEmail(email);

  return (
    <div className="layout">
      {/* barra lateral reutilizada */}
      <SideBar logoImg={logoImg} />

      <main className="content">
        <div className="auth-wrapper">
          <div className="auth-card">
            {!email ? (
              <>
                <img
                  src={logoImg}
                  alt="EloPinion"
                  style={{ width: "100%", marginBottom: "1rem" }}
                />
                <LoginForm onSuccess={handleLoginSuccess} />
              </>
            ) : (
              <h2>Sesión iniciada como {email}</h2>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
