from app import app, db, User, Employee, Order, Shift, MenuItem, OrderItem, Product, RecipeItem, MenuCategory
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import os

def init_database():
    with app.app_context():
        # Удаляем существующую базу данных, если она есть
        db_path = os.path.join('instance', 'cafe.db')
        if os.path.exists(db_path):
            print(f"Удаление существующей базы данных: {db_path}")
            os.remove(db_path)
        
        # Создаем таблицы
        print("Создание таблиц базы данных...")
        db.create_all()
        
        # Добавляем пользователей
        print("Добавление пользователей...")
        users = [
            User(
                username='admin',
                password=generate_password_hash('admin'),
                role='admin',
                status='активен'
            ),
            User(
                username='waiter1',
                password=generate_password_hash('waiter1'),
                role='waiter',
                status='активен'
            ),
            User(
                username='waiter2',
                password=generate_password_hash('waiter2'),
                role='waiter',
                status='активен'
            ),
            User(
                username='cook1',
                password=generate_password_hash('cook1'),
                role='cook',
                status='активен'
            ),
            User(
                username='cook2',
                password=generate_password_hash('cook2'),
                role='cook',
                status='активен'
            )
        ]
        
        for user in users:
            db.session.add(user)
        
        db.session.flush()  # Получаем ID пользователей
        
        # Добавляем сотрудников
        print("Добавление сотрудников...")
        employees = [
            Employee(
                name='Иванов Иван Иванович',
                position='Администратор',
                phone='+7 (999) 123-45-67',
                email='ivanov@example.com',
                hire_date=datetime.now().date() - timedelta(days=90),
                status='активен',
                user_id=users[0].id  # admin
            ),
            Employee(
                name='Петрова Анна Сергеевна',
                position='Официант',
                phone='+7 (999) 234-56-78',
                email='petrova@example.com',
                hire_date=datetime.now().date() - timedelta(days=60),
                status='активен',
                user_id=users[1].id  # waiter1
            ),
            Employee(
                name='Сидоров Алексей Петрович',
                position='Официант',
                phone='+7 (999) 345-67-89',
                email='sidorov@example.com',
                hire_date=datetime.now().date() - timedelta(days=45),
                status='активен',
                user_id=users[2].id  # waiter2
            ),
            Employee(
                name='Козлова Мария Ивановна',
                position='Повар',
                phone='+7 (999) 456-78-90',
                email='kozlova@example.com',
                hire_date=datetime.now().date() - timedelta(days=30),
                status='активен',
                user_id=users[3].id  # cook1
            ),
            Employee(
                name='Смирнов Дмитрий Александрович',
                position='Повар',
                phone='+7 (999) 567-89-01',
                email='smirnov@example.com',
                hire_date=datetime.now().date() - timedelta(days=15),
                status='активен',
                user_id=users[4].id  # cook2
            )
        ]
        
        for employee in employees:
            db.session.add(employee)
        
        db.session.flush()  # Получаем ID сотрудников
        
        # Добавляем категории блюд
        print("Добавление категорий блюд...")
        categories = [
            MenuCategory(name='Горячие блюда', description='Основные горячие блюда'),
            MenuCategory(name='Супы', description='Первые блюда'),
            MenuCategory(name='Салаты', description='Холодные закуски и салаты'),
            MenuCategory(name='Десерты', description='Сладкие блюда и десерты'),
            MenuCategory(name='Напитки', description='Горячие и холодные напитки')
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.flush()  # Получаем ID категорий
        
        # Добавляем позиции меню
        print("Добавление позиций меню...")
        menu_items = [
            MenuItem(name='Стейк из говядины', description='Сочный стейк из мраморной говядины', price=650.0, category='Горячие блюда', is_available=True),
            MenuItem(name='Паста Карбонара', description='Классическая итальянская паста с беконом и сливочным соусом', price=450.0, category='Горячие блюда', is_available=True),
            MenuItem(name='Борщ', description='Традиционный украинский борщ со сметаной', price=350.0, category='Супы', is_available=True),
            MenuItem(name='Грибной суп', description='Суп из белых грибов со сливками', price=380.0, category='Супы', is_available=True),
            MenuItem(name='Цезарь с курицей', description='Салат Цезарь с куриным филе и соусом', price=420.0, category='Салаты', is_available=True),
            MenuItem(name='Греческий салат', description='Классический греческий салат с сыром фета', price=380.0, category='Салаты', is_available=True),
            MenuItem(name='Тирамису', description='Итальянский десерт с маскарпоне', price=320.0, category='Десерты', is_available=True),
            MenuItem(name='Чизкейк', description='Классический чизкейк с ягодным соусом', price=350.0, category='Десерты', is_available=True),
            MenuItem(name='Капучино', description='Кофейный напиток с молоком', price=180.0, category='Напитки', is_available=True),
            MenuItem(name='Чай зеленый', description='Зеленый чай с жасмином', price=150.0, category='Напитки', is_available=True)
        ]
        
        for item in menu_items:
            db.session.add(item)
        
        db.session.flush()  # Получаем ID позиций меню
        
        # Добавляем продукты
        print("Добавление продуктов...")
        products = [
            Product(name='Говядина', unit='кг', quantity=10.0),
            Product(name='Свинина', unit='кг', quantity=8.0),
            Product(name='Курица', unit='кг', quantity=15.0),
            Product(name='Мука', unit='кг', quantity=20.0),
            Product(name='Сахар', unit='кг', quantity=15.0),
            Product(name='Соль', unit='кг', quantity=5.0),
            Product(name='Перец', unit='кг', quantity=2.0),
            Product(name='Масло растительное', unit='л', quantity=10.0),
            Product(name='Масло сливочное', unit='кг', quantity=5.0),
            Product(name='Молоко', unit='л', quantity=20.0),
            Product(name='Сливки', unit='л', quantity=5.0),
            Product(name='Сыр', unit='кг', quantity=7.0),
            Product(name='Яйца', unit='шт', quantity=100.0),
            Product(name='Картофель', unit='кг', quantity=30.0),
            Product(name='Морковь', unit='кг', quantity=15.0),
            Product(name='Лук', unit='кг', quantity=10.0),
            Product(name='Помидоры', unit='кг', quantity=12.0),
            Product(name='Огурцы', unit='кг', quantity=10.0),
            Product(name='Кофе', unit='кг', quantity=5.0),
            Product(name='Чай', unit='кг', quantity=3.0)
        ]
        
        for product in products:
            db.session.add(product)
        
        db.session.flush()  # Получаем ID продуктов
        
        # Добавляем рецепты
        print("Добавление рецептов...")
        
        # Словарь с рецептами для каждого блюда
        recipes = {
            'Стейк из говядины': [
                {'name': 'Говядина', 'quantity': 0.3},
                {'name': 'Соль', 'quantity': 0.01},
                {'name': 'Перец', 'quantity': 0.005},
                {'name': 'Масло растительное', 'quantity': 0.02},
                {'name': 'Масло сливочное', 'quantity': 0.02}
            ],
            'Паста Карбонара': [
                {'name': 'Мука', 'quantity': 0.1},
                {'name': 'Яйца', 'quantity': 2},
                {'name': 'Свинина', 'quantity': 0.1},
                {'name': 'Сыр', 'quantity': 0.05},
                {'name': 'Сливки', 'quantity': 0.1},
                {'name': 'Соль', 'quantity': 0.005},
                {'name': 'Перец', 'quantity': 0.002}
            ],
            'Борщ': [
                {'name': 'Говядина', 'quantity': 0.2},
                {'name': 'Картофель', 'quantity': 0.3},
                {'name': 'Морковь', 'quantity': 0.1},
                {'name': 'Лук', 'quantity': 0.1},
                {'name': 'Соль', 'quantity': 0.01},
                {'name': 'Перец', 'quantity': 0.005}
            ],
            'Грибной суп': [
                {'name': 'Картофель', 'quantity': 0.2},
                {'name': 'Морковь', 'quantity': 0.1},
                {'name': 'Лук', 'quantity': 0.1},
                {'name': 'Сливки', 'quantity': 0.1},
                {'name': 'Соль', 'quantity': 0.01},
                {'name': 'Перец', 'quantity': 0.005}
            ],
            'Цезарь с курицей': [
                {'name': 'Курица', 'quantity': 0.15},
                {'name': 'Сыр', 'quantity': 0.05},
                {'name': 'Яйца', 'quantity': 1},
                {'name': 'Масло растительное', 'quantity': 0.03},
                {'name': 'Соль', 'quantity': 0.005},
                {'name': 'Перец', 'quantity': 0.002}
            ],
            'Греческий салат': [
                {'name': 'Помидоры', 'quantity': 0.15},
                {'name': 'Огурцы', 'quantity': 0.15},
                {'name': 'Сыр', 'quantity': 0.05},
                {'name': 'Масло растительное', 'quantity': 0.03},
                {'name': 'Соль', 'quantity': 0.005},
                {'name': 'Перец', 'quantity': 0.002}
            ],
            'Тирамису': [
                {'name': 'Яйца', 'quantity': 2},
                {'name': 'Сахар', 'quantity': 0.1},
                {'name': 'Сливки', 'quantity': 0.2},
                {'name': 'Кофе', 'quantity': 0.05}
            ],
            'Чизкейк': [
                {'name': 'Яйца', 'quantity': 2},
                {'name': 'Сахар', 'quantity': 0.15},
                {'name': 'Сливки', 'quantity': 0.2},
                {'name': 'Сыр', 'quantity': 0.2}
            ],
            'Капучино': [
                {'name': 'Кофе', 'quantity': 0.02},
                {'name': 'Молоко', 'quantity': 0.15},
                {'name': 'Сахар', 'quantity': 0.01}
            ],
            'Чай зеленый': [
                {'name': 'Чай', 'quantity': 0.01},
                {'name': 'Сахар', 'quantity': 0.01}
            ]
        }
        
        # Создаем словарь продуктов для быстрого доступа
        product_dict = {product.name: product for product in products}
        
        # Добавляем рецепты для каждого блюда
        for menu_item in menu_items:
            # Проверяем, есть ли рецепт для данного блюда
            if menu_item.name in recipes:
                recipe_ingredients = recipes[menu_item.name]
                
                for ingredient in recipe_ingredients:
                    product_name = ingredient['name']
                    quantity = ingredient['quantity']
                    
                    # Проверяем, есть ли такой продукт
                    if product_name in product_dict:
                        product = product_dict[product_name]
                        
                        # Создаем запись рецепта
                        recipe_item = RecipeItem(
                            menu_item_id=menu_item.id,
                            product_id=product.id,
                            quantity=quantity
                        )
                        
                        db.session.add(recipe_item)
        
        # Добавляем смены
        print("Добавление смен...")
        shifts = [
            Shift(
                shift_date=datetime.now().date() - timedelta(days=1),
                start_time='09:00',
                end_time='18:00',
                employees=f"{employees[1].id},{employees[3].id}",  # waiter1, cook1
                status='завершена'
            ),
            Shift(
                shift_date=datetime.now().date(),
                start_time='09:00',
                end_time='18:00',
                employees=f"{employees[2].id},{employees[4].id}",  # waiter2, cook2
                status='активна'
            ),
            Shift(
                shift_date=datetime.now().date() + timedelta(days=1),
                start_time='09:00',
                end_time='18:00',
                employees=f"{employees[1].id},{employees[3].id}",  # waiter1, cook1
                status='запланирована'
            )
        ]
        
        for shift in shifts:
            db.session.add(shift)
        
        db.session.flush()  # Получаем ID смен
        
        # Добавляем заказы
        print("Добавление заказов...")
        orders = [
            Order(
                order_date=datetime.now() - timedelta(hours=2),
                table_number=1,
                customers_count=2,
                items='Капучино x2, Чизкейк x2',
                total_price=1060.0,
                status='оплачен',
                waiter_id=users[1].id,  # waiter1
                shift_id=shifts[0].id  # вчерашняя смена
            ),
            Order(
                order_date=datetime.now() - timedelta(minutes=30),
                table_number=3,
                customers_count=4,
                items='Борщ x2, Стейк из говядины x2, Капучино x4',
                total_price=2320.0,
                status='готов',
                waiter_id=users[2].id,  # waiter2
                shift_id=shifts[1].id  # сегодняшняя смена
            ),
            Order(
                order_date=datetime.now() - timedelta(minutes=15),
                table_number=2,
                customers_count=1,
                items='Паста Карбонара x1, Чай зеленый x1',
                total_price=600.0,
                status='готовится',
                waiter_id=users[2].id,  # waiter2
                shift_id=shifts[1].id  # сегодняшняя смена
            ),
            Order(
                order_date=datetime.now() - timedelta(minutes=5),
                table_number=4,
                customers_count=3,
                items='Цезарь с курицей x2, Борщ x3',
                total_price=1890.0,
                status='принят',
                waiter_id=users[2].id,  # waiter2
                shift_id=shifts[1].id  # сегодняшняя смена
            )
        ]
        
        for order in orders:
            db.session.add(order)
        
        # Сохраняем изменения
        db.session.commit()
        
        print("База данных успешно инициализирована с тестовыми данными.")
        print("Учетные данные для входа:")
        print("- Администратор: admin / admin")
        print("- Официант 1: waiter1 / waiter1")
        print("- Официант 2: waiter2 / waiter2")
        print("- Повар 1: cook1 / cook1")
        print("- Повар 2: cook2 / cook2")

if __name__ == "__main__":
    init_database() 