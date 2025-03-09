from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cafe_management_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модели данных
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin, waiter, cook
    status = db.Column(db.String(20), default='активен')  # активен, уволен

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    hire_date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(20), default='активен')  # активен, уволен
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('employee', uselist=False))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    table_number = db.Column(db.Integer, nullable=False)
    customers_count = db.Column(db.Integer, default=1)
    items = db.Column(db.Text)
    total_price = db.Column(db.Float)
    status = db.Column(db.String(20), default='принят')  # принят, готовится, готов, оплачен, отменен
    waiter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    waiter = db.relationship('User', backref='orders')
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'))
    shift = db.relationship('Shift', backref='orders')

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # еда, напиток
    is_available = db.Column(db.Boolean, default=True)
    # Связь с рецептами
    recipe_items = db.relationship('RecipeItem', backref='menu_item', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # кг, л, шт и т.д.
    quantity = db.Column(db.Float, default=0)
    # Связь с рецептами
    recipe_items = db.relationship('RecipeItem', backref='product', lazy=True)

class RecipeItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # Количество продукта для блюда

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)
    order = db.relationship('Order', backref='order_items')
    menu_item = db.relationship('MenuItem')

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shift_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    employees = db.Column(db.Text)  # Список ID сотрудников через запятую
    status = db.Column(db.String(20), default='запланирована')  # запланирована, активна, завершена

# Декораторы для проверки ролей
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin' or user.status != 'активен':
            flash('У вас нет доступа к этой странице', 'danger')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def waiter_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'waiter' or user.status != 'активен':
            flash('У вас нет доступа к этой странице', 'danger')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def cook_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'cook' or user.status != 'активен':
            flash('У вас нет доступа к этой странице', 'danger')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def any_role_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or user.status != 'активен':
            flash('У вас нет доступа к этой странице', 'danger')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

# Создание базы данных и таблиц
# Функция для создания таблиц и добавления администратора
def create_tables():
    with app.app_context():
        db.create_all()
        # Создаем администратора, если его нет
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin'),
                role='admin',
                status='активен'
            )
            db.session.add(admin)
            
            # Добавляем тестовые данные для меню
            if not MenuItem.query.first():
                menu_items = [
                    MenuItem(name='Капучино', description='Кофейный напиток с молоком', price=150.0, category='напиток'),
                    MenuItem(name='Латте', description='Кофе с молоком', price=170.0, category='напиток'),
                    MenuItem(name='Эспрессо', description='Крепкий кофе', price=120.0, category='напиток'),
                    MenuItem(name='Американо', description='Эспрессо с добавлением воды', price=130.0, category='напиток'),
                    MenuItem(name='Чай', description='Черный/зеленый чай', price=100.0, category='напиток'),
                    MenuItem(name='Круассан', description='Слоеный круассан с маслом', price=120.0, category='еда'),
                    MenuItem(name='Сэндвич', description='Сэндвич с курицей и овощами', price=250.0, category='еда'),
                    MenuItem(name='Салат Цезарь', description='Салат с курицей, сыром и соусом', price=350.0, category='еда'),
                    MenuItem(name='Паста Карбонара', description='Паста с беконом и сливочным соусом', price=400.0, category='еда'),
                    MenuItem(name='Чизкейк', description='Классический чизкейк', price=200.0, category='еда')
                ]
                for item in menu_items:
                    db.session.add(item)
            
            db.session.commit()

# Функция для получения информации о сотруднике по ID
@app.template_filter('get_employee')
def get_employee(employee_id):
    return Employee.query.get(employee_id)

# Функция для получения информации о пользователе по ID
@app.template_filter('get_user')
def get_user(user_id):
    return User.query.get(user_id)

# Функция для расчета доступного количества блюд
def calculate_available_portions(menu_item_id):
    menu_item = MenuItem.query.get(menu_item_id)
    if not menu_item or not menu_item.recipe_items:
        return 'inf'  # Если нет рецепта, считаем, что блюдо доступно в неограниченном количестве
    
    available_portions = float('inf')
    for recipe_item in menu_item.recipe_items:
        if recipe_item.quantity <= 0:
            continue
        
        product = recipe_item.product
        if product.quantity <= 0:
            return 0  # Если какого-то продукта нет, блюдо недоступно
        
        # Сколько порций можно приготовить из имеющегося количества этого продукта
        portions = product.quantity / recipe_item.quantity
        available_portions = min(available_portions, int(portions))
    
    return available_portions

