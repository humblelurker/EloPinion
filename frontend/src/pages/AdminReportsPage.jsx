import { useEffect, useState } from "react";
import { useNavigate, Link }   from "react-router-dom";
import logoImg from '../assets/logo.png';

export default function AdminReportsPage() {
  const [items, setItems] = useState([]);
  const navigate = useNavigate();

  /* carga inicial */
  useEffect(() => {
    fetch("/api/reports/pending/", { credentials: "include" })
      .then(r => {
        if (r.status === 401) {
          navigate("/auth");
          return [];
        }
        if (r.status === 403) {
          alert("Solo administradores");
          navigate("/");
          return [];
        }
        return r.json();
      })
      .then(setItems)
      .catch(console.error);
  }, [navigate]);

  async function moderate(id, status) {
    const ok = window.confirm(`Marcar reporte #${id} como ${status}?`);
    if (!ok) return;

    const resp = await fetch(`/api/reports/${id}/`, {
      method: "PATCH",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
    if (resp.ok) {
      setItems(arr => arr.filter(r => r.id !== id));   // quita de la lista
    } else {
      alert("Error al actualizar");
    }
  }

  /* vista */
  return (
    <div className="layout">
      <aside className="sidebar">
        <img src={logoImg} alt="EloPinion" className="sidebar-logo" />
        <nav><Link to="/">Inicio</Link></nav>
        <nav><Link to="/auth">Login / Registro</Link></nav>
        <nav><Link to="/my-reviews">Mis reseñas</Link></nav>
        <nav><Link to="/moderate">Moderar reportes</Link></nav>
      </aside>

      <main className="content">
        <h1>Reportes pendientes</h1>

        {!items.length && <p>No hay reportes pendientes 🎉</p>}

        {items.map(rep => (
          <div key={rep.id} className="report-card">
            <p>
              <b>#{rep.id}</b> • 
              <b>{rep.reviewer}</b> reseña {rep.productoA} vs {rep.productoB} <br/>
              Ganador: <b>{rep.ganador}</b><br/>
              Reportado por: <b>{rep.reporter}</b>
            </p>
            {rep.reason && <p><i>Motivo:</i> {rep.reason}</p>}

            <div className="report-actions">
              <button onClick={() => moderate(rep.id, "Aprobada")}>Aprobar</button>
              <button onClick={() => moderate(rep.id, "Rechazada")}>Rechazar</button>
            </div>
          </div>
        ))}
      </main>
    </div>
  );
}
