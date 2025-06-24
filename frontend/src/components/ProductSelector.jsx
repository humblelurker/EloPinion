import React from 'react';
import './ProductSelector.css';
function ProductSelector({ products, selectedA, selectedB, onSelect }) {
  return (
    <div className="product-selector">
      <h2>Selecciona productos para comparar</h2>
      <div className="product-grid">
        {products.map((product) => {
          const isSelectedA = selectedA?.id === product.id;
          const isSelectedB = selectedB?.id === product.id;
          const isSelected = isSelectedA || isSelectedB;

          return (
            <div
              key={product.id}
              className={`product-card ${isSelected ? 'selected' : ''}`}
              onClick={() => onSelect(product)}
            >
              <h3>{product.name}</h3>
              <p>{product.category}</p>
              <img src={product.imageUrl} alt={product.name} />
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ProductSelector;