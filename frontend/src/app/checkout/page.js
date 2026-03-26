'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import AuthGuard from '@/components/AuthGuard';
import api from '@/lib/api';

function CheckoutContent() {
  const [cart, setCart] = useState({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [orderResult, setOrderResult] = useState(null);
  const router = useRouter();

  useEffect(() => {
    api.getCart().then(data => {
      setCart(data);
      setLoading(false);
      if (data.items.length === 0) router.push('/cart');
    }).catch(() => setLoading(false));
  }, [router]);

  const formatPrice = (p) =>
    new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(p);

  const handleCheckout = async () => {
    setProcessing(true);
    try {
      const data = await api.checkout();
      setOrderResult(data);
      window.dispatchEvent(new Event('cart-updated'));
    } catch (err) {
      alert(err.message || 'Error processing order');
    }
    setProcessing(false);
  };

  if (loading) return <div className="container" style={{ padding: '60px 24px', textAlign: 'center', color: 'var(--text-muted)' }}>Cargando...</div>;

  // Show payment result
  if (orderResult) {
    return (
      <div className="container page-enter" style={{ padding: '40px 24px' }}>
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="payment-result glass-card"
        >
          <div className="success-icon">✅</div>
          <h2 className="heading-lg">¡Pedido Creado!</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 32 }}>
            Tu pedido ha sido registrado exitosamente. Paga en cualquier OXXO o punto de referencia.
          </p>

          <div className="payment-details">
            <div className="payment-qr">
              <img
                src={`data:image/png;base64,${orderResult.payment.qr_code}`}
                alt="QR Code"
                className="qr-image"
              />
            </div>

            <div className="payment-info">
              <div className="info-row">
                <span className="info-label">Código de Referencia</span>
                <span className="info-value ref-code">{orderResult.payment.reference_code}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Código de Barras</span>
                <span className="info-value">{orderResult.payment.barcode_number}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Total a Pagar</span>
                <span className="info-value total">{formatPrice(orderResult.payment.total)}</span>
              </div>
              <div className="info-row">
                <span className="info-label">Estado</span>
                <span className="badge badge-warning">Pendiente de Pago</span>
              </div>
            </div>
          </div>

          <div className="payment-instructions glass-card">
            <h4>📋 Instrucciones de Pago</h4>
            <ol>
              <li>Acude a cualquier tienda <strong>OXXO</strong> o punto de referencia autorizado</li>
              <li>Presenta el <strong>código QR</strong> o dicta el <strong>código de referencia</strong></li>
              <li>Realiza el pago por <strong>{formatPrice(orderResult.payment.total)}</strong></li>
              <li>Guarda tu ticket como comprobante</li>
              <li>Tu pedido será confirmado automáticamente</li>
            </ol>
          </div>

          <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
            <button className="btn btn-primary" onClick={() => router.push('/orders')}>
              Ver Mis Pedidos
            </button>
            <button className="btn btn-secondary" onClick={() => router.push('/products')}>
              Seguir Comprando
            </button>
          </div>
        </motion.div>

        <style jsx>{`
          .payment-result {
            max-width: 700px;
            margin: 0 auto;
            padding: 48px;
            text-align: center;
          }
          .success-icon {
            font-size: 4rem;
            margin-bottom: 16px;
          }
          .payment-details {
            display: flex;
            gap: 32px;
            align-items: center;
            margin: 32px 0;
            text-align: left;
          }
          .payment-qr {
            flex-shrink: 0;
          }
          .qr-image {
            width: 180px;
            height: 180px;
            border-radius: var(--radius-md);
            background: white;
            padding: 8px;
          }
          .payment-info {
            flex: 1;
          }
          .info-row {
            display: flex;
            flex-direction: column;
            gap: 4px;
            margin-bottom: 16px;
          }
          .info-label {
            font-size: 0.8rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
          }
          .info-value {
            font-weight: 600;
            font-size: 1rem;
          }
          .ref-code {
            font-family: monospace;
            font-size: 1.1rem;
            color: var(--accent-primary-light);
          }
          .total {
            font-size: 1.3rem;
            color: var(--accent-success);
          }
          .payment-instructions {
            text-align: left;
            padding: 24px;
            margin-top: 24px;
          }
          .payment-instructions h4 {
            margin-bottom: 12px;
            font-size: 1rem;
          }
          .payment-instructions ol {
            padding-left: 20px;
          }
          .payment-instructions li {
            margin-bottom: 8px;
            color: var(--text-secondary);
            font-size: 0.9rem;
            line-height: 1.5;
          }
          @media (max-width: 600px) {
            .payment-details {
              flex-direction: column;
              text-align: center;
            }
            .payment-result {
              padding: 32px 20px;
            }
          }
        `}</style>
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
        💳 <span className="gradient-text">Checkout</span>
      </motion.h1>

      <div className="checkout-layout">
        <div className="order-review">
          <h3 className="heading-md" style={{ marginBottom: 20 }}>Resumen del Pedido</h3>
          {cart.items.map(item => (
            <div key={item.id} className="review-item glass-card">
              <div className="review-image">
                {item.product?.image_url ? (
                  <img src={item.product.image_url} alt={item.product.name} />
                ) : <span>📦</span>}
              </div>
              <div className="review-info">
                <h4>{item.product?.name}</h4>
                <p>{item.quantity} × {formatPrice(item.product?.price || 0)}</p>
              </div>
              <div className="review-subtotal">
                {formatPrice((item.product?.price || 0) * item.quantity)}
              </div>
            </div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="checkout-summary glass-card"
        >
          <h3 className="heading-md">Método de Pago</h3>
          <div className="payment-method glass-card" style={{ marginTop: 16, padding: 20 }}>
            <span style={{ fontSize: '2rem' }}>🏪</span>
            <div>
              <h4>Pago en Efectivo</h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                OXXO y puntos de referencia autorizados
              </p>
            </div>
          </div>

          <div style={{ marginTop: 24, padding: '16px 0', borderTop: '1px solid var(--border-glass)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
              <span style={{ color: 'var(--text-secondary)' }}>Subtotal</span>
              <span>{formatPrice(cart.total)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
              <span style={{ color: 'var(--text-secondary)' }}>Envío</span>
              <span style={{ color: 'var(--accent-success)' }}>Gratis</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '1.3rem', fontWeight: 700 }}>
              <span>Total</span>
              <span className="gradient-text">{formatPrice(cart.total)}</span>
            </div>
          </div>

          <motion.button
            whileTap={{ scale: 0.98 }}
            className="btn btn-primary"
            style={{ width: '100%', marginTop: 16, padding: '16px' }}
            onClick={handleCheckout}
            disabled={processing}
          >
            {processing ? 'Procesando...' : `Confirmar Pedido — ${formatPrice(cart.total)}`}
          </motion.button>
        </motion.div>
      </div>

      <style jsx>{`
        .checkout-layout {
          display: grid;
          grid-template-columns: 1fr 400px;
          gap: 32px;
          margin-top: 32px;
        }
        .order-review {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .review-item {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 16px;
        }
        .review-image {
          width: 60px;
          height: 60px;
          border-radius: 8px;
          overflow: hidden;
          background: var(--bg-secondary);
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5rem;
        }
        .review-image img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        .review-info {
          flex: 1;
        }
        .review-info h4 {
          font-size: 0.9rem;
          margin-bottom: 4px;
        }
        .review-info p {
          font-size: 0.85rem;
          color: var(--text-muted);
        }
        .review-subtotal {
          font-weight: 600;
          color: var(--accent-primary-light);
        }
        .checkout-summary {
          padding: 28px;
          height: fit-content;
          position: sticky;
          top: 100px;
        }
        .payment-method {
          display: flex;
          align-items: center;
          gap: 16px;
        }
        .payment-method h4 {
          font-size: 0.95rem;
        }
        @media (max-width: 768px) {
          .checkout-layout {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}

export default function CheckoutPage() {
  return (
    <AuthGuard requireAuth>
      <CheckoutContent />
    </AuthGuard>
  );
}
