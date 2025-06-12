import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Feed.css";

export default function Feed() {
  const [items, setItems] = useState([]);
  const [drafts, setDrafts] = useState({});          // texto x-reseña
  const navigate = useNavigate();

  /* ─── carga inicial ───────────────────────────── */
  useEffect(() => {
    fetch("/api/feed/", { credentials: "include" })
      .then((r) => {
        if (r.status === 401) {
          navigate("/auth");
          return [];
        }
        return r.json();
      })
      .then(setItems)
      .catch(console.error);
  }, []);

  /* ─── helpers ─────────────────────────────────── */
  const loserOf = (r) =>
    r.preferred_product === r.product_a ? r.product_b : r.product_a;

  const handleDraft = (id, text) =>
    setDrafts((d) => ({ ...d, [id]: text }));

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

    // añade el nuevo comentario al estado
    const newComment = await resp.json();
    setItems((arr) =>
      arr.map((r) =>
        r.id === reviewId
          ? { ...r, comments: [...(r.comments || []), newComment] }
          : r
      )
    );
    handleDraft(reviewId, "");       // limpia textarea
  }

  async function reportReview(reviewId) {
    const ok = window.confirm("¿Reportar esta reseña?");
    if (!ok) return;

    const resp = await fetch("/api/reports/", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ review: reviewId, reason: "" }),
    });
    if (resp.ok) alert("Reporte enviado ✔");
    else alert("Error al reportar");
  }

  /* ─── render ──────────────────────────────────── */
  if (!items.length) return <p className="feed-loading">Cargando feed…</p>;

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

          {/* comentarios renderizados */}
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

          {/* botón reportar */}
          <button
            className="feed-report-btn"
            onClick={() => reportReview(r.id)}
          >
            Reportar
          </button>
        </li>
      ))}
    </ul>
  );
}
