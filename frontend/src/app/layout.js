import './globals.css';
import { AuthProvider } from '@/lib/auth';
import Navbar from '@/components/Navbar';

export const metadata = {
  title: 'GestorPro - Tu Tienda de Tecnología Premium',
  description: 'Descubre los mejores productos de tecnología con los mejores precios. Laptops, smartphones, periféricos y más.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>
        <AuthProvider>
          <Navbar />
          <main style={{ paddingTop: '80px', minHeight: '100vh' }}>
            {children}
          </main>
          <footer style={{
            textAlign: 'center',
            padding: '40px 24px',
            color: 'var(--text-muted)',
            fontSize: '0.85rem',
            borderTop: '1px solid var(--border-glass)',
          }}>
            <p>© 2026 GestorPro — Todos los derechos reservados</p>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
