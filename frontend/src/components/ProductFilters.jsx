import React from 'react';
import './ProductFilters.css';

function ProductFilters({ categories, selectedCat, onCategoryChange, searchTerm, onSearchChange }) {
  return (
    <div className="product-filters">
      <input
        type="text"
        placeholder="Buscar producto..."
        value={searchTerm}
        onChange={(e) => onSearchChange(e.target.value)}
      />

      <select value={selectedCat} onChange={(e) => onCategoryChange(e.target.value)}>
        <option value="">Todas las categorías</option>
        {categories.map((cat) => (
          <option key={cat} value={cat}>
            {cat}
          </option>
        ))}
      </select>
    </div>
  );
}

export default ProductFilters;