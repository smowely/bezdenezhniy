from app import app, db, MenuItem, Product, RecipeItem

# Примеры рецептов для блюд
recipes = {
    "Борщ": [
        {"product": "Говядина", "quantity": 0.3},
        {"product": "Капуста белокочанная", "quantity": 0.2},
        {"product": "Свекла", "quantity": 0.2},
        {"product": "Морковь", "quantity": 0.1},
        {"product": "Лук репчатый", "quantity": 0.1},
        {"product": "Картофель", "quantity": 0.2},
        {"product": "Томатная паста", "quantity": 0.05},
        {"product": "Соль", "quantity": 0.01},
    ],
    "Картофельное пюре": [
        {"product": "Картофель", "quantity": 0.3},
        {"product": "Молоко", "quantity": 0.1},
        {"product": "Масло сливочное", "quantity": 0.03},
        {"product": "Соль", "quantity": 0.005},
    ],
    "Котлеты": [
        {"product": "Говядина", "quantity": 0.15},
        {"product": "Свинина", "quantity": 0.15},
        {"product": "Лук репчатый", "quantity": 0.05},
        {"product": "Яйца", "quantity": 1},
        {"product": "Соль", "quantity": 0.005},
        {"product": "Масло растительное", "quantity": 0.03},
    ],
    "Салат Цезарь": [
        {"product": "Курица", "quantity": 0.15},
        {"product": "Салат Романо", "quantity": 0.1},
        {"product": "Сыр твердый", "quantity": 0.05},
        {"product": "Хлеб белый", "quantity": 0.05},
        {"product": "Масло оливковое", "quantity": 0.02},
        {"product": "Соль", "quantity": 0.003},
    ],
    "Паста Карбонара": [
        {"product": "Макароны", "quantity": 0.15},
        {"product": "Бекон", "quantity": 0.1},
        {"product": "Сыр твердый", "quantity": 0.05},
        {"product": "Яйца", "quantity": 1},
        {"product": "Сливки", "quantity": 0.1},
        {"product": "Соль", "quantity": 0.003},
    ],
    "Кофе Американо": [
        {"product": "Кофе молотый", "quantity": 0.015},
        {"product": "Вода", "quantity": 0.2},
    ],
    "Чай черный": [
        {"product": "Чай черный", "quantity": 0.003},
        {"product": "Вода", "quantity": 0.2},
    ],
    "Морс ягодный": [
        {"product": "Ягоды замороженные", "quantity": 0.05},
        {"product": "Сахар", "quantity": 0.02},
        {"product": "Вода", "quantity": 0.25},
    ],
}

def add_recipes():
    with app.app_context():
        # Получаем все блюда
        menu_items = MenuItem.query.all()
        
        # Получаем все продукты
        products = {product.name: product for product in Product.query.all()}
        
        # Проверяем, есть ли уже рецепты
        existing_count = RecipeItem.query.count()
        if existing_count > 0:
            print(f"В базе данных уже есть {existing_count} рецептов. Пропускаем добавление.")
            return
        
        # Добавляем недостающие продукты
        missing_products = set()
        for recipe_name, ingredients in recipes.items():
            for ingredient in ingredients:
                if ingredient["product"] not in products:
                    missing_products.add(ingredient["product"])
        
        for product_name in missing_products:
            product = Product(name=product_name, unit="кг", quantity=5.0)
            db.session.add(product)
            products[product_name] = product
        
        db.session.commit()
        
        # Добавляем рецепты для существующих блюд
        recipes_added = 0
        for menu_item in menu_items:
            if menu_item.name in recipes:
                for ingredient in recipes[menu_item.name]:
                    product = products.get(ingredient["product"])
                    if product:
                        recipe_item = RecipeItem(
                            menu_item_id=menu_item.id,
                            product_id=product.id,
                            quantity=ingredient["quantity"]
                        )
                        db.session.add(recipe_item)
                        recipes_added += 1
        
        db.session.commit()
        print(f"Добавлено {recipes_added} ингредиентов для рецептов.")

if __name__ == "__main__":
    add_recipes() 