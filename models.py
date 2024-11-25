from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    activity_level = db.Column(db.String(20), nullable=False)
    tdee = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<UserData {self.id}>"