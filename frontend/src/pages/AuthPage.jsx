import { useState } from "react";
import RegisterForm from "../components/RegisterForm";
import LoginForm from "../components/LoginForm";
import "./AuthPage.css";               // ←  importa el CSS
import logo from "../assets/logo.png";  

export default function AuthPage() {
  const [user, setUser] = useState(null);

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        {!user ? (
          <>
            <img src={logo} alt="EloPinion" style={{ width: "100%", marginBottom: "1rem" }} />
            <RegisterForm />
            <hr style={{ margin: "1.5rem 0", opacity: 0.2 }} />
            <LoginForm onSuccess={setUser} />
          </>
        ) : (
          <h2>Sesión iniciada como {user}</h2>
        )}
      </div>
    </div>
  );
}
