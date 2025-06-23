import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import SideBar from "../components/SideBar.jsx";
import logoImg from "../assets/logo.png";
import "./AdminReportsPage.css";

export default function AdminReportsPage() {
  const [items, setItems] = useState([]);
  const [userInfo, setUserInfo] = useState({ logged: false, isAdmin: false });
  const navigate = useNavigate();

  /* carga inicial + verificación de sesión */
  useEffect(() => {
    fetch("/api/whoami/", { credentials: "include" })
      .then((r) => (r.ok ? r.json() : {}))
      .then(({ user, is_admin }) => {
        setUserInfo({ logged: !!user, isAdmin: is_admin });
      });

    fetch("/api/reports/pending/", { credentials: "include" })
      .then((r) => {
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
      setItems((arr) => arr.filter((r) => r.id !== id));
    } else {
      alert("Error al actualizar");
    }
  }

  /* vista */
  return (
    <div className="layout">
      <SideBar
        logoImg={logoImg}
        logged={userInfo.logged}
        isAdmin={userInfo.isAdmin}
      />

      <main className="content">
        <h1>Reportes pendientes</h1>

        {!items.length && <p>No hay reportes pendientes 🎉</p>}

        {items.map((rep) => (
          <div key={rep.id} className="report-card">
            <p>
              <b>#{rep.id}</b> • <b>{rep.reviewer}</b> reseña {rep.productoA} vs{" "}
              {rep.productoB}
              <br />
              Ganador: <b>{rep.ganador}</b>
              <br />
              Reportado por: <b>{rep.reporter}</b>
            </p>
            {rep.reason && (
              <p>
                <i>Motivo:</i> {rep.reason}
              </p>
            )}

            <div className="report-actions">
              <button onClick={() => moderate(rep.id, "Aprobada")}>
                Aprobar
              </button>
              <button onClick={() => moderate(rep.id, "Rechazada")}>
                Rechazar
              </button>
            </div>
          </div>
        ))}
      </main>
    </div>
  );
}
