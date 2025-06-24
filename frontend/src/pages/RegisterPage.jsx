import React from 'react';
import RegisterForm from '../components/RegisterForm';
import SideBar from '../components/SideBar';
import logoImg from '../assets/logo.png';
import { Link } from 'react-router-dom';
import './AuthPage.css';

export default function RegisterPage() {
  return (
    <div className="layout">
      <SideBar logoImg={logoImg} />
      <main className="content">
        <div className="auth-wrapper">
          <div className="auth-card">
            <img src={logoImg} alt="EloPinion" style={{ width: "100%", marginBottom: "1rem" }} />
            <h3 style={{ color: "white", marginBottom: "1rem" }}>Crear cuenta</h3>
            <RegisterForm />
            <p style={{ marginTop: "1rem", textAlign: "center" }}>
              ¿Ya tienes cuenta?{" "}
              <Link to="/auth" style={{ color: "#5865f2", fontWeight: "bold" }}>
                Inicia sesión aquí
              </Link>
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}