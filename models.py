from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    # 必須實現的 Flask-Login 屬性和方法
    @property
    def is_authenticated(self):
        return True  # 如果用戶已驗證，返回 True

    @property
    def is_active(self):
        return True  # 如果用戶活躍，返回 True。如果需要停用某些用戶，可以改為動態邏輯。

    @property
    def is_anonymous(self):
        return False  # Flask-Login 將匿名用戶認定為 False

    def get_id(self):
        return str(self.id)  # 返回用戶的唯一標識符，用於登入狀態跟踪


class Canteen(db.Model):
    __tablename__ = 'canteens'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)  # 新增商家介紹欄位
    menus = db.relationship('Menu', backref='canteen', lazy=True)

class Menu(db.Model):
    __tablename__ = 'menus'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    nutrition_calories = db.Column(db.Float, nullable=False)  # 總熱量 (大卡)
    nutrition_protein = db.Column(db.Float, nullable=False)   # 蛋白質 (g)
    nutrition_fat = db.Column(db.Float, nullable=False)       # 脂肪 (g)
    nutrition_carbs = db.Column(db.Float, nullable=False)     # 醣類 (g)
    canteen_id = db.Column(db.Integer, db.ForeignKey('canteens.id'), nullable=False)

class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 與 User 表的外鍵關係
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    activity_level = db.Column(db.String(20), nullable=False)
    tdee = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)

    user = db.relationship('User', backref=db.backref('user_data', lazy=True))

    def __repr__(self):
        return f"<UserData {self.id}>"

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    calories = db.Column(db.Float, nullable=False, default=0.0)
    protein = db.Column(db.Float, nullable=False, default=0.0)
    fat = db.Column(db.Float, nullable=False, default=0.0)
    carbs = db.Column(db.Float, nullable=False, default=0.0)

    # Relationship to Menu
    menu = db.relationship('Menu', backref='orders', lazy='joined')  # 确保立即加载




