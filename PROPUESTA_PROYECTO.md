# 📋 Propuesta Inicial del Proyecto — Gestor de Productos

---

## 1️⃣ Datos Generales del Proyecto

| Campo | Detalle |
|-------|---------|
| **Nombre del Proyecto** | Gestor de Productos — Sistema de Gestión de Productos con E-Commerce |
| **Nombre del Equipo** | Equipo Dinamita |
| **Fecha** | 7 de abril de 2026 |
| **Profesor** | José de Jesús Eduardo Barrientos Ávalos |
| **Materia** | Desarrollo Web Profesional |

### Integrantes y Rol Técnico

| # | Nombre Completo | Rol Técnico |
|---|----------------|-------------|
| 1 | José Antonio Balderas Melchor | Full Stack Developer |
| 2 | Cristian Efraín Oropeza Yepez | Full Stack Developer |
| 3 | Juan Francisco Rodríguez Guerrero | Full Stack Developer |
| 4 | Manuel Alejandro Mata Campos | Full Stack Developer |

### Tecnologías Utilizadas

| Capa | Tecnología | Versión |
|------|-----------|---------|
| **Frontend** | Next.js (React) | 15.x |
| **Backend** | Flask (Python) | 3.1.0 |
| **Base de Datos** | MongoDB | 7.x |
| **Autenticación** | Flask-JWT-Extended (JWT) | 4.7.1 |
| **Validación** | Marshmallow | 4.3.0 |
| **Rate Limiting** | Flask-Limiter | 3.12 |
| **Sanitización** | Bleach | 6.x |
| **QR / Pagos** | qrcode + Pillow | 8.0 |
| **Control de versiones** | Git + GitHub | — |

---

## 2️⃣ Definición del Problema

### Contexto

En el ecosistema actual del comercio electrónico en México, las pequeñas y medianas empresas (PyMEs) representan más del 99% de los establecimientos del país. Muchas de estas empresas buscan digitalizar sus procesos de venta y gestión de inventarios, pero se enfrentan a barreras significativas: los sistemas comerciales existentes como Shopify o WooCommerce suelen tener costos mensuales elevados, curvas de aprendizaje complejas y, más crítico aún, carecen de controles de seguridad granulares que protejan tanto la información del negocio como la de sus clientes.

### Problema Específico

Actualmente, las pequeñas empresas y emprendedores no cuentan con un sistema web accesible, seguro y personalizable que les permita:

- **Gestionar un catálogo de productos** con control de inventario en tiempo real.
- **Implementar diferentes niveles de acceso** para administradores, empleados y clientes, cada uno con permisos claramente definidos.
- **Proteger la información sensible** de usuarios (contraseñas, datos de compra, historial de órdenes) contra ataques comunes como inyección NoSQL, Cross-Site Scripting (XSS), fuerza bruta y enumeración de usuarios.
- **Ofrecer un flujo de compra digital** con generación de referencias de pago y códigos QR para pagos en efectivo en tiendas de conveniencia (modelo OXXO), un método de pago fundamental en el mercado mexicano donde una proporción significativa de la población no cuenta con tarjetas bancarias.

### Impacto del Problema

| Área | Impacto |
|------|---------|
| **Económico** | PyMEs pierden oportunidades de venta al no tener presencia digital con sistema de pagos accesible |
| **Seguridad** | Sistemas caseros sin validación exponen datos de clientes a ataques de inyección, XSS y fuerza bruta |
| **Operativo** | Sin control de roles, cualquier usuario puede modificar inventario o acceder a información confidencial |
| **Experiencia del cliente** | Sin sistema de carrito y órdenes, el proceso de compra es manual, lento y propenso a errores |

### Justificación Tecnológica

La elección del stack tecnológico responde directamente a los requerimientos del problema:

- **Flask (Python)**: Framework ligero y flexible que permite implementar seguridad granular a nivel de middleware, ideal para APIs RESTful con control de acceso por roles. Su ecosistema de extensiones (Flask-JWT-Extended, Flask-Limiter, Flask-CORS) permite integrar capas de seguridad sin dependencias pesadas.

