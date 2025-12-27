// Админ панель - управление товарами и заказами
let currentPage = 'dashboard';
let editProductId = null;

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    setupNavigation();
    loadProducts();
    loadOrders();

    // Форма добавления товара
    document.getElementById('addProductForm').addEventListener('submit', function(e) {
        e.preventDefault();
        addProduct();
    });

    // Форма редактирования товара
    document.getElementById('editProductForm').addEventListener('submit', function(e) {
        e.preventDefault();
        updateProduct();
    });

    // Закрытие модального окна
    document.querySelector('.close-modal').addEventListener('click', function() {
        document.getElementById('editModal').style.display = 'none';
    });
});

// Навигация
function setupNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const pageId = this.getAttribute('href').substring(1);
            showPage(pageId);

            // Обновляем активный класс
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            this.classList.add('active');

            // Обновляем заголовок
            const titles = {
                'dashboard': 'Статистика',
                'products': 'Управление товарами',
                'orders': 'Заказы',
                'add-product': 'Добавить товар'
            };
            document.getElementById('pageTitle').textContent = titles[pageId];
        });
    });
}

// Переключение страниц
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(pageId).classList.add('active');
    currentPage = pageId;
}

// Загрузка статистики
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        document.getElementById('totalProducts').textContent = stats.total_products;
        document.getElementById('totalOrders').textContent = stats.total_orders;
        document.getElementById('pendingOrders').textContent = stats.pending_orders;
        document.getElementById('totalRevenue').textContent = stats.total_revenue + ' ₽';

        // Обновляем график (если есть)
        if (typeof updateChart === 'function') {
            updateChart(stats.chart_data);
        }
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

// Загрузка товаров
async function loadProducts() {
    try {
        const response = await fetch('/api/admin/products');
        const products = await response.json();

        const tableBody = document.getElementById('productsTable');
        tableBody.innerHTML = '';

        products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${product.id}</td>
                <td>
                    <img src="${product.image_url || 'https://via.placeholder.com/50'}"
                         alt="${product.name}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;">
                </td>
                <td>${product.name}</td>
                <td>${product.price} ₽</td>
                <td>
                    <span class="stock-badge ${product.stock > 0 ? 'in-stock' : 'out-of-stock'}">
                        ${product.stock} шт.
                    </span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-edit" onclick="openEditModal(${product.id}, '${product.name}', ${product.price}, ${product.stock})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn-delete" onclick="deleteProduct(${product.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Ошибка загрузки товаров:', error);
    }
}

// Загрузка заказов
async function loadOrders() {
    try {
        const response = await fetch('/api/admin/orders');
        const orders = await response.json();

        const tableBody = document.getElementById('ordersTable');
        tableBody.innerHTML = '';

        orders.forEach(order => {
            const items = JSON.parse(order.items);
            const itemsText = items.map(item => `${item.name} (×${item.quantity})`).join(', ');

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>#${order.id}</td>
                <td>${order.username || `Пользователь ${order.user_id}`}</td>
                <td title="${itemsText}">${items.length} товаров</td>
                <td>${order.total_price} ₽</td>
                <td>
                    <select class="status-select" data-order-id="${order.id}" onchange="updateOrderStatus(${order.id}, this.value)">
                        <option value="pending" ${order.status === 'pending' ? 'selected' : ''}>Ожидает</option>
                        <option value="processing" ${order.status === 'processing' ? 'selected' : ''}>В обработке</option>
                        <option value="completed" ${order.status === 'completed' ? 'selected' : ''}>Завершен</option>
                        <option value="cancelled" ${order.status === 'cancelled' ? 'selected' : ''}>Отменен</option>
                    </select>
                </td>
                <td>${new Date(order.created_at).toLocaleDateString()}</td>
                <td>
                    <button class="btn-view" onclick="viewOrderDetails(${order.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error('Ошибка загрузки заказов:', error);
    }
}

// Добавление товара
async function addProduct() {
    const formData = {
        name: document.getElementById('name').value,
        description: document.getElementById('description').value,
        price: parseFloat(document.getElementById('price').value),
        stock: parseInt(document.getElementById('stock').value),
        category: document.getElementById('category').value,
        image_url: document.getElementById('image_url').value || 'https://via.placeholder.com/300x200'
    };

    try {
        const response = await fetch('/api/admin/products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            alert('✅ Товар успешно добавлен!');
            document.getElementById('addProductForm').reset();
            loadProducts();
            loadStats();
            showPage('products');
        } else {
            alert('❌ Ошибка при добавлении товара');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('❌ Ошибка при добавлении товара');
    }
}

// Открытие модального окна редактирования
function openEditModal(id, name, price, stock) {
    editProductId = id;
    document.getElementById('editId').value = id;
    document.getElementById('editName').value = name;
    document.getElementById('editPrice').value = price;
    document.getElementById('editStock').value = stock;
    document.getElementById('editModal').style.display = 'flex';
}

// Обновление товара
async function updateProduct() {
    const formData = {
        id: editProductId,
        name: document.getElementById('editName').value,
        price: parseFloat(document.getElementById('editPrice').value),
        stock: parseInt(document.getElementById('editStock').value)
    };

    try {
        const response = await fetch(`/api/admin/products?id=${editProductId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            alert('✅ Товар успешно обновлен!');
            document.getElementById('editModal').style.display = 'none';
            loadProducts();
            loadStats();
        } else {
            alert('❌ Ошибка при обновлении товара');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('❌ Ошибка при обновлении товара');
    }
}

// Удаление товара
async function deleteProduct(productId) {
    if (!confirm('Вы уверены, что хотите удалить этот товар?')) return;

    try {
        const response = await fetch(`/api/admin/products?id=${productId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('✅ Товар удален!');
            loadProducts();
            loadStats();
        } else {
            alert('❌ Ошибка при удалении товара');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('❌ Ошибка при удалении товара');
    }
}

// Обновление статуса заказа
async function updateOrderStatus(orderId, status) {
    try {
        const response = await fetch(`/api/admin/orders/${orderId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status })
        });

        if (response.ok) {
            console.log(`Статус заказа #${orderId} изменен на ${status}`);
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

// Просмотр деталей заказа
function viewOrderDetails(orderId) {
    alert(`Просмотр заказа #${orderId}\nДетальная информация будет здесь`);
    // Можно реализовать модальное окно с деталями
}

// Обновление всех данных
function loadData() {
    loadStats();
    if (currentPage === 'products') loadProducts();
    if (currentPage === 'orders') loadOrders();
}

// Автоматическое обновление каждые 30 секунд
setInterval(loadData, 30000);