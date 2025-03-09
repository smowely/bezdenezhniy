from app import app, db, MenuItem

# Примеры блюд для меню
menu_items = [
    {
        "name": "Борщ",
        "description": "Традиционный украинский борщ со сметаной и зеленью",
        "price": 250.0,
        "category": "еда"
    },
    {
        "name": "Картофельное пюре",
        "description": "Нежное картофельное пюре с маслом",
        "price": 150.0,
        "category": "еда"
    },
    {
        "name": "Котлеты",
        "description": "Сочные котлеты из говядины и свинины",
        "price": 280.0,
        "category": "еда"
    },
    {
        "name": "Салат Цезарь",
        "description": "Классический салат Цезарь с курицей и сыром пармезан",
        "price": 320.0,
        "category": "еда"
    },
    {
        "name": "Паста Карбонара",
        "description": "Итальянская паста с беконом, сыром и сливочным соусом",
        "price": 350.0,
        "category": "еда"
    },
    {
        "name": "Кофе Американо",
        "description": "Классический американо из свежемолотых зерен",
        "price": 120.0,
        "category": "напиток"
    },
    {
        "name": "Чай черный",
        "description": "Черный чай с сахаром и лимоном",
        "price": 90.0,
        "category": "напиток"
    },
    {
        "name": "Морс ягодный",
        "description": "Освежающий морс из лесных ягод",
        "price": 110.0,
        "category": "напиток"
    }
]

def add_menu_items():
    with app.app_context():
        # Проверяем, есть ли уже блюда в базе
        existing_count = MenuItem.query.count()
        if existing_count > 0:
            print(f"В базе данных уже есть {existing_count} блюд. Пропускаем добавление.")
            return
        
        # Добавляем блюда
        for item_data in menu_items:
            menu_item = MenuItem(
                name=item_data["name"],
                description=item_data["description"],
                price=item_data["price"],
                category=item_data["category"],
                is_available=True
            )
            db.session.add(menu_item)
        
        # Сохраняем изменения
        db.session.commit()
        print(f"Добавлено {len(menu_items)} блюд в базу данных.")

if __name__ == "__main__":
    add_menu_items() 