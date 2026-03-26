'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import ProductCard from '@/components/ProductCard';
import api from '@/lib/api';

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await api.getProducts(selectedCategory, search);
      setProducts(data.products || []);
    } catch { /**/ }
    setLoading(false);
  };

  useEffect(() => {
    loadProducts();
  }, [selectedCategory]);

  useEffect(() => {
    api.getCategories().then(data => setCategories(data.categories || [])).catch(() => {});
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    loadProducts();
  };

  return (
    <div className="page-enter container" style={{ padding: '40px 24px' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="products-header"
      >
        <h1 className="heading-lg">
          Nuestros <span className="gradient-text">Productos</span>
        </h1>
        <p style={{ color: 'var(--text-secondary)', marginTop: 8 }}>
          Explora nuestra colección de tecnología premium
        </p>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="filters"
      >
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            className="form-input search-input"
            placeholder="🔍 Buscar productos..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit" className="btn btn-primary btn-sm">Buscar</button>
        </form>

        <div className="category-filters">
          <button
            className={`category-chip ${!selectedCategory ? 'active' : ''}`}
            onClick={() => setSelectedCategory('')}
          >
            Todos
          </button>
          {categories.map(cat => (
            <button
              key={cat}
              className={`category-chip ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Products Grid */}
      {loading ? (
        <div className="product-grid">
          {[1,2,3,4,5,6].map(i => (
            <div key={i} className="skeleton" style={{ height: 350, borderRadius: 16 }} />
          ))}
        </div>
      ) : products.length === 0 ? (
        <div className="empty-state">
          <span style={{ fontSize: '3rem' }}>📭</span>
          <h3>No se encontraron productos</h3>
          <p>Intenta con otra búsqueda o categoría</p>
        </div>
      ) : (
        <div className="product-grid">
          {products.map((product, i) => (
            <ProductCard key={product.id} product={product} index={i} />
          ))}
        </div>
      )}

      <style jsx>{`
        .products-header {
          margin-bottom: 32px;
        }
        .filters {
          margin-bottom: 32px;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .search-form {
          display: flex;
          gap: 12px;
          max-width: 500px;
        }
        .search-input {
          flex: 1;
        }
        .category-filters {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }
        .category-chip {
          padding: 8px 18px;
          border-radius: 50px;
          border: 1px solid var(--border-glass);
          background: var(--bg-secondary);
          color: var(--text-secondary);
          font-size: 0.85rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
          font-family: 'Inter', sans-serif;
        }
        .category-chip:hover {
          border-color: var(--accent-primary);
          color: var(--text-primary);
        }
        .category-chip.active {
          background: var(--accent-primary);
          border-color: var(--accent-primary);
          color: white;
        }
        .empty-state {
          text-align: center;
          padding: 80px 0;
          color: var(--text-muted);
        }
        .empty-state h3 {
          margin: 16px 0 8px;
          color: var(--text-secondary);
        }
      `}</style>
    </div>
  );
}
