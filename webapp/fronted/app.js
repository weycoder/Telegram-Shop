// Инициализация корзины
let cart = JSON.parse(localStorage.getItem('cart')) || [];
let currentProduct = null;

// Telegram Web App интеграция
if (window.Telegram?.WebApp) {
    Telegram.WebApp.expand();
    Telegram.WebApp.enableClosingConfirmation();
    Telegram.WebApp.setHeaderColor('#667eea');
    Telegram.WebApp.setBackgroundColor('#667eea');
}

// Загрузка товаров
async function loadProducts(category = 'all') {
    try {
        const response = await fetch(`/api/products${category !== 'all' ? `?category=${category}` : ''}`);
        const products = await response.json();

        const productsGrid = document.getElementById('products');
        productsGrid.innerHTML = '';

        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'product-card';
            productCard.innerHTML = `
                <img src="${product.image_url || 'https://via.placeholder.com/300x200'}"
                     alt="${product.name}" class="product-image">
                <div class="product-info">
                    <h3 class="product-title">${product.name}</h3>
                    <p class="product-description">${product.description?.substring(0, 60)}...</p>
                    <div class="product-price">${product.price} ₽</div>
                    <div class="product-stock">В наличии: ${product.stock} шт.</div>
                    <button class="add-to-cart" onclick="addToCart(${product.id}, '${product.name}', ${product.price}, 1)">
                        <i class="fas fa-cart-plus"></i> В корзину
                    </button>
                </div>
            `;

            productCard.onclick = () => openProductModal(product);
            productsGrid.appendChild(productCard);
        });

        updateCartCount();
    } catch (error) {
        console.error('Ошибка загрузки товаров:', error);
    }
}

// Загрузка категорий
async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        const categories = await response.json();

        const categoriesDiv = document.getElementById('categories');
        categoriesDiv.innerHTML = `
            <button class="category-btn active" onclick="changeCategory('all')">Все товары</button>
            ${categories.map(cat => `
                <button class="category-btn" onclick="changeCategory('${cat}')">${cat}</button>
            `).join('')}
        `;
    } catch (error) {
        console.error('Ошибка загрузки категорий:', error);
    }
}

// Смена категории
function changeCategory(category) {
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    loadProducts(category);
}

// Открытие модального окна товара
function openProductModal(product) {
    currentProduct = product;
    document.getElementById('modalTitle').textContent = product.name;
    document.getElementById('modalImage').src = product.image_url || 'https://via.placeholder.com/300x200';
    document.getElementById('modalDescription').textContent = product.description;
    document.getElementById('modalPrice').textContent = `${product.price} ₽`;
    document.getElementById('quantity').value = 1;
    document.getElementById('productModal').style.display = 'flex';
}

// Закрытие модальных окон
document.querySelectorAll('.close-modal, .close-cart').forEach(btn => {
    btn.onclick = function() {
        document.getElementById('productModal').style.display = 'none';
        document.getElementById('cartOverlay').style.display = 'none';
    };
});

// Управление корзиной
function addToCart(productId, name, price, quantity = 1) {
    const existingItem = cart.find(item => item.id === productId);

    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({
            id: productId,
            name,
            price,
            quantity,
            image: currentProduct?.image_url
        });
    }

    saveCart();
    updateCartCount();
    showNotification('Товар добавлен в корзину!');
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    saveCart();
    updateCartDisplay();
    updateCartCount();
}

function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function updateCartCount() {
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    document.getElementById('cartCount').textContent = totalItems;
}

function updateCartDisplay() {
    const cartItems = document.getElementById('cartItems');
    const cartTotal = document.getElementById('cartTotal');

    if (cart.length === 0) {
        cartItems.innerHTML = '<p style="text-align: center; padding: 20px;">Корзина пуста</p>';
        cartTotal.textContent = '0';
        return;
    }

    cartItems.innerHTML = cart.map(item => `
        <div class="cart-item">
            <img src="${item.image || 'https://via.placeholder.com/100'}"
                 alt="${item.name}" class="cart-item-image">
            <div class="cart-item-info">
                <h4>${item.name}</h4>
                <div class="cart-item-price">${item.price} ₽ × ${item.quantity}</div>
                <div class="cart-item-total">${item.price * item.quantity} ₽</div>
            </div>
            <div class="remove-item" onclick="removeFromCart(${item.id})">
                <i class="fas fa-trash"></i>
            </div>
        </div>
    `).join('');

    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    cartTotal.textContent = total.toFixed(2);
}

// Оформление заказа
document.getElementById('checkoutBtn').onclick = async function() {
    if (cart.length === 0) {
        alert('Корзина пуста!');
        return;
    }

    try {
        const orderData = {
            items: cart,
            total: cart.reduce((sum, item) => sum + (item.price * item.quantity), 0)
        };

        // Если в Telegram Web App
        if (window.Telegram?.WebApp) {
            const user = Telegram.WebApp.initDataUnsafe.user;
            orderData.user_id = user.id;
            orderData.username = user.username || `${user.first_name} ${user.last_name}`;
        }

        const response = await fetch('/api/create-order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        });

        const result = await response.json();

        if (result.success) {
            showNotification('Заказ оформлен!');
            cart = [];
            saveCart();
            updateCartCount();
            updateCartDisplay();
            document.getElementById('cartOverlay').style.display = 'none';

            // Показать уведомление в Telegram
            if (window.Telegram?.WebApp) {
                Telegram.WebApp.showAlert('✅ Заказ успешно оформлен!');
            }
        }
    } catch (error) {
        console.error('Ошибка оформления заказа:', error);
        alert('Ошибка при оформлении заказа');
    }
};

// Уведомления
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Управление корзиной (открытие/закрытие)
document.getElementById('cartBtn').onclick = function() {
    updateCartDisplay();
    document.getElementById('cartOverlay').style.display = 'block';
};

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    loadProducts();
    loadCategories();
    updateCartCount();

    // Обработчики для модального окна
    document.getElementById('addToCartModal').onclick = function() {
        const quantity = parseInt(document.getElementById('quantity').value);
        if (currentProduct) {
            addToCart(currentProduct.id, currentProduct.name, currentProduct.price, quantity);
            document.getElementById('productModal').style.display = 'none';
        }
    };

    // Кнопки +/-
    document.querySelector('.qty-btn.minus').onclick = function() {
        const input = document.getElementById('quantity');
        if (input.value > 1) input.value = parseInt(input.value) - 1;
    };

    document.querySelector('.qty-btn.plus').onclick = function() {
        const input = document.getElementById('quantity');
        input.value = parseInt(input.value) + 1;
    };
});