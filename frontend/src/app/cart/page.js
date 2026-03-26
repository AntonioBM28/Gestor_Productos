'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import AuthGuard from '@/components/AuthGuard';
import api from '@/lib/api';

function CartContent() {
  const [cart, setCart] = useState({ items: [], total: 0, count: 0 });
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const loadCart = async () => {
    try {
      const data = await api.getCart();
      setCart(data);
    } catch { /**/ }
    setLoading(false);
  };

  useEffect(() => { loadCart(); }, []);

  const updateQty = async (itemId, qty) => {
    try {
      if (qty <= 0) {
        await api.removeFromCart(itemId);
      } else {
        await api.updateCartItem(itemId, qty);
      }
      await loadCart();
      window.dispatchEvent(new Event('cart-updated'));
    } catch (err) { alert(err.message); }
  };

  const removeItem = async (itemId) => {
    try {
      await api.removeFromCart(itemId);
      await loadCart();
      window.dispatchEvent(new Event('cart-updated'));
    } catch (err) { alert(err.message); }
  };

  const formatPrice = (p) =>
    new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(p);

  if (loading) {
    return (
      <div className="container" style={{ padding: '40px 24px' }}>
        {[1,2,3].map(i => <div key={i} className="skeleton" style={{ height: 100, borderRadius: 16, marginBottom: 16 }} />)}
      </div>
    );
  }

  return (
    <div className="container page-enter" style={{ padding: '40px 24px' }}>
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="heading-lg"
      >
        🛒 Tu <span className="gradient-text">Carrito</span>
      </motion.h1>

      {cart.items.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="empty-cart"
        >
          <span style={{ fontSize: '4rem' }}>🛒</span>
          <h3>Tu carrito está vacío</h3>
          <p>Agrega productos para empezar a comprar</p>
          <button className="btn btn-primary" onClick={() => router.push('/products')}>
            Ver Productos
          </button>
        </motion.div>
      ) : (
        <div className="cart-layout">
          <div className="cart-items">
            <AnimatePresence>
              {cart.items.map((item, i) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: i * 0.05 }}
                  className="cart-item glass-card"
                >
                  <div className="item-image">
                    {item.product?.image_url ? (
                      <img src={item.product.image_url} alt={item.product.name} />
                    ) : (
                      <span>📦</span>
                    )}
                  </div>
                  <div className="item-info">
                    <h3>{item.product?.name}</h3>
                    <p className="item-price">{formatPrice(item.product?.price || 0)}</p>
                  </div>
                  <div className="item-controls">
                    <button className="qty-btn" onClick={() => updateQty(item.id, item.quantity - 1)}>−</button>
                    <span className="qty-value">{item.quantity}</span>
                    <button className="qty-btn" onClick={() => updateQty(item.id, item.quantity + 1)}>+</button>
                  </div>
                  <div className="item-subtotal">
                    {formatPrice((item.product?.price || 0) * item.quantity)}
                  </div>
                  <button className="remove-btn" onClick={() => removeItem(item.id)}>✕</button>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="cart-summary glass-card"
          >
            <h3 className="heading-md">Resumen</h3>
            <div className="summary-row">
              <span>Productos ({cart.count})</span>
              <span>{formatPrice(cart.total)}</span>
            </div>
            <div className="summary-row">
              <span>Envío</span>
              <span style={{ color: 'var(--accent-success)' }}>Gratis</span>
            </div>
            <div className="summary-divider" />
            <div className="summary-row total-row">
              <span>Total</span>
              <span className="gradient-text">{formatPrice(cart.total)}</span>
            </div>
            <motion.button
              whileTap={{ scale: 0.98 }}
              className="btn btn-primary"
              style={{ width: '100%', marginTop: 16 }}
              onClick={() => router.push('/checkout')}
            >
              Proceder al Pago 💳
            </motion.button>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'center', marginTop: 12 }}>
              🏪 Pago disponible en OXXO y puntos de referencia
            </p>
          </motion.div>
        </div>
      )}

      <style jsx>{`
        .empty-cart {
          text-align: center;
          padding: 80px 0;
          color: var(--text-muted);
        }
        .empty-cart h3 {
          margin: 16px 0 8px;
          color: var(--text-secondary);
        }
        .empty-cart .btn {
          margin-top: 24px;
        }
        .cart-layout {
          display: grid;
          grid-template-columns: 1fr 360px;
          gap: 32px;
          margin-top: 32px;
        }
        .cart-items {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .cart-item {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 16px;
        }
        .item-image {
          width: 80px;
          height: 80px;
          border-radius: var(--radius-md);
          overflow: hidden;
          background: var(--bg-secondary);
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 2rem;
        }
        .item-image img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .item-info {
          flex: 1;
          min-width: 0;
        }
        .item-info h3 {
          font-size: 0.95rem;
          font-weight: 600;
          margin-bottom: 4px;
        }
        .item-price {
          color: var(--text-muted);
          font-size: 0.85rem;
        }
        .item-controls {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .qty-btn {
          width: 32px;
          height: 32px;
          border-radius: 8px;
          border: 1px solid var(--border-glass);
          background: var(--bg-secondary);
          color: var(--text-primary);
          font-size: 1rem;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }
        .qty-btn:hover {
          border-color: var(--accent-primary);
          background: var(--bg-tertiary);
        }
        .qty-value {
          font-weight: 600;
          min-width: 24px;
          text-align: center;
        }
        .item-subtotal {
          font-weight: 600;
          color: var(--accent-primary-light);
          font-size: 0.95rem;
          min-width: 100px;
          text-align: right;
        }
        .remove-btn {
          background: none;
          border: none;
          color: var(--text-muted);
          font-size: 1.1rem;
          cursor: pointer;
          padding: 4px;
          transition: color 0.2s;
        }
        .remove-btn:hover {
          color: var(--accent-danger);
        }
        .cart-summary {
          padding: 28px;
          height: fit-content;
          position: sticky;
          top: 100px;
        }
        .cart-summary h3 {
          margin-bottom: 20px;
        }
        .summary-row {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          font-size: 0.95rem;
          color: var(--text-secondary);
        }
        .summary-divider {
          height: 1px;
          background: var(--border-glass);
          margin: 12px 0;
        }
        .total-row {
          font-size: 1.2rem;
          font-weight: 700;
          color: var(--text-primary);
        }
        @media (max-width: 768px) {
          .cart-layout {
            grid-template-columns: 1fr;
          }
          .cart-item {
            flex-wrap: wrap;
          }
          .item-subtotal {
            min-width: auto;
          }
        }
      `}</style>
    </div>
  );
}

export default function CartPage() {
  return (
    <AuthGuard requireAuth>
      <CartContent />
    </AuthGuard>
  );
}
