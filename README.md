# 🛍️ GestorPro - Gestor de Productos

Sistema de gestión de productos con carrito de compras, pagos y roles de usuario.

## 🏗️ Tech Stack

- **Frontend:** Next.js 16 (React)
- **Backend:** Flask (Python)
- **Base de Datos:** MongoDB (local)
- **Autenticación:** JWT

---

## 🚀 Instalación y Configuración

### Requisitos Previos

1. **Node.js** (v18 o superior) → [Descargar](https://nodejs.org/)
2. **Python** (v3.10 o superior) → [Descargar](https://www.python.org/)
3. **MongoDB Community Server** → [Descargar](https://www.mongodb.com/try/download/community)

### 1. Instalar MongoDB

#### Windows
1. Descarga MongoDB Community Server desde el link de arriba
2. Instálalo con la opción **"Complete"**
3. Asegúrate de marcar **"Install MongoDB as a Service"**
4. MongoDB correrá automáticamente en `localhost:27017`

#### macOS
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

#### Linux (Ubuntu)
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### 2. Configurar el Backend

```bash
cd backend

# Instalar dependencias de Python
pip install -r requirements.txt

# Ejecutar seed (crea admin y productos de ejemplo)
python seed.py
```

### 3. Configurar el Frontend

```bash
cd frontend

# Instalar dependencias de Node
npm install
```

---

## ▶️ Ejecutar el Proyecto

Necesitas **2 terminales** abiertas:

### Terminal 1 - Backend (Puerto 5000)
```bash
cd backend
python app.py
```

### Terminal 2 - Frontend (Puerto 3000)
```bash
cd frontend
npm run dev
```

Abre tu navegador en: **http://localhost:3000**

---

## 👤 Credenciales de Prueba

| Rol | Email | Contraseña |
|-----|-------|------------|
| Admin | admin@gestorproductos.com | admin123 |

> Los usuarios normales se crean desde la opción **"Registrarse"** en la app.

---

## 🔑 Roles de Usuario

| Rol | Permisos |
|-----|----------|
| **Guest** (sin cuenta) | Ver productos |
| **User** | Ver productos, carrito, comprar, ver órdenes |
| **Admin** | Todo lo anterior + CRUD productos, gestionar usuarios, confirmar pagos |

---

## 📡 API Endpoints

### Auth (`/api/auth`)
| Método | Ruta | Acceso |
|--------|------|--------|
| POST | `/register` | Público |
| POST | `/login` | Público |
| GET | `/me` | Autenticado |

### Products (`/api/products`)
| Método | Ruta | Acceso |
|--------|------|--------|
| GET | `/` | Público |
| GET | `/<id>` | Público |
| POST | `/` | Admin |
| PUT | `/<id>` | Admin |
| DELETE | `/<id>` | Admin |
| GET | `/categories` | Público |

### Cart (`/api/cart`)
| Método | Ruta | Acceso |
|--------|------|--------|
| GET | `/` | User |
| POST | `/` | User |
| PUT | `/<id>` | User |
| DELETE | `/<id>` | User |
| DELETE | `/clear` | User |

### Orders (`/api/orders`)
| Método | Ruta | Acceso |
|--------|------|--------|
| POST | `/checkout` | User |
| GET | `/` | User/Admin |
| GET | `/<id>` | User/Admin |
| PUT | `/<id>/confirm` | Admin |
| PUT | `/<id>/cancel` | User/Admin |

### Users (`/api/users`)
| Método | Ruta | Acceso |
|--------|------|--------|
| GET | `/` | Admin |
| PUT | `/<id>/role` | Admin |
| DELETE | `/<id>` | Admin |

---

## 📁 Estructura del Proyecto

```
Gestor_Productos/
├── backend/
│   ├── app.py              # App principal Flask
│   ├── db.py               # Conexión a MongoDB
│   ├── models.py           # Serialización y validación
│   ├── auth.py             # Autenticación (login/register)
│   ├── middleware.py        # Decoradores de roles
│   ├── seed.py             # Datos iniciales
│   ├── utils.py            # QR y códigos de referencia
│   ├── requirements.txt    # Dependencias Python
│   └── routes/
│       ├── products.py     # CRUD productos
│       ├── cart.py         # Carrito
│       ├── orders.py       # Órdenes y checkout
│       └── users.py        # Gestión de usuarios (admin)
├── frontend/
│   ├── src/
│   │   ├── app/            # Páginas Next.js
│   │   ├── components/     # Componentes React
│   │   └── lib/            # API client y auth context
│   └── package.json
└── README.md
```
