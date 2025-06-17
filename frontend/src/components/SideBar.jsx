import React from "react";
import { Link } from "react-router-dom";
import './SideBar.css'; // Assuming you have a CSS file for styling

function SideBar({logoImg, logged, isAdmin}) {
        return (
        <aside className="sidebar">
          <img src={logoImg} alt="EloPinion" className="sidebar-logo" />
          <nav><Link to="/">Inicio</Link></nav>
          <nav><Link to="/auth">Login / Registro</Link></nav>
          <nav><Link to="/statistics">Informes</Link></nav>
              {/* link visible sólo logeado */}
          <nav>{logged && <Link to="/my-reviews">Mis reseñas</Link>}</nav>
          {isAdmin && <nav><Link to="/moderate">Moderar reportes</Link></nav>}
        </aside>
        )
}

export default SideBar;