- **MongoDB**: Base de datos NoSQL que ofrece flexibilidad en el esquema de datos para catálogos de productos con atributos variables, índices TTL para auto-limpieza de tokens revocados y logs de seguridad, y escalabilidad horizontal para crecimiento futuro.

- **Next.js (React)**: Framework de React con renderizado del lado del servidor (SSR) que mejora el SEO y la velocidad de carga inicial, crucial para un e-commerce. Su sistema de enrutamiento basado en archivos simplifica la arquitectura del frontend.

- **JWT (JSON Web Tokens)**: Mecanismo de autenticación stateless con soporte para access tokens de corta duración y refresh tokens de larga duración, permitiendo sesiones seguras sin almacenar estado en el servidor y con capacidad de revocación mediante blacklist.

- **Marshmallow + Bleach**: Combinación de validación de esquemas y sanitización de entradas que previene inyección NoSQL y XSS a nivel de cada endpoint, proporcionando una defensa en profundidad.

---

## 3️⃣ Objetivo General

Desarrollar una aplicación web Full Stack segura de gestión de productos y comercio electrónico que implemente autenticación robusta con tokens JWT, control de acceso basado en roles (RBAC), validación y sanitización exhaustiva de datos, protección contra ataques comunes de seguridad web, y un flujo de compra completo con generación de referencias de pago en efectivo.

---

## 4️⃣ Objetivos Específicos

1. **Implementar autenticación segura mediante JWT** con access tokens de corta duración (15 minutos en producción), refresh tokens de larga duración (30 días), y mecanismo de revocación de sesiones mediante blacklist de tokens almacenada en MongoDB con auto-limpieza por TTL.

2. **Diseñar e implementar un esquema de control de acceso basado en roles (RBAC)** con al menos tres niveles: invitado (acceso público al catálogo), usuario registrado (carrito de compras, órdenes, historial) y administrador (gestión completa de productos, usuarios y órdenes), incluyendo protección contra auto-degradación de rol y eliminación del último administrador.

3. **Integrar validación robusta de datos en todas las capas** utilizando schemas de Marshmallow para cada entidad (usuarios, productos, carrito, órdenes, roles), con reglas de validación estrictas: contraseñas fuertes (mínimo 8 caracteres con mayúscula, minúscula, número y carácter especial), precios acotados (0.01 a 1,000,000), cantidades limitadas (1-100 por producto), y emails con formato válido.

4. **Implementar protección contra ataques de seguridad web** incluyendo: sanitización XSS con Bleach en todos los inputs, prevención de inyección NoSQL escapando operadores MongoDB (`$gt`, `$ne`, `$regex`), rate limiting por IP (5 intentos de login/minuto, 3 registros/minuto), bloqueo temporal de cuenta tras 5 intentos fallidos de login, headers de seguridad HTTP (CSP, X-Frame-Options, HSTS, X-Content-Type-Options), y respuestas de tiempo constante en login para evitar enumeración de usuarios.

5. **Desarrollar un sistema de gestión de productos completo** con operaciones CRUD protegidas por rol de administrador, búsqueda por nombre con protección contra inyección de regex, filtrado por categorías, control de inventario en tiempo real con validación de stock en cada operación de compra, y paginación de resultados.

6. **Implementar un flujo de compra funcional con sistema de pagos en efectivo** que incluya: carrito de compras persistente con límites de seguridad (máximo 50 productos distintos, 100 unidades por producto), proceso de checkout con validación atómica de stock, generación de códigos de referencia únicos y códigos QR para pago en tiendas de conveniencia, y sistema de confirmación/cancelación de órdenes con restauración automática de inventario.

7. **Establecer un sistema de auditoría y logging de seguridad** que registre en MongoDB todos los eventos críticos: intentos de login exitosos y fallidos, cambios de rol, creación/modificación/eliminación de productos, operaciones de órdenes, y accesos no autorizados, con retención automática de 90 días mediante índices TTL.

