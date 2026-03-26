'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Link from 'next/link';

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    router.push('/');
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await login(email, password);
      if (data.user.role === 'admin') {
        router.push('/admin');
      } else {
        router.push('/products');
      }
    } catch (err) {
      setError(err.message || 'Error al iniciar sesión');
    }
    setLoading(false);
  };

  return (
    <div className="auth-page page-enter">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="auth-card glass-card"
      >
        <div className="auth-header">
          <span className="auth-icon">🔐</span>
          <h1 className="heading-md">Iniciar Sesión</h1>
          <p className="auth-subtitle">Bienvenido de vuelta a GestorPro</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="auth-error">{error}</div>}

          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              className="form-input"
              placeholder="tu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Contraseña</label>
            <input
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <motion.button
            whileTap={{ scale: 0.98 }}
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: 8 }}
            disabled={loading}
          >
            {loading ? 'Entrando...' : 'Iniciar Sesión'}
          </motion.button>
        </form>

        <p className="auth-footer">
          ¿No tienes cuenta?{' '}
          <Link href="/register" className="auth-link">Regístrate aquí</Link>
        </p>

        <div className="demo-access">
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 8 }}>
            Acceso demo admin:
          </p>
          <code style={{ fontSize: '0.75rem', color: 'var(--accent-primary-light)' }}>
            admin@gestorproductos.com / admin123
          </code>
        </div>
      </motion.div>

      <style jsx>{`
        .auth-page {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: calc(100vh - 160px);
          padding: 40px 24px;
        }
        .auth-card {
          width: 100%;
          max-width: 440px;
          padding: 40px;
        }
        .auth-header {
          text-align: center;
          margin-bottom: 32px;
        }
        .auth-icon {
          font-size: 3rem;
          display: block;
          margin-bottom: 16px;
        }
        .auth-subtitle {
          color: var(--text-muted);
          margin-top: 8px;
        }
        .auth-form {
          display: flex;
          flex-direction: column;
        }
        .auth-error {
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.3);
          color: var(--accent-danger);
          padding: 12px 16px;
          border-radius: var(--radius-md);
          margin-bottom: 16px;
          font-size: 0.9rem;
        }
        .auth-footer {
          text-align: center;
          margin-top: 24px;
          color: var(--text-muted);
          font-size: 0.9rem;
        }
        .auth-link {
          color: var(--accent-primary-light);
          text-decoration: none;
          font-weight: 600;
        }
        .auth-link:hover {
          text-decoration: underline;
        }
        .demo-access {
          text-align: center;
          margin-top: 20px;
          padding-top: 20px;
          border-top: 1px solid var(--border-glass);
        }
      `}</style>
    </div>
  );
}
