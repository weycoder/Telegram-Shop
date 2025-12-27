from flask import Flask, render_template_string, jsonify, request
import sqlite3
import json

app = Flask(__name__)


# Главная страница
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Telegram Shop</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; }
            .btn { display: inline-block; margin: 10px; padding: 15px 30px; 
                   background: #0088cc; color: white; text-decoration: none; 
                   border-radius: 10px; font-size: 18px; }
            .container { max-width: 800px; margin: 0 auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛍️ Telegram Shop</h1>
            <p>Интернет-магазин в Telegram</p>

            <div>
                <a href="/shop" class="btn">🛒 Открыть магазин</a>
                <a href="/admin" class="btn">👨‍💼 Админ-панель</a>
            </div>

            <div style="margin-top: 50px; padding: 20px; background: #f5f5f5; border-radius: 10px;">
                <h3>API Endpoints:</h3>
                <p><a href="/api/products">/api/products</a> - Список товаров</p>
                <p><a href="/api/status">/api/status</a> - Статус сервера</p>
            </div>
        </div>
    </body>
    </html>
    '''


# Страница магазина
@app.route('/shop')
def shop():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Магазин</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: Arial; background: #f5f7fa; padding: 20px; }
            .header { background: white; padding: 20px; border-radius: 15px; 
                     margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .products { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
            .product-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .product-img { width: 100%; height: 150px; object-fit: cover; border-radius: 5px; margin-bottom: 10px; }
            .price { color: #0088cc; font-weight: bold; font-size: 20px; margin: 10px 0; }
            button { background: #0088cc; color: white; border: none; padding: 10px; width: 100%; 
                     border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛒 Магазин товаров</h1>
            <p>Выберите товары для покупки</p>
        </div>

        <div class="products" id="products">
            <div class="product-card">
                <img src="https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/iphone-15-pro-finish-select-202309-6-7inch?wid=5120&hei=2880&fmt=webp&qlt=70&.v=1693009279096" 
                     class="product-img">
                <h3>iPhone 15 Pro</h3>
                <p>Новый смартфон Apple</p>
                <div class="price">999.99 ₽</div>
                <button onclick="alert('Товар добавлен в корзину!')">В корзину</button>
            </div>

            <div class="product-card">
                <img src="https://images.samsung.com/is/image/samsung/p6pim/ru/2302/gallery/ru-galaxy-s23-s911-sm-s911bzadeub-534866168?$650_519_PNG$" 
                     class="product-img">
                <h3>Samsung Galaxy S23</h3>
                <p>Флагман Samsung</p>
                <div class="price">899.99 ₽</div>
                <button onclick="alert('Товар добавлен в корзину!')">В корзину</button>
            </div>

            <div class="product-card">
                <img src="https://sony.scene7.com/is/image/sonyglobalsolutions/WH-1000XM5-B_primary-image?$categorypdpnav$&fmt=png-alpha" 
                     class="product-img">
                <h3>Наушники Sony</h3>
                <p>Шумоподавляющие</p>
                <div class="price">349.99 ₽</div>
                <button onclick="alert('Товар добавлен в корзину!')">В корзину</button>
            </div>
        </div>

        <script>
            // Telegram Web App интеграция
            if (window.Telegram && Telegram.WebApp) {
                Telegram.WebApp.expand();
                Telegram.WebApp.setHeaderColor('#0088cc');
                document.querySelector('.header').innerHTML = 
                    '<h1>🛒 Магазин в Telegram</h1><p>Добро пожаловать!</p>' + 
                    document.querySelector('.header').innerHTML;
            }
        </script>
    </body>
    </html>
    '''


# API эндпоинты
@app.route('/api/products')
def get_products():
    products = [
        {"id": 1, "name": "iPhone 15 Pro", "price": 999.99, "stock": 10},
        {"id": 2, "name": "Samsung Galaxy S23", "price": 899.99, "stock": 15},
        {"id": 3, "name": "Наушники Sony", "price": 349.99, "stock": 20}
    ]
    return jsonify(products)


@app.route('/api/status')
def status():
    return jsonify({"status": "online", "service": "Telegram Shop"})


if __name__ == '__main__':
    app.run(debug=True)