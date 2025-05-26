import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Feed() {
  const [items, setItems] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("/api/feed/", { credentials: "include" })
      .then(r => {
        if (r.status === 401) {
          navigate("/auth");
          return [];
        }
        return r.json();
      })
      .then(setItems)
      .catch(console.error);
  }, [navigate]);

  if (!items.length) return <p>Cargando feed…</p>;

  return (
    <ul style={{ listStyle: "none", padding: 0 }}>
      {items.map(r => {
        const loser =
          r.preferred_product__name === r.product_a__name
            ? r.product_b__name
            : r.product_a__name;

        return (
          <li key={r.id} style={{ margin: "1rem 0", padding: ".5rem", background: "#2a2c3a", borderRadius: "6px" }}>
            <div>
              <b>{r.user__username}</b> prefirió{" "}
              <b>{r.preferred_product__name}</b> sobre {loser}
            </div>
            {r.justification && (
              <p style={{ margin: "0.5rem 0 0", fontStyle: "italic", opacity: 0.8 }}>
                “{r.justification}”
              </p>
            )}
          </li>
        );
      })}
    </ul>
  );
}
