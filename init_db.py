from app import app, db
from add_products import add_products
from add_menu_items import add_menu_items
from add_recipes import add_recipes

def init_database():
    with app.app_context():
        # Создаем таблицы, если их нет
        db.create_all()
        print("Таблицы базы данных созданы.")
        
        # Добавляем продукты
        add_products()
        
        # Добавляем блюда
        add_menu_items()
        
        # Добавляем рецепты
        add_recipes()
        
        print("Инициализация базы данных завершена.")

if __name__ == "__main__":
    init_database() 