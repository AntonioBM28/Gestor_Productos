"""Seed script to create initial admin user and sample products."""
from app import create_app
from models import db, User, Product
from werkzeug.security import generate_password_hash


def seed():
    app = create_app()
    with app.app_context():
        # Check if admin exists
        if User.query.filter_by(role='admin').first():
            print('Admin user already exists, skipping user seed.')
        else:
            admin = User(
                username='admin',
                email='admin@gestorproductos.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            print('Admin user created: admin@gestorproductos.com / admin123')

        # Seed sample products if none exist
        if Product.query.count() == 0:
            products = [
                Product(
                    name='Laptop Gaming ASUS ROG',
                    description='Laptop gaming de alto rendimiento con RTX 4060, 16GB RAM, 512GB SSD. Pantalla 15.6" Full HD 144Hz.',
                    price=24999.99,
                    stock=15,
                    image_url='https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500',
                    category='Electrónica'
                ),
                Product(
                    name='iPhone 15 Pro Max',
                    description='Smartphone Apple con chip A17 Pro, 256GB, cámara de 48MP con sistema de triple cámara.',
                    price=27999.00,
                    stock=25,
                    image_url='https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500',
                    category='Electrónica'
                ),
                Product(
                    name='Audífonos Sony WH-1000XM5',
                    description='Audífonos inalámbricos con cancelación de ruido líder en la industria, 30 horas de batería.',
                    price=6499.00,
                    stock=30,
                    image_url='https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=500',
                    category='Audio'
                ),
                Product(
                    name='Monitor Samsung Odyssey G7',
                    description='Monitor curvo 32" WQHD 240Hz, 1ms respuesta, HDR600. Para gaming competitivo.',
                    price=12999.00,
                    stock=10,
                    image_url='https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500',
                    category='Electrónica'
                ),
                Product(
                    name='Teclado Mecánico Razer BlackWidow',
                    description='Teclado mecánico RGB con switches Green, reposamuñecas ergonómico incluido.',
                    price=3299.00,
                    stock=40,
                    image_url='https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=500',
                    category='Periféricos'
                ),
                Product(
                    name='Mouse Logitech G Pro X Superlight',
                    description='Mouse inalámbrico ultra ligero 63g, sensor HERO 25K, 70 horas de batería.',
                    price=2499.00,
                    stock=50,
                    image_url='https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500',
                    category='Periféricos'
                ),
                Product(
                    name='Silla Gamer Secretlab Titan',
                    description='Silla ergonómica premium con soporte lumbar ajustable, reclinable 165°, piel sintética.',
                    price=11999.00,
                    stock=8,
                    image_url='https://images.unsplash.com/photo-1612372606404-0ab33e7187ee?w=500',
                    category='Mobiliario'
                ),
                Product(
                    name='Webcam Logitech StreamCam',
                    description='Webcam Full HD 1080p 60fps, enfoque automático, ideal para streaming y videollamadas.',
                    price=2899.00,
                    stock=20,
                    image_url='https://images.unsplash.com/photo-1587826080692-f439cd0b70da?w=500',
                    category='Periféricos'
                ),
                Product(
                    name='Tablet Samsung Galaxy Tab S9',
                    description='Tablet de 11" con Snapdragon 8 Gen 2, 128GB, S Pen incluido, resistente al agua.',
                    price=14999.00,
                    stock=12,
                    image_url='https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500',
                    category='Electrónica'
                ),
                Product(
                    name='Bocina JBL Charge 5',
                    description='Bocina portátil Bluetooth con 20h de batería, resistencia IP67, powerbank integrado.',
                    price=3199.00,
                    stock=35,
                    image_url='https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500',
                    category='Audio'
                ),
            ]
            db.session.add_all(products)
            print(f'{len(products)} sample products created.')
        else:
            print('Products already exist, skipping product seed.')

        db.session.commit()
        print('Seed completed!')


if __name__ == '__main__':
    seed()
