'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import AuthGuard from '@/components/AuthGuard';
import api from '@/lib/api';

function AdminContent() {
  const [tab, setTab] = useState('products');
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editProduct, setEditProduct] = useState(null);
  const [form, setForm] = useState({ name: '', description: '', price: '', stock: '', image_url: '', category: '' });

  const loadData = async () => {
    setLoading(true);
    try {
      const [pData, oData] = await Promise.all([api.getProducts(), api.getOrders()]);
      setProducts(pData.products || []);
      setOrders(oData.orders || []);
    } catch { /**/ }
    setLoading(false);
  };

  useEffect(() => { loadData(); }, []);

  const formatPrice = (p) =>
    new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(p);

  const formatDate = (d) =>
    new Date(d).toLocaleDateString('es-MX', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

  const openForm = (product = null) => {
    if (product) {
      setEditProduct(product);
      setForm({
        name: product.name,
        description: product.description || '',
        price: product.price.toString(),
        stock: product.stock.toString(),
        image_url: product.image_url || '',
        category: product.category || ''
      });
    } else {
      setEditProduct(null);
      setForm({ name: '', description: '', price: '', stock: '', image_url: '', category: '' });
    }
    setShowForm(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = {
      name: form.name,
      description: form.description,
      price: parseFloat(form.price),
      stock: parseInt(form.stock),
      image_url: form.image_url,
      category: form.category
    };
    try {
      if (editProduct) {
        await api.updateProduct(editProduct.id, data);
      } else {
        await api.createProduct(data);
      }
      setShowForm(false);
      loadData();
    } catch (err) {
      alert(err.message || 'Error');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('¿Seguro que deseas eliminar este producto?')) return;
    try {
      await api.deleteProduct(id);
      loadData();
    } catch (err) { alert(err.message); }
  };

  const handleConfirmOrder = async (id) => {
    try {
      await api.confirmOrder(id);
      loadData();
    } catch (err) { alert(err.message); }
  };

  return (
    <div className="container page-enter" style={{ padding: '40px 24px' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="heading-lg">
          ⚙️ Panel de <span className="gradient-text">Administración</span>
        </h1>

        {/* Stats */}
        <div className="stats-grid">
          <div className="stat-card glass-card">
            <span className="sc-icon">📦</span>
            <div>
              <span className="sc-value">{products.length}</span>
              <span className="sc-label">Productos</span>
            </div>
          </div>
          <div className="stat-card glass-card">
            <span className="sc-icon">🛒</span>
            <div>
              <span className="sc-value">{orders.length}</span>
              <span className="sc-label">Pedidos</span>
            </div>
          </div>
          <div className="stat-card glass-card">
            <span className="sc-icon">⏳</span>
            <div>
              <span className="sc-value">{orders.filter(o => o.status === 'pending').length}</span>
              <span className="sc-label">Pendientes</span>
            </div>
          </div>
          <div className="stat-card glass-card">
            <span className="sc-icon">💰</span>
            <div>
              <span className="sc-value">{formatPrice(orders.filter(o => o.status === 'confirmed').reduce((s, o) => s + o.total, 0))}</span>
              <span className="sc-label">Ventas</span>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="admin-tabs">
          <button className={`tab-btn ${tab === 'products' ? 'active' : ''}`} onClick={() => setTab('products')}>
            📦 Productos
          </button>
          <button className={`tab-btn ${tab === 'orders' ? 'active' : ''}`} onClick={() => setTab('orders')}>
            🛒 Pedidos
          </button>
        </div>

        {loading ? (
          <div>{[1,2,3].map(i => <div key={i} className="skeleton" style={{ height: 60, borderRadius: 12, marginBottom: 12 }} />)}</div>
        ) : tab === 'products' ? (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
              <h3 className="heading-md">Gestión de Productos</h3>
              <button className="btn btn-primary" onClick={() => openForm()}>+ Nuevo Producto</button>
            </div>
            <div className="admin-table">
              <div className="table-header">
                <span className="th-name">Producto</span>
                <span className="th-cat">Categoría</span>
                <span className="th-price">Precio</span>
                <span className="th-stock">Stock</span>
                <span className="th-actions">Acciones</span>
              </div>
              {products.map((p, i) => (
                <motion.div
                  key={p.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.03 }}
                  className="table-row glass-card"
                >
                  <span className="tr-name">
                    <div className="tr-thumb">
                      {p.image_url ? <img src={p.image_url} alt="" /> : '📦'}
                    </div>
                    {p.name}
                  </span>
                  <span className="tr-cat">{p.category || '—'}</span>
                  <span className="tr-price">{formatPrice(p.price)}</span>
                  <span className={`tr-stock ${p.stock <= 5 ? 'low' : ''}`}>{p.stock}</span>
                  <span className="tr-actions">
                    <button className="btn btn-secondary btn-sm" onClick={() => openForm(p)}>✏️</button>
                    <button className="btn btn-danger btn-sm" onClick={() => handleDelete(p.id)}>🗑️</button>
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        ) : (
          <div>
            <h3 className="heading-md" style={{ marginBottom: 20 }}>Gestión de Pedidos</h3>
            {orders.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: 40 }}>No hay pedidos</p>
            ) : (
              orders.map((order, i) => (
                <motion.div
                  key={order.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="order-row glass-card"
                >
                  <div className="or-header">
                    <div>
                      <strong>Pedido #{order.id}</strong>
                      <span className="or-date">{formatDate(order.created_at)}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <span className={`badge ${order.status === 'confirmed' ? 'badge-success' : order.status === 'cancelled' ? 'badge-danger' : 'badge-warning'}`}>
                        {order.status === 'confirmed' ? '✅ Confirmado' : order.status === 'cancelled' ? '❌ Cancelado' : '⏳ Pendiente'}
                      </span>
                      <span className="or-total">{formatPrice(order.total)}</span>
                    </div>
                  </div>
                  <div className="or-items">
                    {order.items.map(item => (
                      <span key={item.id} className="or-item">{item.product_name} ×{item.quantity}</span>
                    ))}
                  </div>
                  <div className="or-footer">
                    <code className="or-ref">{order.reference_code}</code>
                    {order.status === 'pending' && (
                      <button className="btn btn-primary btn-sm" onClick={() => handleConfirmOrder(order.id)}>
                        ✅ Confirmar Pago
                      </button>
                    )}
                  </div>
                </motion.div>
              ))
            )}
          </div>
        )}
      </motion.div>

      {/* Product Form Modal */}
      <AnimatePresence>
        {showForm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="modal-overlay"
            onClick={() => setShowForm(false)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 30 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 30 }}
              className="modal glass-card"
              onClick={e => e.stopPropagation()}
            >
              <h3 className="heading-md">{editProduct ? 'Editar Producto' : 'Nuevo Producto'}</h3>
              <form onSubmit={handleSubmit} className="product-form">
                <div className="form-group">
                  <label className="form-label">Nombre</label>
                  <input className="form-input" value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Descripción</label>
                  <textarea className="form-input" value={form.description} onChange={e => setForm({...form, description: e.target.value})} />
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Precio (MXN)</label>
                    <input type="number" step="0.01" className="form-input" value={form.price} onChange={e => setForm({...form, price: e.target.value})} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Stock</label>
                    <input type="number" className="form-input" value={form.stock} onChange={e => setForm({...form, stock: e.target.value})} required />
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">URL de Imagen</label>
                  <input className="form-input" value={form.image_url} onChange={e => setForm({...form, image_url: e.target.value})} />
                </div>
                <div className="form-group">
                  <label className="form-label">Categoría</label>
                  <input className="form-input" value={form.category} onChange={e => setForm({...form, category: e.target.value})} />
                </div>
                <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
                  <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>
                    {editProduct ? 'Guardar Cambios' : 'Crear Producto'}
                  </button>
                  <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancelar</button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <style jsx>{`
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
          margin: 32px 0;
        }
        .stat-card {
          padding: 24px;
          display: flex;
          align-items: center;
          gap: 16px;
        }
        .sc-icon {
          font-size: 2rem;
        }
        .sc-value {
          display: block;
          font-family: 'Outfit', sans-serif;
          font-size: 1.5rem;
          font-weight: 700;
        }
        .sc-label {
          font-size: 0.8rem;
          color: var(--text-muted);
        }
        .admin-tabs {
          display: flex;
          gap: 8px;
          margin-bottom: 24px;
          border-bottom: 1px solid var(--border-glass);
          padding-bottom: 8px;
        }
        .tab-btn {
          padding: 10px 20px;
          border: none;
          background: none;
          color: var(--text-muted);
          font-family: 'Inter', sans-serif;
          font-size: 0.95rem;
          font-weight: 500;
          cursor: pointer;
          border-radius: 8px;
          transition: all 0.2s;
        }
        .tab-btn:hover {
          color: var(--text-primary);
          background: var(--bg-glass);
        }
        .tab-btn.active {
          color: var(--text-primary);
          background: var(--bg-tertiary);
        }
        .admin-table {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .table-header {
          display: grid;
          grid-template-columns: 2fr 1fr 1fr 0.5fr 1fr;
          gap: 16px;
          padding: 12px 20px;
          font-size: 0.8rem;
          font-weight: 600;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        .table-row {
          display: grid;
          grid-template-columns: 2fr 1fr 1fr 0.5fr 1fr;
          gap: 16px;
          padding: 16px 20px;
          align-items: center;
          font-size: 0.9rem;
        }
        .tr-name {
          display: flex;
          align-items: center;
          gap: 12px;
          font-weight: 500;
        }
        .tr-thumb {
          width: 40px;
          height: 40px;
          border-radius: 8px;
          overflow: hidden;
          background: var(--bg-secondary);
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .tr-thumb img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .tr-cat {
          color: var(--text-secondary);
        }
        .tr-price {
          color: var(--accent-primary-light);
          font-weight: 600;
        }
        .tr-stock {
          font-weight: 600;
        }
        .tr-stock.low {
          color: var(--accent-danger);
        }
        .tr-actions {
          display: flex;
          gap: 8px;
        }
        .order-row {
          padding: 20px;
          margin-bottom: 12px;
        }
        .or-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
          flex-wrap: wrap;
          gap: 8px;
        }
        .or-date {
          display: block;
          font-size: 0.8rem;
          color: var(--text-muted);
        }
        .or-total {
          font-family: 'Outfit', sans-serif;
          font-size: 1.1rem;
          font-weight: 700;
          color: var(--accent-primary-light);
        }
        .or-items {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-bottom: 12px;
        }
        .or-item {
          padding: 4px 12px;
          background: var(--bg-secondary);
          border-radius: 20px;
          font-size: 0.8rem;
          color: var(--text-secondary);
        }
        .or-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding-top: 12px;
          border-top: 1px solid var(--border-glass);
        }
        .or-ref {
          font-size: 0.8rem;
          color: var(--accent-primary-light);
          background: var(--bg-secondary);
          padding: 4px 10px;
          border-radius: 6px;
        }
        .modal-overlay {
          position: fixed;
          inset: 0;
          background: rgba(0, 0, 0, 0.6);
          backdrop-filter: blur(8px);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 9999;
          padding: 24px;
        }
        .modal {
          width: 100%;
          max-width: 520px;
          padding: 32px;
          max-height: 90vh;
          overflow-y: auto;
        }
        .product-form {
          margin-top: 20px;
        }
        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
        }
        @media (max-width: 768px) {
          .table-header { display: none; }
          .table-row {
            grid-template-columns: 1fr;
            gap: 8px;
          }
          .tr-actions {
            justify-content: flex-end;
          }
          .stats-grid {
            grid-template-columns: 1fr 1fr;
          }
        }
      `}</style>
    </div>
  );
}

export default function AdminPage() {
  return (
    <AuthGuard requireAdmin>
      <AdminContent />
    </AuthGuard>
  );
}
