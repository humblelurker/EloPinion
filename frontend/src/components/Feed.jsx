import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Feed.css";

/**
 * Props
 * ─────────────────────────────────────────────────────────────
 * api         – URL que devuelve las reseñas (por defecto /api/feed/)
 * canDelete   – true  ⇒ muestra botón “Eliminar” y lo llama vía DELETE
 * allowReport – false ⇒ oculta el botón “Reportar”
 */
export default function Feed({
  api = "/api/feed/",
  canDelete = false,
  allowReport = true,
}) {
  const [items,  setItems]  = useState([]);
  const [drafts, setDrafts] = useState({});
  const navigate = useNavigate();

  /* ─── carga inicial ─────────────────────────── */
  useEffect(() => {
    fetch(api, { credentials: "include" })
      .then((r) => {
        if (r.status === 401) {
          navigate("/auth");
          return [];
        }
        return r.json();
      })
      .then(setItems)
      .catch(console.error);
  }, [api, navigate]);

  /* ─── helpers ───────────────────────────────── */
  const loserOf = (r) =>
    r.preferred_product === r.product_a ? r.product_b : r.product_a;

  const handleDraft = (id, text) =>
    setDrafts((d) => ({ ...d, [id]: text }));

  /* ─── comentar ──────────────────────────────── */
  async function sendComment(reviewId) {
    const text = (drafts[reviewId] || "").trim();
    if (!text) return;

    const resp = await fetch("/api/comments/", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ review: reviewId, text }),
    });

    if (resp.status === 401) {
      alert("Debes iniciar sesión");
      return;
    }
    if (!resp.ok) {
      alert("Error al comentar");
      return;
    }
    const newComment = await resp.json();
    setItems((arr) =>
      arr.map((r) =>
        r.id === reviewId
          ? { ...r, comments: [...(r.comments || []), newComment] }
          : r
      )
    );
    handleDraft(reviewId, "");
  }

  /* ─── reportar ──────────────────────────────── */
  async function reportReview(reviewId) {
    if (!window.confirm("¿Reportar esta reseña?")) return;
    const resp = await fetch("/api/reports/", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ review: reviewId, reason: "" }),
    });
    alert(resp.ok ? "Reporte enviado ✔" : "Error al reportar");
  }

  /* ─── eliminar propia ───────────────────────── */
  async function deleteReview(reviewId) {
    if (!window.confirm("¿Eliminar esta reseña? Esta acción es permanente.")) return;
    const resp = await fetch(`/api/my-reviews/${reviewId}/`, {
      method: "DELETE",
      credentials: "include",
    });
    if (resp.status === 204) {
      setItems((arr) => arr.filter((r) => r.id !== reviewId));
    } else if (resp.status === 401) {
      alert("Debes iniciar sesión");
    } else {
      alert("Error al eliminar reseña");
    }
  }

  /* ─── render ────────────────────────────────── */
  if (!items.length)
    return <p className="feed-loading">Cargando reseñas…</p>;

  return (
    <ul className="feed-list">
      {items.map((r) => (
        <li key={r.id} className="feed-item">
          <div className="feed-header">
            <b>{r.user}</b> prefirió <b>{r.preferred_product}</b> sobre{" "}
            {loserOf(r)}
          </div>

          {r.justification && (
            <p className="feed-justification">“{r.justification}”</p>
          )}

          {!r.allow_comments && (
            <span className="feed-disabled">Comentarios desactivados</span>
          )}

          {/* comentarios existentes */}
          {r.comments?.length > 0 && (
            <ul className="feed-comments">
              {r.comments.map((c) => (
                <li key={c.id}>
                  <b>{c.user}</b>: {c.text}
                </li>
              ))}
            </ul>
          )}

          {/* formulario para comentar */}
          {r.allow_comments && (
            <div className="feed-form">
              <textarea
                rows={2}
                placeholder="Escribe un comentario…"
                value={drafts[r.id] || ""}
                onChange={(e) => handleDraft(r.id, e.target.value)}
              />
              <button
                className="feed-comment-btn"
                onClick={() => sendComment(r.id)}
              >
                Publicar comentario
              </button>
            </div>
          )}

          {/* ─── acciones ─── */}
          <div className="feed-actions">
            {allowReport && (
              <button
                className="feed-report-btn"
                onClick={() => reportReview(r.id)}
              >
                Reportar
              </button>
            )}

            {canDelete && (
              <button
                className="feed-delete-btn"
                onClick={() => deleteReview(r.id)}
              >
                Eliminar
              </button>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
