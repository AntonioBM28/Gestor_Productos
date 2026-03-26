'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import ProductCard from '@/components/ProductCard';
import api from '@/lib/api';

export default function Home() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getProducts().then(data => {
      setProducts(data.products?.slice(0, 6) || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <div className="page-enter">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-bg">
          <div className="hero-orb hero-orb-1" />
          <div className="hero-orb hero-orb-2" />
          <div className="hero-orb hero-orb-3" />
        </div>
        <div className="container hero-content">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            className="hero-text"
          >
            <span className="hero-badge">🚀 La mejor tienda tech de México</span>
            <h1 className="heading-xl">
              Tecnología <span className="gradient-text">Premium</span><br />
              al Mejor Precio
            </h1>
            <p className="hero-subtitle">
              Encuentra los mejores productos de tecnología. Laptops, smartphones,
              periféricos y más. Paga fácil en OXXO y recibe en tu puerta.
            </p>
            <div className="hero-actions">
              <Link href="/products" className="btn btn-primary btn-lg">
                Ver Productos ✨
              </Link>
              <Link href="/register" className="btn btn-secondary btn-lg">
                Crear Cuenta
              </Link>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
            className="hero-visual"
          >
            <div className="hero-card animate-float">
              <div className="hero-card-glow" />
              <span className="hero-emoji">🛍️</span>
              <div className="hero-card-stats">
                <div className="stat-item">
                  <span className="stat-number">500+</span>
                  <span className="stat-label">Productos</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">24/7</span>
                  <span className="stat-label">Soporte</span>
                </div>
                <div className="stat-item">
                  <span className="stat-number">🏪</span>
                  <span className="stat-label">Pago OXXO</span>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="features container">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="features-grid"
        >
          {[
            { icon: '🔒', title: 'Compra Segura', desc: 'Tu información siempre protegida con encriptación de grado militar.' },
            { icon: '🏪', title: 'Pago en OXXO', desc: 'Paga en efectivo en cualquier OXXO con tu código QR o de barras.' },
            { icon: '📦', title: 'Envío Rápido', desc: 'Recibe tus productos en la puerta de tu casa en 2-5 días hábiles.' },
            { icon: '💬', title: 'Soporte 24/7', desc: 'Nuestro equipo está siempre listo para ayudarte con cualquier duda.' },
          ].map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1, duration: 0.5 }}
              className="feature-card glass-card"
            >
              <span className="feature-icon">{feature.icon}</span>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-desc">{feature.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Featured Products */}
      <section className="featured container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="section-header"
        >
          <h2 className="heading-lg">
            Productos <span className="gradient-text">Destacados</span>
          </h2>
          <p className="section-subtitle">Lo más nuevo y lo mejor que tenemos para ti</p>
        </motion.div>

        {loading ? (
          <div className="product-grid">
            {[1,2,3].map(i => (
              <div key={i} className="skeleton" style={{ height: 350, borderRadius: 16 }} />
            ))}
          </div>
        ) : (
          <div className="product-grid">
            {products.map((p, i) => (
              <ProductCard key={p.id} product={p} index={i} />
            ))}
          </div>
        )}

        <div style={{ textAlign: 'center', marginTop: 40 }}>
          <Link href="/products" className="btn btn-primary btn-lg">
            Ver Todos los Productos →
          </Link>
        </div>
      </section>

      <style jsx>{`
        .hero {
          position: relative;
          padding: 80px 0 100px;
          overflow: hidden;
        }
        .hero-bg {
          position: absolute;
          inset: 0;
          pointer-events: none;
        }
        .hero-orb {
          position: absolute;
          border-radius: 50%;
          filter: blur(80px);
        }
        .hero-orb-1 {
          width: 500px;
          height: 500px;
          background: rgba(124, 58, 237, 0.15);
          top: -100px;
          right: -100px;
        }
        .hero-orb-2 {
          width: 400px;
          height: 400px;
          background: rgba(6, 182, 212, 0.1);
          bottom: -100px;
          left: -100px;
        }
        .hero-orb-3 {
          width: 300px;
          height: 300px;
          background: rgba(124, 58, 237, 0.08);
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
        }
        .hero-content {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 60px;
          align-items: center;
          position: relative;
          z-index: 1;
        }
        .hero-badge {
          display: inline-block;
          padding: 8px 20px;
          background: rgba(124, 58, 237, 0.15);
          border: 1px solid rgba(124, 58, 237, 0.3);
          border-radius: 50px;
          font-size: 0.85rem;
          font-weight: 600;
          color: var(--accent-primary-light);
          margin-bottom: 24px;
        }
        .hero-subtitle {
          font-size: 1.15rem;
          color: var(--text-secondary);
          line-height: 1.7;
          margin: 24px 0 32px;
          max-width: 500px;
        }
        .hero-actions {
          display: flex;
          gap: 16px;
          flex-wrap: wrap;
        }
        .hero-visual {
          display: flex;
          justify-content: center;
          align-items: center;
        }
        .hero-card {
          position: relative;
          text-align: center;
          padding: 40px;
          background: var(--bg-glass);
          border: 1px solid var(--border-glass);
          border-radius: 24px;
          backdrop-filter: blur(20px);
          width: 100%;
          max-width: 380px;
        }
        .hero-card-glow {
          position: absolute;
          inset: -1px;
          border-radius: 24px;
          background: var(--accent-gradient);
          opacity: 0.15;
          z-index: -1;
          filter: blur(20px);
        }
        .hero-emoji {
          font-size: 4rem;
          display: block;
          margin-bottom: 24px;
        }
        .hero-card-stats {
          display: flex;
          justify-content: space-around;
          gap: 16px;
        }
        .stat-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .stat-number {
          font-family: 'Outfit', sans-serif;
          font-size: 1.5rem;
          font-weight: 700;
          color: var(--accent-primary-light);
        }
        .stat-label {
          font-size: 0.8rem;
          color: var(--text-muted);
        }

        .features {
          padding: 80px 0;
        }
        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 24px;
        }
        .feature-card {
          padding: 32px;
          text-align: center;
        }
        .feature-icon {
          font-size: 2.5rem;
          display: block;
          margin-bottom: 16px;
        }
        .feature-title {
          font-family: 'Outfit', sans-serif;
          font-size: 1.2rem;
          font-weight: 600;
          margin-bottom: 8px;
        }
        .feature-desc {
          color: var(--text-muted);
          font-size: 0.9rem;
          line-height: 1.6;
        }

        .featured {
          padding: 40px 0 100px;
        }
        .section-header {
          text-align: center;
          margin-bottom: 48px;
        }
        .section-subtitle {
          color: var(--text-secondary);
          margin-top: 12px;
          font-size: 1.05rem;
        }

        @media (max-width: 768px) {
          .hero-content {
            grid-template-columns: 1fr;
            gap: 40px;
            text-align: center;
          }
          .hero-subtitle {
            margin-left: auto;
            margin-right: auto;
          }
          .hero-actions {
            justify-content: center;
          }
        }
      `}</style>
    </div>
  );
}
