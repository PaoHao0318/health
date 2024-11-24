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