---

## 📐 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENTE (Browser)                       │
│                        Next.js 15.x                          │
│              React Components + Client Router                │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS (JSON)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE SEGURIDAD                         │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │   CORS   │  │ Rate Limiter │  │  Security Headers     │  │
│  │ (origins)│  │ (por IP)     │  │  (CSP, HSTS, XFO...) │  │
│  └──────────┘  └──────────────┘  └───────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 AUTENTICACIÓN (JWT)                           │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐   │
│  │ Access Token  │  │ Refresh     │  │ Token Blacklist  │   │
│  │ (15min/1hr)  │  │ Token (30d) │  │ (MongoDB + TTL)  │   │
│  └──────────────┘  └─────────────┘  └──────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              AUTORIZACIÓN (RBAC Middleware)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │  guest   │  │   user   │  │  admin   │  │ is_active  │  │
│  │ (público)│  │ (auth)   │  │ (full)   │  │  check     │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               VALIDACIÓN Y SANITIZACIÓN                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Marshmallow   │  │ Bleach (XSS) │  │ NoSQL Injection  │  │
│  │ Schemas       │  │ Sanitization │  │ Prevention       │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    API REST (Flask)                           │
│  ┌──────────┐  ┌──────────┐  ┌────────┐  ┌─────────────┐  │
│  │  /auth   │  │/products │  │ /cart   │  │  /orders    │  │
│  │  /users  │  │          │  │        │  │             │  │
│  └──────────┘  └──────────┘  └────────┘  └─────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    MongoDB (Local)                            │
│  ┌────────┐ ┌──────────┐ ┌───────┐ ┌────────┐ ┌─────────┐ │
│  │ users  │ │ products │ │ cart  │ │ orders │ │security │ │
│  │        │ │          │ │_items │ │        │ │ _logs   │ │
│  └────────┘ └──────────┘ └───────┘ └────────┘ └─────────┘ │
│  ┌──────────────┐                                           │
│  │token_blacklist│ (TTL: 31 días)                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔒 Resumen de Mecanismos de Seguridad

| # | Mecanismo | Implementación | Capa |
|---|-----------|---------------|------|
| 1 | Autenticación JWT | Access + Refresh Tokens con blacklist | Autenticación |
| 2 | Hashing de contraseñas | Werkzeug (PBKDF2 + SHA256 + salt) | Almacenamiento |
| 3 | Política de contraseñas | 8+ chars, mayúscula, minúscula, número, especial | Validación |
| 4 | Control de roles (RBAC) | Decoradores: `admin_required`, `user_required`, `role_required` | Autorización |
| 5 | Rate Limiting | Flask-Limiter por IP en endpoints críticos | Red |
| 6 | Account Lockout | Bloqueo 15min tras 5 intentos fallidos | Autenticación |
| 7 | Sanitización XSS | Bleach strip tags en todos los inputs | Validación |
| 8 | Prevención NoSQL Injection | Escape de operadores `$` y caracteres regex | Validación |
| 9 | Headers de seguridad HTTP | CSP, HSTS, X-Frame-Options, X-Content-Type-Options | Transporte |
| 10 | CORS restrictivo | Solo orígenes permitidos con métodos explícitos | Red |
| 11 | Validación de schemas | Marshmallow con tipos, rangos y formatos estrictos | Validación |
| 12 | Audit logging | Registro de eventos de seguridad en MongoDB (TTL 90d) | Monitoreo |
| 13 | Tiempo constante en login | Evita enumeración de usuarios por timing | Autenticación |
| 14 | Límite de tamaño de request | MAX_CONTENT_LENGTH = 2MB | Red |
| 15 | Auto-limpieza de tokens | Índices TTL en MongoDB para blacklist y logs | Mantenimiento |

---

*Documento elaborado por el Equipo Dinamita para la materia de Desarrollo Web Profesional.*
*Profesor: José de Jesús Eduardo Barrientos Ávalos.*
*Fecha: 7 de abril de 2026.*
