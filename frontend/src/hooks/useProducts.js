

import { useEffect, useState } from 'react';

function useProducts() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/products')
      .then((res) => {
        if (!res.ok) {
          throw new Error('Error al cargar productos');
        }
        return res.json();
      })
      .then((data) => {
        setProducts(data);
        const uniqueCategories = Array.from(new Set(data.map((p) => p.category)));
        setCategories(uniqueCategories);
      })
      .catch((err) => {
        console.error('Error fetching products:', err);
        setError(err.message);
      });
  }, []);

  return { products, categories, error };
}

export default useProducts;