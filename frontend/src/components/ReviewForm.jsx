import React from 'react';

export default function ReviewForm({
  a,
  b,
  pref,
  setPref,
  text,
  setText,
  allowC,
  setAC,
  handleSubmit,
  status
}) {
  return (
    <div className="card review-form">
      <h2>Prefiero…</h2>

      <label className="radio-group">
        <span>
          <input
            type="radio"
            name="pref"
            value="A"
            checked={pref === 'A'}
            onChange={() => setPref('A')}
          />{' '}
          {a.name}
        </span>
        <span>
          <input
            type="radio"
            name="pref"
            value="B"
            checked={pref === 'B'}
            onChange={() => setPref('B')}
          />{' '}
          {b.name}
        </span>
      </label>

      <label style={{ margin: '.5rem 0', display: 'block' }}>
        <input
          type="checkbox"
          checked={allowC}
          onChange={e => setAC(e.target.checked)}
        />{' '}
        Permitir comentarios
      </label>

      <textarea
        rows={3}
        placeholder="Justificación (opcional)…"
        value={text}
        onChange={e => setText(e.target.value)}
      />

      <button onClick={handleSubmit}>Enviar reseña</button>
      {status && <p className="status-msg">{status}</p>}
    </div>
  );
}
