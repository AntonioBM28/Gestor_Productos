'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import AuthGuard from '@/components/AuthGuard';
import api from '@/lib/api';

function OrdersContent() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getOrders().then(data => {
      setOrders(data.orders || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const formatPrice = (p) =>
    new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(p);

  const formatDate = (d) =>
    new Date(d).toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });

  const statusBadge = (status) => {
    const map = {
      pending: { class: 'badge-warning', text: '⏳ Pendiente' },
      confirmed: { class: 'badge-success', text: '✅ Confirmado' },
      cancelled: { class: 'badge-danger', text: '❌ Cancelado' },
    };
    const s = map[status] || map.pending;
    return <span className={`badge ${s.class}`}>{s.text}</span>;
  };

  if (loading) return <div className="container" style={{ padding: '60px 24px' }}>{[1,2].map(i => <div key={i} className="skeleton" style={{ height: 120, borderRadius: 16, marginBottom: 16 }} />)}</div>;

  return (
    <div className="container page-enter" style={{ padding: '40px 24px' }}>
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="heading-lg"
      >
        📋 Mis <span className="gradient-text">Pedidos</span>
      </motion.h1>

      {orders.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '80px 0', color: 'var(--text-muted)' }}>
          <span style={{ fontSize: '3rem' }}>📭</span>
          <h3 style={{ marginTop: 16, color: 'var(--text-secondary)' }}>No tienes pedidos aún</h3>
        </div>
      ) : (
        <div className="orders-list">
          {orders.map((order, i) => (
            <motion.div
              key={order.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              className="order-card glass-card"
            >
              <div className="order-header">
                <div>
                  <span className="order-id">Pedido #{order.id}</span>
                  <span className="order-date">{formatDate(order.created_at)}</span>
                </div>
                <div className="order-status">
                  {statusBadge(order.status)}
                </div>
              </div>

              <div className="order-items">
                {order.items.map(item => (
                  <div key={item.id} className="order-item">
                    <span className="oi-name">{item.product_name}</span>
                    <span className="oi-qty">×{item.quantity}</span>
                    <span className="oi-price">{formatPrice(item.price_at_purchase * item.quantity)}</span>
                  </div>
                ))}
              </div>

              <div className="order-footer">
                <div>
                  <span className="ref-label">Referencia: </span>
                  <code className="ref-code">{order.reference_code}</code>
                </div>
                <span className="order-total">{formatPrice(order.total)}</span>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      <style jsx>{`
        .orders-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
          margin-top: 32px;
        }
        .order-card {
          padding: 24px;
        }
        .order-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
          flex-wrap: wrap;
          gap: 8px;
        }
        .order-id {
          font-weight: 700;
          font-size: 1rem;
          display: block;
        }
        .order-date {
          font-size: 0.8rem;
          color: var(--text-muted);
        }
        .order-items {
          border-top: 1px solid var(--border-glass);
          border-bottom: 1px solid var(--border-glass);
          padding: 12px 0;
          margin-bottom: 16px;
        }
        .order-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 6px 0;
          font-size: 0.9rem;
        }
        .oi-name {
          flex: 1;
          color: var(--text-secondary);
        }
        .oi-qty {
          color: var(--text-muted);
          font-size: 0.85rem;
        }
        .oi-price {
          font-weight: 600;
          color: var(--text-primary);
          min-width: 100px;
          text-align: right;
        }
        .order-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 8px;
        }
        .ref-label {
          font-size: 0.8rem;
          color: var(--text-muted);
        }
        .ref-code {
          font-size: 0.85rem;
          color: var(--accent-primary-light);
          background: var(--bg-secondary);
          padding: 2px 8px;
          border-radius: 4px;
        }
        .order-total {
          font-family: 'Outfit', sans-serif;
          font-size: 1.3rem;
          font-weight: 700;
          color: var(--accent-primary-light);
        }
      `}</style>
    </div>
  );
}

export default function OrdersPage() {
  return (
    <AuthGuard requireAuth>
      <OrdersContent />
    </AuthGuard>
  );
}
