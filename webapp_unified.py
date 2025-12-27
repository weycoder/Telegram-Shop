"""
Единый Flask сервер для PythonAnywhere
Обслуживает и Web App, и API, и статические файлы
"""
import os
import sys
from flask import Flask, render_template, jsonify, request, send_from_directory
from flaskcors import CORS
import sqlite3
import json

# Добавляем пути для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__,
            static_folder='webapp/frontend',
            template_folder='templates')
CORS(app)

# ========== КОНФИГУРАЦИЯ ==========
class Config:
    DATABASE = 'shop.db'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

app.config.from_object(Config)

# ========== ПОМОЩНИКИ БАЗЫ ДАННЫХ ==========
def get_db():
    """Подключение к базе данных"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()

    # Таблица товаров
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        image_url TEXT,
        category TEXT,
        stock INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Таблица заказов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT,
        items TEXT NOT NULL,
        total_price REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Тестовые данные
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        test_products = [
            ('iPhone 15 Pro', 'Новый смартфон Apple', 999.99, 'https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/iphone-15-pro-finish-select-202309-6-7inch?wid=5120&hei=2880&fmt=webp&qlt=70&.v=1693009279096', 'Телефоны', 10),
            ('Samsung Galaxy S23', 'Флагман Samsung', 899.99, 'https://images.samsung.com/is/image/samsung/p6pim/ru/2302/gallery/ru-galaxy-s23-s911-sm-s911bzadeub-534866168?$650_519_PNG$', 'Телефоны', 15),
            ('Наушники Sony WH-1000XM5', 'Беспроводные шумоподавляющие', 349.99, 'https://sony.scene7.com/is/image/sonyglobalsolutions/WH-1000XM5-B_primary-image?$categorypdpnav$&fmt=png-alpha', 'Аксессуары', 20),
            ('Ноутбук MacBook Air M2', 'Легкий и мощный', 1299.99, 'https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/macbook-air-midnight-select-20220606?wid=904&hei=840&fmt=jpeg&qlt=90&.v=1653084303665', 'Ноутбуки', 8),
            ('Часы Apple Watch Series 9', 'Умные часы', 399.99, 'https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/watch-card-40-s9-202309_GEO_RU?wid=680&hei=528&fmt=p-jpg&qlt=95&.v=1693340630862', 'Гаджеты', 12)
        ]

        cursor.executemany('''
        INSERT INTO products (name, description, price, image_url, category, stock)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', test_products)

    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

# Инициализируем БД при первом запуске
with app.app_context():
    init_db()

# ========== СТАТИЧЕСКИЕ ФАЙЛЫ ==========
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/admin/static/<path:filename>')
def admin_static_files(filename):
    return send_from_directory('admin', filename)

# ========== WEB APP СТРАНИЦЫ ==========
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webapp')
def webapp_page():
    return render_template('webapp.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

# ========== API ДЛЯ WEB APP ==========
@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    conn = get_db()

    if category and category != 'all':
        products = conn.execute(
            'SELECT * FROM products WHERE category = ? AND stock > 0',
            (category,)
        ).fetchall()
    else:
        products = conn.execute(
            'SELECT * FROM products WHERE stock > 0'
        ).fetchall()

    conn.close()
    return jsonify([dict(product) for product in products])

@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db()
    categories = conn.execute(
        'SELECT DISTINCT category FROM products WHERE category IS NOT NULL'
    ).fetchall()
    conn.close()
    return jsonify([row['category'] for row in categories])

@app.route('/api/create-order', methods=['POST'])
def create_order():
    data = request.json
    conn = get_db()

    conn.execute('''
    INSERT INTO orders (user_id, username, items, total_price, status)
    VALUES (?, ?, ?, ?, 'pending')
    ''', (
        data.get('user_id', 0),
        data.get('username', 'Гость'),
        json.dumps(data['items'], ensure_ascii=False),
        data['total']
    ))

    # Обновляем остатки
    for item in data['items']:
        conn.execute(
            'UPDATE products SET stock = stock - ? WHERE id = ?',
            (item['quantity'], item['id'])
        )

    conn.commit()
    order_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    conn.close()

    return jsonify({'success': True, 'order_id': order_id})

# ========== API ДЛЯ АДМИНКИ ==========
@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db()

    total_products = conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    total_orders = conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    pending_orders = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE status = 'pending'"
    ).fetchone()[0]

    revenue_result = conn.execute(
        'SELECT SUM(total_price) FROM orders WHERE status = "completed"'
    ).fetchone()[0]
    total_revenue = revenue_result if revenue_result else 0

    conn.close()

    return jsonify({
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue
    })

@app.route('/api/admin/products', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_products():
    conn = get_db()

    if request.method == 'GET':
        products = conn.execute(
            'SELECT * FROM products ORDER BY created_at DESC'
        ).fetchall()
        conn.close()
        return jsonify([dict(product) for product in products])

    elif request.method == 'POST':
        data = request.json
        conn.execute('''
        INSERT INTO products (name, description, price, image_url, category, stock)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['description'],
            data['price'],
            data.get('image_url', ''),
            data.get('category', ''),
            data.get('stock', 0)
        ))
        conn.commit()
        product_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()
        return jsonify({'success': True, 'id': product_id})

    elif request.method == 'PUT':
        data = request.json
        product_id = request.args.get('id')

        conn.execute('''
        UPDATE products 
        SET name = ?, price = ?, stock = ?
        WHERE id = ?
        ''', (
            data['name'],
            data['price'],
            data['stock'],
            product_id
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

    elif request.method == 'DELETE':
        product_id = request.args.get('id')
        conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/api/admin/orders', methods=['GET'])
def get_orders():
    conn = get_db()
    orders = conn.execute(
        'SELECT * FROM orders ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return jsonify([dict(order) for order in orders])

@app.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    data = request.json
    conn = get_db()

    conn.execute(
        'UPDATE orders SET status = ? WHERE id = ?',
        (data['status'], order_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True})

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    app.run(debug=True)