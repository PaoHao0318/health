import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, url_for
from models import db, Canteen, Menu  # 確保 models 模組存在
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///canteens.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


# 創建資料表，將創建資料表的邏輯放入 if __name__ 區塊
def create_tables():
    with app.app_context():
        db.create_all()

# 商家列表頁面
@app.route('/')
def index():
    canteens = Canteen.query.all()  # 取得所有商家的資料
    # 確保 description 不為 None，若為 None 則給予空字串
    for canteen in canteens:
        if canteen.description is None:
            canteen.description = ""
    return render_template('index.html', canteens=canteens)


# 顯示單一店家及其菜單，並提供編輯菜單的功能
@app.route('/canteen/<int:canteen_id>', methods=['GET', 'POST'])
def view_or_edit_canteen(canteen_id):
    canteen = Canteen.query.get(canteen_id)
    if canteen is None:
        return "Canteen not found", 404  # 如果商家找不到，返回 404

    if request.method == 'POST':
        menu_name = request.form.get('menu_name')
        if not menu_name:
            return "菜單名稱是必填的", 400  # 錯誤處理：缺少菜單名稱
        
        ingredients = request.form.get('ingredients')
        nutrition_calories = float(request.form.get('nutrition_calories', 0))  # 預設為 0
        nutrition_protein = float(request.form.get('nutrition_protein', 0))
        nutrition_fat = float(request.form.get('nutrition_fat', 0))
        nutrition_carbs = float(request.form.get('nutrition_carbs', 0))
        
        new_menu = Menu(
            name=menu_name, 
            ingredients=ingredients,
            nutrition_calories=nutrition_calories,
            nutrition_protein=nutrition_protein,
            nutrition_fat=nutrition_fat,
            nutrition_carbs=nutrition_carbs,
            canteen_id=canteen.id
        )
        
        # 添加新的菜單到資料庫
        db.session.add(new_menu)
        db.session.commit()
        
        # 診斷：確認菜單是否正確添加
        print(f"菜單 {new_menu.name} 已成功新增！")

        # 使用重定向刷新頁面，並從資料庫中重新獲取最新菜單資料
        return redirect(url_for('view_or_edit_canteen', canteen_id=canteen.id))

    # 確保每次加載頁面時都從資料庫查詢最新的菜單資料
    menus = Menu.query.filter_by(canteen_id=canteen.id).all()

    # 診斷：查看頁面加載的菜單數據
    print(f"加載菜單：{menus}")

    return render_template('view_canteen.html', canteen=canteen, menus=menus)



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


if __name__ == '__main__':
    create_tables()  # 手動創建資料表
    app.run(debug=True)  # 啟動 Flask 應用