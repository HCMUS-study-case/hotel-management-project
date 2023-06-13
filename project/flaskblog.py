from flask import Flask, render_template, url_for, flash, redirect, request, abort
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, PasswordField, SubmitField, BooleanField, RadioField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_wtf.file import FileField, FileAllowed
from datetime import datetime
from dateutil import parser

from PIL import Image
import os
import secrets


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['WTF_CSRF_ENABLED'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

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


class RegistrationForm(FlaskForm):
    name = StringField('Họ và tên', validators=[DataRequired()])
    citizen_id = StringField('Căn cước công dân', validators=[DataRequired()])
    place_issued = StringField('Nơi cấp', validators=[DataRequired()])
    birthdate = DateField('Ngày sinh', format='%Y-%m-%d', validators=[DataRequired()])
    home_town = StringField('Quê quán', validators=[DataRequired()])
    gender = RadioField('Giới tính', choices=[('male', 'Nam'), ('female', 'Nữ')], validators=[DataRequired()])
    address = StringField('Địa chỉ', validators=[DataRequired()])
    phone_number = StringField('SĐT', validators=[DataRequired()])
    role = SelectField('Vai trò', choices=[('AD', 'Admin'), ('HR', 'Nhân sự'), ('RE', 'Lễ tân'), ('AC', 'Kế toán'), ('WA', 'Phục vụ')], 
                        validators=[DataRequired()])
    username = StringField('Tên đăng nhập:', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đăng ký')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập:', validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    remember = BooleanField('Nhớ tài khoản')
    submit = SubmitField('Đăng nhập')

class UpdateAccountForm(FlaskForm):
    name = StringField('Họ và tên', validators=[DataRequired()])
    citizen_id = StringField('Căn cước công dân', validators=[DataRequired()])
    place_issued = StringField('Nơi cấp', validators=[DataRequired()])
    birthdate = DateField('Ngày sinh', format='%Y-%m-%d', validators=[DataRequired()])
    home_town = StringField('Quê quán', validators=[DataRequired()])
    gender = RadioField('Giới tính', choices=[('male', 'Nam'), ('female', 'Nữ')], validators=[DataRequired()])
    address = StringField('Địa chỉ', validators=[DataRequired()])
    phone_number = StringField('SĐT', validators=[DataRequired()])
    role = SelectField('Vai trò', choices=[('AD', 'Admin'), ('HR', 'Nhân sự'), ('RE', 'Lễ tân'), ('AC', 'Kế toán'), ('WA', 'Phục vụ')], 
                        validators=[DataRequired()])
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class RoomForm(FlaskForm):
    name = StringField('Tên phòng', validators=[DataRequired()])
    type = SelectField('Loại phòng', choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], validators=[DataRequired()])
    price = IntegerField("Giá phòng", validators=[DataRequired()])
    status = SelectField('Tình trạng', choices=[('Đầy', 'Đầy'), ('Có người', 'Có người'), ('Trống', 'Trống')], 
                        validators=[DataRequired()], default="Trống")
    note = StringField('Ghi chú')
    submit = SubmitField('Tạo phòng')

class RentalForm(FlaskForm):
    room_name = StringField('Phòng', validators=[DataRequired()])
    customer_name = StringField('Tên khách hàng', validators=[DataRequired()])
    customer_type = SelectField('Loại khách', choices=[('Nội địa', 'Nội địa'), ('Nước ngoài', 'Nước ngoài')], 
                                validators=[DataRequired()])
    customer_id = StringField('CCCD/CMND', validators=[DataRequired()])
    customer_address = StringField('Địa chỉ', validators=[DataRequired()])
    num_customers = IntegerField('Số lượng khách', default=0)
    start_date = DateField('Ngày bắt đầu', format='%Y-%m-%d', validators=[DataRequired()])
    payment_date = DateField('Ngày kết thúc', format='%Y-%m-%d', validators=[DataRequired()])
    unit_price = FloatField('Đơn giá', default=0)
    number_of_days = IntegerField('Số ngày thuê', default=0)
    amount = FloatField('Thành tiền', default=0)
    total_amount = FloatField('Tổng tiền', default=0)
    paid = SelectField('Thanh toán', choices=[('True', 'True'), ('False', 'False')], default="False")
    submit = SubmitField('Tạo phiếu thuê')

with app.app_context():
    db.create_all()


@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/login_admin", methods=['GET', 'POST'])
def create_admin():
    admin = User(name="ADMIN", citizen_id="ADMIN", place_issued="ADMIN", 
            birthdate=datetime.strptime("01/01/2000", "%d/%m/%Y").date(), home_town="ADMIN", gender="ADMIN", 
            address="ADMIN", phone_number="ADMIN", role="ADMIN", 
            username="admin", email="ADMIN@gmail.com", password="admin")
    with app.app_context():
        db.session.add(admin)
        db.session.commit()
    flash('Admin đã được khởi tạo thành công.', 'success')
    return redirect(url_for('login'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, citizen_id=form.citizen_id.data, place_issued=form.place_issued.data, 
                    birthdate=form.birthdate.data, home_town=form.home_town.data, gender=form.gender.data, 
                    address=form.address.data, phone_number=form.phone_number.data, role=form.role.data, 
                    username=form.username.data, email=form.email.data, password=form.password.data)
        with app.app_context():            
            db.session.add(user)
            db.session.commit()
        flash('Đăng ký thành công', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if (user and user.password):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Đăng nhập thất bại. Kiểm tra lại tên đăng nhập và mật khẩu', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.name = form.name.data
        current_user.citizen_id = form.citizen_id.data
        current_user.place_issued = form.place_issued.data
        current_user.birthdate = form.birthdate.data
        current_user.home_town = form.home_town.data
        current_user.gender = form.gender.data
        current_user.address = form.address.data
        current_user.phone_number = form.phone_number.data
        current_user.role = form.role.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.citizen_id.data = current_user.citizen_id
        form.place_issued.data = current_user.place_issued
        form.birthdate.data = current_user.birthdate
        form.home_town.data = current_user.home_town
        form.gender.data = current_user.gender
        form.address.data = current_user.address
        form.phone_number.data = current_user.phone_number
        form.role.data = current_user.role
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/all_user")
@login_required
def all_user():
    if not current_user.is_authenticated:
        return abort(403)
    users = User.query.all()
    return render_template('all_user.html', users=users)

@app.route("/user/<string:username>")
@login_required
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

@app.route("/user/<string:username>/delete", methods=['POST'])
@login_required
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User has been deleted.', 'success')
    else:
        flash('User not found.', 'danger')
    return redirect(url_for('all_user'))

@app.route('/create_room', methods=['GET', 'POST'])
@login_required
def create_room():
    form = RoomForm()
    if form.validate_on_submit():
        name = form.name.data
        type = form.type.data
        price = form.price.data
        status = form.status.data
        note = form.note.data
        room = Room(name=name, status=status, note=note, type=type, price=price)
        db.session.add(room)
        db.session.commit()

        flash('Phòng đã được tạo thành công!', 'success')
        return redirect(url_for('room_list'))

    return render_template('create_room.html', form=form)


@app.route('/room_list')
@login_required
def room_list():
    rooms = Room.query.all()
    return render_template('room_list.html', rooms=rooms)

@app.route('/update_room/<int:room_id>', methods=['GET', 'POST'])
@login_required
def update_room(room_id):
    form = RoomForm()
    room = Room.query.get(room_id)
    if form.validate_on_submit():
        room.name = form.name.data
        room.type = form.type.data
        room.price = form.price.data  # Giá phòng được nhập từ form
        room.status = form.status.data
        room.note = form.note.data
        db.session.commit()
        flash('Room has been updated.', 'success')
        return redirect(url_for('room_list'))
    return render_template('update_room.html', form=form, room=room)



@app.route('/delete_room/<int:room_id>', methods=['POST'])
@login_required
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    if room:
        db.session.delete(room)
        db.session.commit()
        flash('Phòng đã được xóa thành công.', 'success')
    else:
        flash('Không tìm thấy phòng.', 'danger')
    return redirect(url_for('room_list'))


@app.route('/search', methods=['GET'])
@login_required
def search():
    room_name = request.args.get('room_name')
    room_price_min = request.args.get('room_price_min')
    room_price_max = request.args.get('room_price_max')
    room_type = request.args.get('room_type')
    query = Room.query
    if room_name:
        query = query.filter(Room.name.ilike(f'%{room_name}%'))
    if room_price_min and room_price_max:
        query = query.filter(Room.price.between(int(room_price_min), int(room_price_max)))
    if room_type:
        query = query.filter(Room.type.ilike(f'%{room_type}%'))
    results = query.all()
    return render_template('room_list.html', rooms=results)


def check_room_capacity(room_name):
    room = Room.query.filter_by(name=room_name).first()
    if room:
        rental_count = Rental.query.filter_by(room_name=room_name).count()
        return rental_count < 3
    return False


def update_room_capacity(room_name):
    room = Room.query.filter_by(name=room_name).first()
    if room:
        rental_count = Rental.query.filter_by(room_name=room_name).count()
        room.num_customers = rental_count
        db.session.commit()

def calculate_unit_price(room_name, num_customers, customer_type):
    room = Room.query.filter_by(name=room_name).first()
    unit_price = room.price
    if num_customers <= 2 and customer_type == "Nội địa":
        return unit_price
    if num_customers > 2 and customer_type == "Nội địa":
        return unit_price * 0.25
    if num_customers <= 2 and customer_type == "Nước ngoài":
        return unit_price * 1.5
    if num_customers > 2 and customer_type == "Nước ngoài":
        return unit_price * 1.5

@app.route('/create_rental', methods=['GET', 'POST'])
@login_required
def create_rental():
    form = RentalForm()
    if form.validate_on_submit():
        if not check_room_capacity(form.room_name.data):
            flash('Phòng đã đạt đến giới hạn số lượng khách hàng.', 'danger')
            return redirect(url_for('room_list'))
        unit_price = calculate_unit_price(form.room_name.data, form.num_customers.data, form.customer_type.data)
        number_of_days = (form.payment_date.data - form.start_date.data).days + 1
        total_amount = unit_price * number_of_days
        rental = Rental(
            room_name=form.room_name.data,
            customer_name=form.customer_name.data,
            customer_type=form.customer_type.data,
            customer_id=form.customer_id.data,
            customer_address=form.customer_address.data,
            num_customers=form.num_customers.data,
            start_date=form.start_date.data,
            payment_date=form.payment_date.data,
            total_amount=total_amount,
            unit_price=unit_price,
            number_of_days=number_of_days,
            amount=total_amount,
            paid="False"
        )
        db.session.add(rental)
        db.session.commit()
        update_room_capacity(form.room_name.data)

        flash('Phiếu thuê đã được tạo thành công!', 'success')
        return redirect(url_for('rental_list'))

    return render_template('create_rental.html', form=form)



@app.route('/rental/<int:rental_id>')
@login_required
def rental_detail(rental_id):
    rental = Rental.query.get(rental_id)
    if rental:
        return render_template('rental_detail.html', rental=rental)
    flash('Không tìm thấy phiếu thuê.', 'error')
    return redirect(url_for('rental_list'))


@app.route('/rental_list')
@login_required
def rental_list():
    rentals = Rental.query.all()
    return render_template('rental_list.html', rentals=rentals)

@app.route('/rental/<int:rental_id>/payment', methods=['GET', 'POST'])
@login_required
def rental_payment(rental_id):
    rental = Rental.query.get(rental_id)
    if not rental:
        flash('Không tìm thấy phiếu thuê.', 'error')
        return redirect(url_for('rental_list'))
    if request.method == 'POST':
        rental.paid = "True"
        db.session.commit()
        flash('Thanh toán thành công!', 'success')
        return redirect(url_for('rental_detail', rental_id=rental_id))
    return render_template('payment.html', rental=rental)



if __name__ == '__main__':
    app.run(debug=True)