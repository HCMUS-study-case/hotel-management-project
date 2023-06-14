from datetime import datetime
from hotelManagement import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    citizen_id = db.Column(db.String(100), unique=True, nullable=False)
    place_issued = db.Column(db.String(50), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    home_town = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(2), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    def __repr__(self):
        return f"User('{self.name}', '{self.birthdate}', '{self.gender}', '{self.phone_number}', '{self.role}', '{self.username}', '{self.password}')"


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    note = db.Column(db.String(1000), nullable=False)
    def __repr__(self):
        return f"Room('{self.name}', '{self.type}', '{self.price}', '{self.status}', '{self.note}')"


class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(100), db.ForeignKey('room.name'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_type = db.Column(db.String(100), nullable=False)
    customer_id = db.Column(db.String(100), nullable=False)
    customer_address = db.Column(db.String(200), nullable=False)
    num_customers = db.Column(db.Integer, nullable=False, default=0)
    start_date = db.Column(db.Date, nullable=False)
    payment_date = db.Column(db.Date)
    total_amount = db.Column(db.Float)
    unit_price = db.Column(db.Float)
    number_of_days = db.Column(db.Integer)
    amount = db.Column(db.Float)
    paid = db.Column(db.String(100))