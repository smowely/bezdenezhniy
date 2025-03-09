from app import app, db, Product

# Список базовых продуктов для добавления
products = [
    {"name": "Мука пшеничная", "unit": "кг", "quantity": 10.0},
    {"name": "Сахар", "unit": "кг", "quantity": 5.0},
    {"name": "Соль", "unit": "кг", "quantity": 2.0},
    {"name": "Масло растительное", "unit": "л", "quantity": 3.0},
    {"name": "Масло сливочное", "unit": "кг", "quantity": 2.0},
    {"name": "Молоко", "unit": "л", "quantity": 5.0},
    {"name": "Яйца", "unit": "шт", "quantity": 30.0},
    {"name": "Картофель", "unit": "кг", "quantity": 15.0},
    {"name": "Морковь", "unit": "кг", "quantity": 5.0},
    {"name": "Лук репчатый", "unit": "кг", "quantity": 5.0},
    {"name": "Чеснок", "unit": "кг", "quantity": 1.0},
    {"name": "Помидоры", "unit": "кг", "quantity": 5.0},
    {"name": "Огурцы", "unit": "кг", "quantity": 5.0},
    {"name": "Капуста белокочанная", "unit": "кг", "quantity": 5.0},
    {"name": "Говядина", "unit": "кг", "quantity": 10.0},
    {"name": "Свинина", "unit": "кг", "quantity": 10.0},
    {"name": "Курица", "unit": "кг", "quantity": 10.0},
    {"name": "Рыба (филе)", "unit": "кг", "quantity": 5.0},
    {"name": "Рис", "unit": "кг", "quantity": 5.0},
    {"name": "Гречка", "unit": "кг", "quantity": 5.0},
    {"name": "Макароны", "unit": "кг", "quantity": 5.0},
    {"name": "Сыр твердый", "unit": "кг", "quantity": 3.0},
    {"name": "Сметана", "unit": "кг", "quantity": 2.0},
    {"name": "Творог", "unit": "кг", "quantity": 2.0},
    {"name": "Кофе молотый", "unit": "кг", "quantity": 1.0},
    {"name": "Чай черный", "unit": "кг", "quantity": 0.5},
    {"name": "Чай зеленый", "unit": "кг", "quantity": 0.5},
    {"name": "Сахарная пудра", "unit": "кг", "quantity": 1.0},
    {"name": "Какао-порошок", "unit": "кг", "quantity": 1.0},
    {"name": "Шоколад", "unit": "кг", "quantity": 2.0},
    {"name": "Ванильный сахар", "unit": "кг", "quantity": 0.5},
    {"name": "Корица", "unit": "кг", "quantity": 0.2},
    {"name": "Лимон", "unit": "кг", "quantity": 2.0},
    {"name": "Апельсины", "unit": "кг", "quantity": 3.0},
    {"name": "Яблоки", "unit": "кг", "quantity": 5.0},
    {"name": "Бананы", "unit": "кг", "quantity": 5.0},
    {"name": "Сода пищевая", "unit": "кг", "quantity": 0.5},
    {"name": "Разрыхлитель", "unit": "кг", "quantity": 0.5},
    {"name": "Дрожжи сухие", "unit": "кг", "quantity": 0.5},
    {"name": "Мед", "unit": "кг", "quantity": 1.0},
]

def add_products():
    with app.app_context():
        # Проверяем, есть ли уже продукты в базе
        existing_count = Product.query.count()
        if existing_count > 0:
            print(f"В базе данных уже есть {existing_count} продуктов. Пропускаем добавление.")
            return
        
        # Добавляем продукты
        for product_data in products:
            product = Product(
                name=product_data["name"],
                unit=product_data["unit"],
                quantity=product_data["quantity"]
            )
            db.session.add(product)
        
        # Сохраняем изменения
        db.session.commit()
        print(f"Добавлено {len(products)} продуктов в базу данных.")

if __name__ == "__main__":
    add_products() 