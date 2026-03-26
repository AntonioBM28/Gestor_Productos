'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Link from 'next/link';

export default function RegisterPage() {
  const { register, isAuthenticated } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    router.push('/');
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }

    if (password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    setLoading(true);
    try {
      await register(username, email, password);
      router.push('/products');
    } catch (err) {
      setError(err.message || 'Error al registrarse');
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
          <span className="auth-icon">✨</span>
          <h1 className="heading-md">Crear Cuenta</h1>
          <p className="auth-subtitle">Únete a GestorPro y empieza a comprar</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="auth-error">{error}</div>}

          <div className="form-group">
            <label className="form-label">Nombre de Usuario</label>
            <input
              type="text"
              className="form-input"
              placeholder="tu_nombre"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

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
              placeholder="Mínimo 6 caracteres"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Confirmar Contraseña</label>
            <input
              type="password"
              className="form-input"
              placeholder="Repite tu contraseña"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
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
            {loading ? 'Creando cuenta...' : 'Crear Cuenta'}
          </motion.button>
        </form>

        <p className="auth-footer">
          ¿Ya tienes cuenta?{' '}
          <Link href="/login" className="auth-link">Inicia sesión</Link>
        </p>
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
      `}</style>
    </div>
  );
}
