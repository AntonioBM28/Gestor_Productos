'use client';

import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function AuthGuard({ children, requireAuth = false, requireAdmin = false }) {
  const { user, loading, isAuthenticated, isAdmin } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;

    if (requireAuth && !isAuthenticated) {
      router.push('/login');
      return;
    }

    if (requireAdmin && !isAdmin) {
      router.push('/');
      return;
    }
  }, [loading, isAuthenticated, isAdmin, requireAuth, requireAdmin, router]);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '60vh',
        color: 'var(--text-muted)'
      }}>
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p style={{ marginTop: 16 }}>Cargando...</p>
        </div>
        <style jsx>{`
          .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid var(--border-glass);
            border-top-color: var(--accent-primary);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 0 auto;
          }
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (requireAuth && !isAuthenticated) return null;
  if (requireAdmin && !isAdmin) return null;

  return children;
}