# Функция для получения текущей даты в шаблонах
@app.context_processor
def utility_processor():
    def now():
        return datetime.now()
    
    def get_user(user_id):
        return User.query.get(user_id)
    
    def get_employee(employee_id):
        return Employee.query.get(employee_id)
    
    def get_available_portions(menu_item_id):
        return calculate_available_portions(menu_item_id)
    
    return dict(now=now, get_user=get_user, get_employee=get_employee, get_available_portions=get_available_portions)

# Маршруты
@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.status == 'активен':
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'waiter':
                return redirect(url_for('waiter_dashboard'))
            elif user.role == 'cook':
                return redirect(url_for('cook_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password) and user.status == 'активен':
            session['user_id'] = user.id
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'waiter':
                return redirect(url_for('waiter_dashboard'))
            elif user.role == 'cook':
                return redirect(url_for('cook_dashboard'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Административные маршруты
@app.route('/admin')
@admin_required
def admin_dashboard():
    # Статистика для дашборда
    employees_count = Employee.query.filter_by(status='активен').count()
    orders_today = Order.query.filter(
        Order.order_date >= datetime.today().replace(hour=0, minute=0, second=0)
    ).count()
    active_shifts = Shift.query.filter_by(status='активна').count()
    
    return render_template('admin/dashboard.html', 
                          employees_count=employees_count,
                          orders_today=orders_today,
                          active_shifts=active_shifts)

# Маршруты для управления пользователями
@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Проверка на существование пользователя
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует', 'danger')
            return redirect(url_for('add_user'))
        
        # Создание нового пользователя
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role=role,
            status='активен'
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Пользователь успешно добавлен', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/add_user.html')

@app.route('/admin/users/fire/<int:id>')
@admin_required
def fire_user(id):
    user = User.query.get_or_404(id)
    user.status = 'уволен'
    
    # Если у пользователя есть связанный сотрудник, также меняем его статус
    employee = Employee.query.filter_by(user_id=user.id).first()
    if employee:
        employee.status = 'уволен'
    
    db.session.commit()
    
    flash('Статус пользователя изменен на "уволен"', 'success')
    return redirect(url_for('admin_users'))

# Маршруты для управления сотрудниками
@app.route('/admin/employees')
@admin_required
def admin_employees():
    employees = Employee.query.all()
    return render_template('admin/employees.html', employees=employees)

@app.route('/admin/employees/add', methods=['GET', 'POST'])
@admin_required
def add_employee():
    if request.method == 'POST':
        name = request.form.get('name')
        position = request.form.get('position')
        phone = request.form.get('phone')
        email = request.form.get('email')
        hire_date_str = request.form.get('hire_date')
        user_id = request.form.get('user_id')
        
        try:
            hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
        except ValueError:
            hire_date = datetime.utcnow().date()
        
        employee = Employee(
            name=name,
            position=position,
            phone=phone,
            email=email,
            hire_date=hire_date,
            status='активен',
            user_id=user_id if user_id else None
        )
        
        db.session.add(employee)
        db.session.commit()
        
        flash('Сотрудник успешно добавлен', 'success')
        return redirect(url_for('admin_employees'))
    
    # Получаем список пользователей без связанных сотрудников
    available_users = User.query.filter(
        ~User.id.in_(db.session.query(Employee.user_id).filter(Employee.user_id != None))
    ).all()
    
    return render_template('admin/add_employee.html', available_users=available_users)

@app.route('/admin/employees/fire/<int:id>')
@admin_required
def fire_employee(id):
    employee = Employee.query.get_or_404(id)
    employee.status = 'уволен'
    
    # Если у сотрудника есть связанный пользователь, также меняем его статус
    if employee.user_id:
        user = User.query.get(employee.user_id)
        if user:
            user.status = 'уволен'
    
    db.session.commit()
    
    flash('Статус сотрудника изменен на "уволен"', 'success')
    return redirect(url_for('admin_employees'))

# Маршруты для управления заказами
@app.route('/admin/orders')
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/orders/update_status/<int:id>', methods=['POST'])
@admin_required
def admin_update_order_status(id):
    order = Order.query.get_or_404(id)
    status = request.form.get('status')
    
    if status in ['принят', 'готовится', 'готов', 'оплачен', 'отменен']:
        order.status = status
        db.session.commit()
        flash(f'Статус заказа изменен на "{status}"', 'success')
    else:
        flash('Недопустимый статус заказа', 'danger')
    
    return redirect(url_for('admin_orders'))

# Маршруты для управления сменами
@app.route('/admin/shifts')
@admin_required
def admin_shifts():
    shifts = Shift.query.order_by(Shift.shift_date.desc()).all()
    return render_template('admin/shifts.html', shifts=shifts)

@app.route('/admin/shifts/add', methods=['GET', 'POST'])
@admin_required
def add_shift():
    if request.method == 'POST':
        shift_date_str = request.form.get('shift_date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        employees_ids = request.form.getlist('employees')
        status = request.form.get('status')
        
        try:
            shift_date = datetime.strptime(shift_date_str, '%Y-%m-%d').date()
        except ValueError:
            shift_date = datetime.utcnow().date()
        
        shift = Shift(
            shift_date=shift_date,
            start_time=start_time,
            end_time=end_time,
            employees=','.join(employees_ids),
            status=status
        )
        
        db.session.add(shift)
        db.session.commit()
        
        flash('Смена успешно создана', 'success')
        return redirect(url_for('admin_shifts'))
    
    employees = Employee.query.filter_by(status='активен').all()
    return render_template('admin/add_shift.html', employees=employees)

@app.route('/admin/shifts/update_status/<int:id>', methods=['POST'])
@admin_required
def update_shift_status(id):
    shift = Shift.query.get_or_404(id)
    status = request.form.get('status')
    
    if status in ['запланирована', 'активна', 'завершена']:
        shift.status = status
        db.session.commit()
        flash(f'Статус смены изменен на "{status}"', 'success')
    else:
        flash('Недопустимый статус смены', 'danger')
    
    return redirect(url_for('admin_shifts'))

# Маршруты для управления продуктами
@app.route('/admin/products')
@admin_required
def admin_products():
    products = Product.query.order_by(Product.name).all()
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        unit = request.form.get('unit')
        quantity = request.form.get('quantity', type=float, default=0)
        
        if not name or not unit:
            flash('Необходимо указать название и единицу измерения', 'danger')
            return redirect(url_for('add_product'))
        
        product = Product(name=name, unit=unit, quantity=quantity)
        db.session.add(product)
        db.session.commit()
        
        flash('Продукт успешно добавлен', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/add_product.html')

@app.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        unit = request.form.get('unit')
        quantity = request.form.get('quantity', type=float)
        
        if not name or not unit or quantity is None:
            flash('Все поля обязательны для заполнения', 'danger')
            return redirect(url_for('edit_product', id=id))
        
        product.name = name
        product.unit = unit
        product.quantity = quantity
        db.session.commit()
        
        flash('Продукт успешно обновлен', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/edit_product.html', product=product)

@app.route('/admin/products/delete/<int:id>')
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    
    # Проверяем, используется ли продукт в рецептах
    if product.recipe_items:
        flash('Невозможно удалить продукт, так как он используется в рецептах', 'danger')
        return redirect(url_for('admin_products'))
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Продукт успешно удален', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/recipes')
@admin_required
def admin_recipes():
    menu_items = MenuItem.query.order_by(MenuItem.name).all()
    return render_template('admin/recipes.html', menu_items=menu_items)

@app.route('/admin/recipes/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_recipe(id):
    menu_item = MenuItem.query.get_or_404(id)
    products = Product.query.order_by(Product.name).all()
    
    if request.method == 'POST':
        # Удаляем существующие записи рецепта
        RecipeItem.query.filter_by(menu_item_id=id).delete()
        
        # Получаем данные из формы
        product_ids = request.form.getlist('product_id')
        quantities = request.form.getlist('quantity')
        
        # Создаем новые записи рецепта
        for i in range(len(product_ids)):
            if i < len(quantities) and product_ids[i] and quantities[i]:
                product_id = int(product_ids[i])
                quantity = float(quantities[i])
                
                recipe_item = RecipeItem(
                    menu_item_id=id,
                    product_id=product_id,
                    quantity=quantity
                )
                db.session.add(recipe_item)
        
        db.session.commit()
        flash('Рецепт успешно обновлен', 'success')
        return redirect(url_for('admin_recipes'))
    
    # Получаем текущие ингредиенты рецепта
    recipe_items = RecipeItem.query.filter_by(menu_item_id=id).all()
    
    return render_template('admin/edit_recipe.html', menu_item=menu_item, products=products, recipe_items=recipe_items)

# Маршруты для официанта
@app.route('/waiter')
@waiter_required
def waiter_dashboard():
    # Получаем активную смену
    active_shifts = Shift.query.filter_by(status='активна').all()
    current_user_id = session.get('user_id')
    
    user_in_active_shift = False
    active_shift = None
    
    for shift in active_shifts:
        employee_ids = shift.employees.split(',') if shift.employees else []
        for emp_id in employee_ids:
            employee = Employee.query.get(emp_id)
            if employee and employee.user_id == current_user_id:
                user_in_active_shift = True
                active_shift = shift
                break
        if user_in_active_shift:
            break
    
    # Получаем заказы текущей смены
    if active_shift:
        orders = Order.query.filter_by(shift_id=active_shift.id, waiter_id=current_user_id).all()
    else:
        orders = []
    
    return render_template('waiter/dashboard.html', 
                          active_shift=active_shift,
                          user_in_active_shift=user_in_active_shift,
                          orders=orders)

@app.route('/waiter/orders')
@waiter_required
def waiter_orders():
    current_user_id = session.get('user_id')
    
    # Получаем активную смену
    active_shifts = Shift.query.filter_by(status='активна').all()
    user_in_active_shift = False
    active_shift = None
    
    for shift in active_shifts:
        employee_ids = shift.employees.split(',') if shift.employees else []
        for emp_id in employee_ids:
            employee = Employee.query.get(emp_id)
            if employee and employee.user_id == current_user_id:
                user_in_active_shift = True
                active_shift = shift
                break
        if user_in_active_shift:
            break
    
    # Получаем заказы текущей смены
    if active_shift:
        orders = Order.query.filter_by(shift_id=active_shift.id).all()
    else:
        orders = []
    
    return render_template('waiter/orders.html', 
                          active_shift=active_shift,
                          user_in_active_shift=user_in_active_shift,
                          orders=orders)

@app.route('/waiter/orders/add', methods=['GET', 'POST'])
@waiter_required
def add_order():
    # Проверяем, назначен ли официант на активную смену
    user_id = session.get('user_id')
    active_shift = None
    user_in_active_shift = False
    
    # Получаем активную смену
    shifts = Shift.query.filter_by(status='активна').all()
    for shift in shifts:
        if shift.employees:
            employee_ids = shift.employees.split(',')
            for employee_id in employee_ids:
                employee = Employee.query.get(employee_id)
                if employee and employee.user_id == user_id:
                    active_shift = shift
                    user_in_active_shift = True
                    break
        if user_in_active_shift:
            break
    
    if not user_in_active_shift:
        flash('Вы не назначены на активную смену. Обратитесь к администратору.', 'warning')
        return redirect(url_for('waiter_dashboard'))
    
    if request.method == 'POST':
        table_number = request.form.get('table_number', type=int)
        customers_count = request.form.get('customers_count', type=int, default=1)
        
        if not table_number:
            flash('Необходимо указать номер столика', 'danger')
            return redirect(url_for('add_order'))
        
        # Получаем выбранные позиции меню
        menu_item_ids = request.form.getlist('menu_item_id')
        quantities = request.form.getlist('quantity')
        
        if not menu_item_ids or not quantities:
            flash('Необходимо выбрать хотя бы одну позицию меню', 'danger')
            return redirect(url_for('add_order'))
        
        # Проверяем доступность продуктов
        for i in range(len(menu_item_ids)):
            if i < len(quantities) and menu_item_ids[i] and quantities[i]:
                menu_item_id = int(menu_item_ids[i])
                quantity = int(quantities[i])
                
                available = calculate_available_portions(menu_item_id)
                if quantity > available:
                    menu_item = MenuItem.query.get(menu_item_id)
                    flash(f'Недостаточно продуктов для приготовления "{menu_item.name}". Доступно: {available}', 'danger')
                    return redirect(url_for('add_order'))
        
        # Создаем заказ
        order = Order(
            table_number=table_number,
            customers_count=customers_count,
            waiter_id=user_id,
            shift_id=active_shift.id,
            status='принят'
        )
        
        db.session.add(order)
        db.session.commit()
        
        # Добавляем позиции заказа
        total_price = 0
        order_items_text = []
        
        for i in range(len(menu_item_ids)):
            if i < len(quantities) and menu_item_ids[i] and quantities[i]:
                menu_item_id = int(menu_item_ids[i])
                quantity = int(quantities[i])
                
                menu_item = MenuItem.query.get(menu_item_id)
                if menu_item:
                    # Создаем позицию заказа
                    order_item = OrderItem(
                        order_id=order.id,
                        menu_item_id=menu_item_id,
                        quantity=quantity,
                        price=menu_item.price
                    )
                    db.session.add(order_item)
                    
                    # Обновляем общую сумму
                    item_total = menu_item.price * quantity
                    total_price += item_total
                    
                    # Добавляем текстовое описание позиции
                    order_items_text.append(f"{menu_item.name} x{quantity}")
                    
                    # Уменьшаем количество доступных продуктов
                    for recipe_item in menu_item.recipe_items:
                        product = recipe_item.product
                        product.quantity -= recipe_item.quantity * quantity
        
        # Обновляем заказ с общей суммой и текстовым описанием позиций
        order.total_price = total_price
        order.items = ', '.join(order_items_text)
        
        db.session.commit()
        
        flash('Заказ успешно создан', 'success')
        return redirect(url_for('waiter_orders'))
    
    # Получаем все доступные позиции меню
    menu_items = MenuItem.query.filter_by(is_available=True).order_by(MenuItem.category, MenuItem.name).all()
    
    return render_template('waiter/add_order.html', 
                          menu_items=menu_items, 
                          active_shift=active_shift)

@app.route('/waiter/orders/update_status/<int:id>/<string:status>')
@waiter_required
def waiter_update_order_status(id, status):
    order = Order.query.get_or_404(id)
    
    # Проверяем, что заказ принадлежит текущему официанту
    if order.waiter_id != session.get('user_id'):
        flash('У вас нет прав для изменения этого заказа', 'danger')
        return redirect(url_for('waiter_orders'))
    
    # Проверяем допустимость статуса для официанта
    if status not in ['принят', 'оплачен']:
        flash('Недопустимый статус заказа', 'danger')
        return redirect(url_for('waiter_orders'))
    
    order.status = status
    db.session.commit()
    
    flash(f'Статус заказа изменен на "{status}"', 'success')
    return redirect(url_for('waiter_orders'))

# Маршруты для повара
@app.route('/cook')
@cook_required
def cook_dashboard():
    # Получаем активную смену
    active_shifts = Shift.query.filter_by(status='активна').all()
    current_user_id = session.get('user_id')
    
    user_in_active_shift = False
    active_shift = None
    
    for shift in active_shifts:
        employee_ids = shift.employees.split(',') if shift.employees else []
        for emp_id in employee_ids:
            employee = Employee.query.get(emp_id)
            if employee and employee.user_id == current_user_id:
                user_in_active_shift = True
                active_shift = shift
                break
        if user_in_active_shift:
            break
    
    # Получаем заказы со статусом "принят" или "готовится"
    if active_shift:
        orders = Order.query.filter(
            Order.shift_id == active_shift.id,
            Order.status.in_(['принят', 'готовится'])
        ).all()
    else:
        orders = []
    
    return render_template('cook/dashboard.html', 
                          active_shift=active_shift,
                          user_in_active_shift=user_in_active_shift,
                          orders=orders)

@app.route('/cook/orders')
@cook_required
def cook_orders():
    # Получаем активную смену
    active_shifts = Shift.query.filter_by(status='активна').all()
    current_user_id = session.get('user_id')
    
    user_in_active_shift = False
    active_shift = None
    
    for shift in active_shifts:
        employee_ids = shift.employees.split(',') if shift.employees else []
        for emp_id in employee_ids:
            employee = Employee.query.get(emp_id)
            if employee and employee.user_id == current_user_id:
                user_in_active_shift = True
                active_shift = shift
                break
        if user_in_active_shift:
            break
    
    # Получаем все заказы текущей смены
    if active_shift:
        orders = Order.query.filter_by(shift_id=active_shift.id).all()
    else:
        orders = []
    
    return render_template('cook/orders.html', 
                          active_shift=active_shift,
                          user_in_active_shift=user_in_active_shift,
                          orders=orders)

@app.route('/cook/orders/update_status/<int:id>/<string:status>')
@cook_required
def cook_update_order_status(id, status):
    order = Order.query.get_or_404(id)
    
    # Проверяем допустимость статуса для повара
    if status not in ['готовится', 'готов']:
        flash('Недопустимый статус заказа', 'danger')
        return redirect(url_for('cook_orders'))
    
    order.status = status
    db.session.commit()
    
    flash(f'Статус заказа изменен на "{status}"', 'success')
    return redirect(url_for('cook_orders'))

if __name__ == '__main__':
    # Создаем таблицы при запуске приложения
    create_tables()
    app.run(debug=True)