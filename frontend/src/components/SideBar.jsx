import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import './SideBar.css';

function SideBar({ logoImg }) {
  const { user } = useAuth();
  const logged = !!user;
  const isAdmin = user?.is_admin ?? false;

  return (
    <aside className="sidebar">
      <img src={logoImg} alt="EloPinion" className="sidebar-logo" />

      <nav><Link to="/">Inicio</Link></nav>
      {!logged && <nav><Link to="/auth">Login / Registro</Link></nav>}
      <nav><Link to="/statistics">Informes</Link></nav>

      {logged && (
        <nav><Link to="/my-reviews">Mis reseñas</Link></nav>
      )}

      {isAdmin && (
        <nav><Link to="/moderate">Moderar reportes</Link></nav>
      )}

      {user && (
        <div className="sidebar-user-info">
          <p><strong>{user.email}</strong></p>
          <p style={{ fontSize: "0.85em", opacity: 0.7 }}>ID: {user.id}</p>
        </div>
      )}
    </aside>
  );
}

export default SideBar;