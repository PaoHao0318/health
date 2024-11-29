import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Canteen, Menu, UserData, User, Order  # 確保 models 模組存在
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///canteens.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'key'  # 用於安全性相關功能（例如 session）

db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

# 創建資料表，將創建資料表的邏輯放入 if __name__ 區塊
def create_tables():
    with app.app_context():
        db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 註冊路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 檢查使用者名稱是否已存在
        if User.query.filter_by(username=username).first():
            flash('使用者名稱已被註冊', 'danger')
            return redirect(url_for('register'))

        # 創建新使用者
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('註冊成功！請登入。', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')
#hihi
# 登入路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('登入成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('登入失敗，請檢查使用者名稱或密碼。', 'danger')

    return render_template('login.html')

# 登出路由
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已成功登出', 'success')
    return redirect(url_for('login'))

# 商家列表頁面
@app.route('/')
def index():
    canteens = Canteen.query.all()

    if current_user.is_authenticated:  # 檢查是否已登入
        user_data = UserData.query.filter_by(user_id=current_user.id).first()
        
        # 計算已點餐的營養總量
        orders = Order.query.filter_by(user_id=current_user.id).all()
        total_nutrition = {
            'calories': sum(order.calories for order in orders),
            'protein': sum(order.protein for order in orders),
            'fat': sum(order.fat for order in orders),
            'carbs': sum(order.carbs for order in orders),
        }

        # 剩餘營養需求
        remaining_nutrition = {}
        if user_data:
            remaining_nutrition = {
                'calories': max(user_data.tdee - total_nutrition['calories'], 0),
                'protein': max(user_data.protein - total_nutrition['protein'], 0),
                'fat': max(user_data.fat - total_nutrition['fat'], 0),
                'carbs': max(user_data.carbs - total_nutrition['carbs'], 0),
            }
    else:
        user_data = None
        orders = []
        total_nutrition = None
        remaining_nutrition = None

    return render_template(
        'index.html',
        canteens=canteens,
        user_data=user_data,
        total_nutrition=total_nutrition,
        remaining_nutrition=remaining_nutrition,
        orders=orders
    )

# 顯示單一店家及其菜單，並提供編輯菜單的功能
@app.route('/canteen/<int:canteen_id>', methods=['GET', 'POST'])
def view_or_edit_canteen(canteen_id):
    canteen = Canteen.query.get(canteen_id)
    if canteen is None:
        return "Canteen not found", 404

    # 點餐邏輯
    if request.method == 'POST' and 'order_menu_id' in request.form:
        menu_id = int(request.form['order_menu_id'])
        quantity = int(request.form.get('quantity', 1))
        menu = Menu.query.get(menu_id)

        if menu and quantity > 0:
            # 計算該餐品的營養
            total_calories = menu.nutrition_calories * quantity
            total_protein = menu.nutrition_protein * quantity
            total_fat = menu.nutrition_fat * quantity
            total_carbs = menu.nutrition_carbs * quantity

            # 創建點餐記錄
            new_order = Order(
                user_id=current_user.id,
                menu_id=menu_id,
                quantity=quantity,
                calories=total_calories,
                protein=total_protein,
                fat=total_fat,
                carbs=total_carbs,
            )
            db.session.add(new_order)
            db.session.commit()

            flash(f'成功點選 {menu.name} ({quantity} 份)', 'success')
        else:
            flash('點餐失敗，請檢查輸入', 'danger')

    # 查詢菜單和用戶已點的餐品
    menus = Menu.query.filter_by(canteen_id=canteen.id).all()
    orders = Order.query.filter_by(user_id=current_user.id).all()

    # 計算已點營養總和
    total_calories = sum(order.calories for order in orders)
    total_protein = sum(order.protein for order in orders)
    total_fat = sum(order.fat for order in orders)
    total_carbs = sum(order.carbs for order in orders)

    # 剩餘營養
    user_data = UserData.query.filter_by(user_id=current_user.id).first()
    if user_data:
        remaining_calories = max(0, user_data.tdee - total_calories)
        remaining_protein = max(0, user_data.protein - total_protein)
        remaining_fat = max(0, user_data.fat - total_fat)
        remaining_carbs = max(0, user_data.carbs - total_carbs)
    else:
        remaining_calories = remaining_protein = remaining_fat = remaining_carbs = None

    return render_template(
        'view_canteen.html',
        canteen=canteen,
        menus=menus,
        orders=orders,
        total_calories=total_calories,
        total_protein=total_protein,
        total_fat=total_fat,
        total_carbs=total_carbs,
        remaining_calories=remaining_calories,
        remaining_protein=remaining_protein,
        remaining_fat=remaining_fat,
        remaining_carbs=remaining_carbs,
    )

@app.route('/add_canteen', methods=['GET', 'POST'])
def add_canteen():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        if not name:
            return "商家名稱是必填的", 400  # 商家名稱不可為空
        if not description:
            return "商家介紹是必填的", 400  # 如果商家介紹也需要必填

        try:
            # 建立新的商家
            new_canteen = Canteen(name=name, description=description)
            db.session.add(new_canteen)
            db.session.commit()
            return redirect(url_for('index'))  # 新增商家後回到首頁
        except Exception as e:
            db.session.rollback()  # 如果有錯誤，回滾事務
            print(f"Error: {e}")
            return "新增商家失敗，請稍後再試"

    return render_template('add_canteen.html')

# 編輯商家資料
@app.route('/edit_canteen/<int:canteen_id>', methods=['GET', 'POST'])
def edit_canteen(canteen_id):
    # 獲取商家資料
    canteen = Canteen.query.get_or_404(canteen_id)

    if request.method == 'POST':
        # 從表單中更新商家資訊
        canteen.name = request.form['name']
        canteen.description = request.form.get('description', '')  # 如果未填，則為空字符串
        
        # 提交更改
        db.session.commit()

        # 重定向回商家詳情頁面
        return redirect(url_for('view_or_edit_canteen', canteen_id=canteen.id))

    # 如果是 GET 請求，渲染編輯頁面
    return render_template('edit_canteen.html', canteen=canteen)

# 新增菜單
@app.route('/canteen/<int:canteen_id>/add_menu', methods=['GET', 'POST'])
def add_menu(canteen_id):
    canteen = Canteen.query.get_or_404(canteen_id)

    if request.method == 'POST':
        menu_name = request.form['menu_name']
        ingredients = request.form['ingredients']
        nutrition_calories = float(request.form['nutrition_calories'])  # 總熱量
        nutrition_protein = float(request.form['nutrition_protein'])    # 蛋白質
        nutrition_fat = float(request.form['nutrition_fat'])            # 脂肪
        nutrition_carbs = float(request.form['nutrition_carbs'])        # 醣類
        
        # 新增菜單品項
        new_menu = Menu(
            name=menu_name, 
            ingredients=ingredients,
            nutrition_calories=nutrition_calories,
            nutrition_protein=nutrition_protein,
            nutrition_fat=nutrition_fat,
            nutrition_carbs=nutrition_carbs,
            canteen_id=canteen.id
        )
        db.session.add(new_menu)
        db.session.commit()
        
        return redirect(url_for('view_or_edit_canteen', canteen_id=canteen.id))
    
    return render_template('add_menu.html', canteen=canteen)

@app.route('/edit_menu/<int:menu_id>', methods=['GET', 'POST'])
def edit_menu(menu_id):
    menu = Menu.query.get_or_404(menu_id)

    if request.method == 'POST':
        # 從表單中獲取數據，並處理空值
        menu.name = request.form.get('name')
        menu.ingredients = request.form.get('ingredients')
        menu.nutrition_calories = float(request.form.get('nutrition_calories', 0))
        menu.nutrition_protein = float(request.form.get('nutrition_protein', 0))
        menu.nutrition_fat = float(request.form.get('nutrition_fat', 0))
        menu.nutrition_carbs = float(request.form.get('nutrition_carbs', 0))

        # 提交到資料庫
        db.session.commit()
        return redirect(url_for('view_or_edit_canteen', canteen_id=menu.canteen_id))

    # 如果是 GET 請求，渲染編輯頁面
    return render_template('edit_menu.html', menu=menu)

# 刪除商家
@app.route('/canteen/delete/<int:canteen_id>', methods=['POST'])
def delete_canteen(canteen_id):
    canteen = Canteen.query.get_or_404(canteen_id)
    db.session.delete(canteen)
    db.session.commit()
    return redirect(url_for('index'))  # 刪除後返回商家列表頁


# 刪除菜單品項
@app.route('/menu/<int:menu_id>/delete', methods=['POST'])
def delete_menu(menu_id):
    menu = Menu.query.get_or_404(menu_id)

    # 刪除菜單品項
    db.session.delete(menu)
    db.session.commit()

    # 返回原商家的菜單頁面
    return redirect(url_for('view_or_edit_canteen', canteen_id=menu.canteen_id))

@app.route('/nutrition_calculator', methods=['GET', 'POST'])
@login_required
def nutrition_calculator():
    if request.method == 'POST':
        # 接收表單數據
        age = int(request.form['age'])
        weight = float(request.form['weight'])  # 公斤
        height = float(request.form['height'])  # 公分
        gender = request.form['gender']
        activity_level = request.form['activity_level']

        # 計算基礎代謝率 (BMR) 和 TDEE
        if gender == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        activity_factors = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        tdee = bmr * activity_factors[activity_level]

        # 營養需求計算
        carbs = round(tdee * 0.5 / 4, 2)
        protein = round(tdee * 0.2 / 4, 2)
        fat = round(tdee * 0.3 / 9, 2)

        # 查找或創建與當前用戶相關聯的 UserData
        user_data = UserData.query.filter_by(user_id=current_user.id).first()
        if user_data is None:
            user_data = UserData(
                user_id=current_user.id,
                age=age, weight=weight, height=height,
                gender=gender, activity_level=activity_level,
                tdee=tdee, carbs=carbs, protein=protein, fat=fat
            )
            db.session.add(user_data)
        else:
            user_data.age = age
            user_data.weight = weight
            user_data.height = height
            user_data.gender = gender
            user_data.activity_level = activity_level
            user_data.tdee = tdee
            user_data.carbs = carbs
            user_data.protein = protein
            user_data.fat = fat

        db.session.commit()

        return render_template('nutrition_result.html', user_data=user_data)

    # 如果是 GET 請求，直接加載計算頁面
    return render_template('nutrition_calculator.html')

@app.route('/place_order/<int:menu_id>', methods=['POST'])
@login_required
def place_order(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    quantity = int(request.form.get('quantity', 1))  # 默認數量為 1

    # 新增訂單記錄
    total_calories = menu.nutrition_calories * quantity
    total_protein = menu.nutrition_protein * quantity
    total_fat = menu.nutrition_fat * quantity
    total_carbs = menu.nutrition_carbs * quantity

    order = Order(
        user_id=current_user.id,
        menu_id=menu.id,
        quantity=quantity,
        calories=total_calories,
        protein=total_protein,
        fat=total_fat,
        carbs=total_carbs
    )
    db.session.add(order)
    db.session.commit()

    flash(f"成功點餐 {menu.name} (數量: {quantity})", 'success')
    return redirect(url_for('view_or_edit_canteen', canteen_id=menu.canteen_id))

@app.route('/delete_order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)

    # 檢查是否屬於目前用戶
    if order.user_id != current_user.id:
        flash("您無權刪除此點餐紀錄", "danger")
        return redirect(url_for('index'))

    # 預先加載 menu.name 避免 DetachedInstanceError
    menu_name = order.menu.name  # 存取 menu 的數據，確保在會話中加載

    # 刪除訂單
    db.session.delete(order)
    db.session.commit()
    flash(f"成功刪除點餐紀錄: {menu_name} x {order.quantity} 份", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    create_tables()  # 手動創建資料表
    app.run(debug=True)  # 啟動 Flask 應用