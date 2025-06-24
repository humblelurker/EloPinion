// ejemplo base
import { useEffect, useState } from "react";

export default function ImageGallery() {
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);

  const fetchImages = async () => {
    const res = await fetch(
      `https://api.unsplash.com/search/photos?query=cat&page=${page}&per_page=15&client_id=PrxQNxAxMd0RLMJe_UnSQW0s-Cf_gmqkyiXWTq3fspE`
    );
    const data = await res.json();
    setItems((prev) => [...prev, ...data.results]);
  };

  useEffect(() => {
    fetchImages();
  }, [page]);

  const handleScroll = () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 200) {
      setPage((p) => p + 1);
    }
  };

  useEffect(() => {
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "16px", padding: "1rem" }}>
      {items.slice(0, 15).map((item, idx) => (
        <div key={item.id} style={{ textAlign: "center" }}>
          <img
            src={item.urls.small}
            alt={item.alt_description}
            style={{
              width: "100%",
              height: "200px",
              objectFit: "cover",
              borderRadius: "8px",
            }}
          />
          <p>Producto {idx + 1}</p>
        </div>
      ))}
    </div>
  );
}