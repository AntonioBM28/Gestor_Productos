'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';
import { motion, AnimatePresence } from 'framer-motion';
import api from '@/lib/api';

export default function Navbar() {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const [cartCount, setCartCount] = useState(0);
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      api.getCart().then(data => setCartCount(data.count)).catch(() => {});
    }
  }, [isAuthenticated]);

  // Listen for cart updates
  useEffect(() => {
    const handler = () => {
      if (isAuthenticated) {
        api.getCart().then(data => setCartCount(data.count)).catch(() => {});
      }
    };
    window.addEventListener('cart-updated', handler);
    return () => window.removeEventListener('cart-updated', handler);
  }, [isAuthenticated]);

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="navbar"
      style={{
        background: scrolled ? 'rgba(10, 10, 15, 0.9)' : 'transparent',
        backdropFilter: scrolled ? 'blur(20px)' : 'none',
        borderBottom: scrolled ? '1px solid rgba(255,255,255,0.05)' : 'none',
      }}
    >
      <div className="nav-content container">
        <Link href="/" className="nav-logo">
          <span className="logo-icon">⚡</span>
          <span className="logo-text">
            Gestor<span className="gradient-text">Pro</span>
          </span>
        </Link>

        <div className="nav-links">
          <Link href="/products" className="nav-link">Productos</Link>
          {isAuthenticated && !isAdmin && (
            <Link href="/cart" className="nav-link cart-link">
              🛒 Carrito
              {cartCount > 0 && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="cart-badge"
                >
                  {cartCount}
                </motion.span>
              )}
            </Link>
          )}
          {isAuthenticated && !isAdmin && (
            <Link href="/orders" className="nav-link">Mis Pedidos</Link>
          )}
          {isAdmin && (
            <Link href="/admin" className="nav-link admin-link">⚙️ Admin</Link>
          )}
        </div>

        <div className="nav-actions">
          {isAuthenticated ? (
            <div className="user-menu">
              <span className="user-greeting">
                {isAdmin && '👑 '}{user?.username}
              </span>
              <button onClick={logout} className="btn btn-secondary btn-sm">
                Salir
              </button>
            </div>
          ) : (
            <div className="auth-buttons">
              <Link href="/login" className="btn btn-secondary btn-sm">
                Iniciar Sesión
              </Link>
              <Link href="/register" className="btn btn-primary btn-sm">
                Registrarse
              </Link>
            </div>
          )}
        </div>

        <button className="mobile-menu-btn" onClick={() => setMenuOpen(!menuOpen)}>
          <span></span><span></span><span></span>
        </button>
      </div>

      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="mobile-menu"
          >
            <Link href="/products" onClick={() => setMenuOpen(false)}>Productos</Link>
            {isAuthenticated && !isAdmin && (
              <Link href="/cart" onClick={() => setMenuOpen(false)}>🛒 Carrito {cartCount > 0 && `(${cartCount})`}</Link>
            )}
            {isAuthenticated && !isAdmin && (
              <Link href="/orders" onClick={() => setMenuOpen(false)}>Mis Pedidos</Link>
            )}
            {isAdmin && (
              <Link href="/admin" onClick={() => setMenuOpen(false)}>⚙️ Admin</Link>
            )}
            {isAuthenticated ? (
              <button onClick={() => { logout(); setMenuOpen(false); }}>Salir</button>
            ) : (
              <>
                <Link href="/login" onClick={() => setMenuOpen(false)}>Iniciar Sesión</Link>
                <Link href="/register" onClick={() => setMenuOpen(false)}>Registrarse</Link>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      <style jsx>{`
        .navbar {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          z-index: 1000;
          padding: 16px 0;
          transition: all 0.3s ease;
        }
        .nav-content {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 24px;
        }
        .nav-logo {
          display: flex;
          align-items: center;
          gap: 8px;
          text-decoration: none;
          font-family: 'Outfit', sans-serif;
          font-size: 1.5rem;
          font-weight: 800;
          color: var(--text-primary);
        }
        .logo-icon {
          font-size: 1.8rem;
        }
        .nav-links {
          display: flex;
          align-items: center;
          gap: 24px;
        }
        .nav-link {
          text-decoration: none;
          color: var(--text-secondary);
          font-weight: 500;
          font-size: 0.95rem;
          transition: color 0.2s;
          position: relative;
        }
        .nav-link:hover {
          color: var(--text-primary);
        }
        .cart-link {
          display: flex;
          align-items: center;
          gap: 4px;
          position: relative;
        }
        .admin-link {
          color: var(--accent-primary-light);
        }
        .nav-actions {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .user-menu {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .user-greeting {
          color: var(--text-secondary);
          font-size: 0.9rem;
          font-weight: 500;
        }
        .auth-buttons {
          display: flex;
          gap: 8px;
        }
        .mobile-menu-btn {
          display: none;
          flex-direction: column;
          gap: 5px;
          background: none;
          border: none;
          cursor: pointer;
          padding: 4px;
        }
        .mobile-menu-btn span {
          display: block;
          width: 24px;
          height: 2px;
          background: var(--text-primary);
          border-radius: 2px;
          transition: all 0.3s;
        }
        @media (max-width: 768px) {
          .nav-links, .nav-actions { display: none; }
          .mobile-menu-btn { display: flex; }
        }
      `}</style>
      <style jsx global>{`
        .cart-badge {
          position: absolute;
          top: -8px;
          right: -12px;
          background: var(--accent-danger);
          color: white;
          font-size: 0.65rem;
          font-weight: 700;
          width: 18px;
          height: 18px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .mobile-menu {
          overflow: hidden;
          display: flex;
          flex-direction: column;
          padding: 16px 24px;
          gap: 12px;
          background: rgba(10, 10, 15, 0.95);
          border-top: 1px solid var(--border-glass);
        }
        .mobile-menu a, .mobile-menu button {
          color: var(--text-secondary);
          text-decoration: none;
          padding: 8px 0;
          font-weight: 500;
          background: none;
          border: none;
          text-align: left;
          font-size: 1rem;
          cursor: pointer;
          font-family: 'Inter', sans-serif;
        }
        .mobile-menu a:hover, .mobile-menu button:hover {
          color: var(--text-primary);
        }
      `}</style>
    </motion.nav>
  );
}
