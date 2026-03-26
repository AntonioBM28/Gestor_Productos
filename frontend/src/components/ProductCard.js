'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

export default function ProductCard({ product, index = 0, onAddedToCart }) {
  const { isAuthenticated, isAdmin } = useAuth();
  const router = useRouter();
  const [adding, setAdding] = useState(false);
  const [imgError, setImgError] = useState(false);

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    setAdding(true);
    try {
      await api.addToCart(product.id, 1);
      window.dispatchEvent(new Event('cart-updated'));
      if (onAddedToCart) onAddedToCart();
    } catch (err) {
      alert(err.message || 'Error adding to cart');
    }
    setAdding(false);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN',
    }).format(price);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.08 }}
      whileHover={{ y: -8, transition: { duration: 0.3 } }}
      className="product-card glass-card"
    >
      <div className="product-image-wrap">
        {!imgError && product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="product-image"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="product-image-placeholder">📦</div>
        )}
        {product.category && (
          <span className="product-category">{product.category}</span>
        )}
        {product.stock <= 5 && product.stock > 0 && (
          <span className="stock-warning">¡Últimas {product.stock}!</span>
        )}
        {product.stock === 0 && (
          <span className="out-of-stock">Agotado</span>
        )}
      </div>

      <div className="product-info">
        <h3 className="product-name">{product.name}</h3>
        <p className="product-desc">
          {product.description?.substring(0, 100)}
          {product.description?.length > 100 ? '...' : ''}
        </p>
        <div className="product-footer">
          <span className="product-price">{formatPrice(product.price)}</span>
          {!isAdmin && product.stock > 0 && (
            <motion.button
              whileTap={{ scale: 0.95 }}
              className="btn btn-primary btn-sm add-btn"
              onClick={handleAddToCart}
              disabled={adding}
            >
              {adding ? '...' : isAuthenticated ? '🛒 Agregar' : '🔒 Iniciar sesión'}
            </motion.button>
          )}
        </div>
      </div>

      <style jsx>{`
        .product-card {
          overflow: hidden;
          display: flex;
          flex-direction: column;
          cursor: pointer;
        }
        .product-image-wrap {
          position: relative;
          width: 100%;
          height: 200px;
          overflow: hidden;
          background: var(--bg-secondary);
        }
        .product-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.5s ease;
        }
        .product-card:hover .product-image {
          transform: scale(1.08);
        }
        .product-image-placeholder {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 3rem;
          background: var(--bg-tertiary);
        }
        .product-category {
          position: absolute;
          top: 12px;
          left: 12px;
          padding: 4px 12px;
          background: rgba(124, 58, 237, 0.85);
          color: white;
          font-size: 0.7rem;
          font-weight: 600;
          border-radius: 20px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          backdrop-filter: blur(10px);
        }
        .stock-warning {
          position: absolute;
          top: 12px;
          right: 12px;
          padding: 4px 10px;
          background: rgba(245, 158, 11, 0.85);
          color: white;
          font-size: 0.7rem;
          font-weight: 600;
          border-radius: 20px;
          backdrop-filter: blur(10px);
        }
        .out-of-stock {
          position: absolute;
          top: 12px;
          right: 12px;
          padding: 4px 10px;
          background: rgba(239, 68, 68, 0.85);
          color: white;
          font-size: 0.7rem;
          font-weight: 600;
          border-radius: 20px;
        }
        .product-info {
          padding: 20px;
          flex: 1;
          display: flex;
          flex-direction: column;
        }
        .product-name {
          font-family: 'Outfit', sans-serif;
          font-size: 1.1rem;
          font-weight: 600;
          margin-bottom: 8px;
          color: var(--text-primary);
        }
        .product-desc {
          font-size: 0.85rem;
          color: var(--text-muted);
          line-height: 1.5;
          flex: 1;
          margin-bottom: 16px;
        }
        .product-footer {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
        }
        .product-price {
          font-family: 'Outfit', sans-serif;
          font-size: 1.3rem;
          font-weight: 700;
          color: var(--accent-primary-light);
        }
      `}</style>
    </motion.div>
  );
}
