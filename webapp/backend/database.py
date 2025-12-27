import sqlite3
import json
from datetime import datetime


def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()

    # Таблица товаров
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS products
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       name
                       TEXT
                       NOT
                       NULL,
                       description
                       TEXT,
                       price
                       REAL
                       NOT
                       NULL,
                       image_url
                       TEXT,
                       category
                       TEXT,
                       stock
                       INTEGER
                       DEFAULT
                       0,
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')

    # Таблица заказов
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS orders
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       user_id
                       INTEGER
                       NOT
                       NULL,
                       username
                       TEXT,
                       items
                       TEXT
                       NOT
                       NULL,
                       total_price
                       REAL
                       NOT
                       NULL,
                       status
                       TEXT
                       DEFAULT
                       'pending',
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')

    # Добавляем тестовые товары
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        test_products = [
            ('iPhone 15 Pro', 'Новый смартфон Apple', 999.99,
             'https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/iphone-15-pro-finish-select-202309-6-7inch?wid=5120&hei=2880&fmt=webp&qlt=70&.v=1693009279096',
             'Телефоны', 10),
            ('Samsung Galaxy S23', 'Флагман Samsung', 899.99,
             'https://images.samsung.com/is/image/samsung/p6pim/ru/2302/gallery/ru-galaxy-s23-s911-sm-s911bzadeub-534866168?$650_519_PNG$',
             'Телефоны', 15),
            ('Наушники Sony WH-1000XM5', 'Беспроводные шумоподавляющие', 349.99,
             'https://sony.scene7.com/is/image/sonyglobalsolutions/WH-1000XM5-B_primary-image?$categorypdpnav$&fmt=png-alpha',
             'Аксессуары', 20),
            ('Ноутбук MacBook Air M2', 'Легкий и мощный', 1299.99,
             'https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/macbook-air-midnight-select-20220606?wid=904&hei=840&fmt=jpeg&qlt=90&.v=1653084303665',
             'Ноутбуки', 8),
            ('Часы Apple Watch Series 9', 'Умные часы', 399.99,
             'https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/watch-card-40-s9-202309_GEO_RU?wid=680&hei=528&fmt=p-jpg&qlt=95&.v=1693340630862',
             'Гаджеты', 12)
        ]

        cursor.executemany('''
                           INSERT INTO products (name, description, price, image_url, category, stock)
                           VALUES (?, ?, ?, ?, ?, ?)
                           ''', test_products)

    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")


def get_db_connection():
    """Получение подключения к БД"""
    conn = sqlite3.connect('shop.db')
    conn.row_factory = sqlite3.Row
    return conn