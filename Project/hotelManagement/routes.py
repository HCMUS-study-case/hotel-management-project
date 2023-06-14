from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from hotelManagement import app, db
from hotelManagement.forms import RegistrationForm, LoginForm, UpdateAccountForm, RoomForm, RentalForm
from hotelManagement.models import User, Room, Rental
from datetime import datetime
from PIL import Image
import os
import secrets
import random
import string


with app.app_context():
    db.create_all()


@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/login_admin", methods=['GET', 'POST'])
def create_admin():
    admin = User(name="ADMIN", citizen_id="ADMIN", place_issued="ADMIN", 
            birthdate=datetime.strptime("01/01/2000", "%d/%m/%Y").date(), home_town="ADMIN", gender="ADMIN", 
            address="ADMIN", phone_number="ADMIN", role="AD", 
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
        role = form.role.data
        random_numbers = ''.join(random.choices(string.digits, k=6))
        username = f"{role}{random_numbers}"
        if len(username) != 8 or not username[:2].isalpha() or not username[2:].isdigit():
            flash('Username không hợp lệ', 'danger')
            return redirect(url_for('register'))
        user = User(name=form.name.data, citizen_id=form.citizen_id.data, place_issued=form.place_issued.data, 
                    birthdate=form.birthdate.data, home_town=form.home_town.data, gender=form.gender.data, 
                    address=form.address.data, phone_number=form.phone_number.data, role=form.role.data, 
                    username=username, email=form.email.data, password=form.password.data)
        with app.app_context():            
            db.session.add(user)
            db.session.commit()
        flash('Đăng ký thành công', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Đăng ký', form=form)


@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        if not form.username.data and form.password.data:
            flash('Vui lòng nhập Tên đăng nhập', 'danger')
        elif not form.password.data and form.username.data:
            flash('Vui lòng nhập Mật khẩu', 'danger')
        elif not form.username.data or not form.password.data:
            flash('Vui lòng nhập Tên đăng nhập và Mật khẩu', 'danger')
        else:
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                if user.password == form.password.data:
                    login_user(user, remember=form.remember.data)
                    next_page = request.args.get('next')
                    flash(f'{form.username.data} Đăng nhập thành công', 'success')
                    return redirect(next_page) if next_page else redirect(url_for('home'))
                else:
                    flash('Kiểm tra lại Mật khẩu', 'danger')
            else:
                flash('Kiểm tra lại Tên đăng nhập', 'danger')
    return render_template('login.html', title='Đăng nhập', form=form)


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
        current_user.password = form.password.data
        db.session.commit()
        flash('Tài khoản đã được cập nhật thành công', 'success')
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
        form.password.data = current_user.password
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Tài khoản', image_file=image_file, form=form)


@app.route("/all_user")
@login_required
def all_user():
    if not current_user.is_authenticated:
        return abort(403)
    users = User.query.all()
    return render_template('all_user.html', users=users, title="Tất cả tài khoản")


@app.route("/user/<string:username>")
@login_required
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user, title="Tài khoản")


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
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Lỗi: {error}', 'danger')
    return render_template('create_room.html', form=form, title="Tạo phòng")


@app.route('/room_list')
@login_required
def room_list():
    rooms = Room.query.all()
    return render_template('room_list.html', rooms=rooms, title="Danh sách tất cả các phòng")


@app.route('/update_room/<int:room_id>', methods=['GET', 'POST'])
@login_required
def update_room(room_id):
    form = RoomForm()
    room = Room.query.get(room_id)
    if form.validate_on_submit():
        room.name = form.name.data
        room.type = form.type.data
        room.price = form.price.data
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


@app.route('/report/')
@login_required
def report():
    return render_template('report.html')


@app.route('/report/revenue_report')
@login_required
def revenue_report():
    room_types = Room.query.with_entities(Room.type).distinct().all()
    revenue_by_room_type = []
    overall_total_revenue = Rental.query.with_entities(db.func.sum(Rental.total_amount)).scalar()
    for room_type in room_types:
        total_revenue = Rental.query.with_entities(db.func.sum(Rental.total_amount)).join(Room).filter(Room.type == room_type[0]).scalar()
        if total_revenue is not None and overall_total_revenue is not None and overall_total_revenue != 0:
            revenue_ratio = (total_revenue / overall_total_revenue) * 100
        else:
            revenue_ratio = 0
        revenue_by_room_type.append({
            'room_type': room_type[0],
            'total_revenue': total_revenue or 0,
            'revenue_ratio': revenue_ratio
        })
    return render_template('revenue_report.html', revenue_by_room_type=revenue_by_room_type)


@app.route('/report/monthly_report')
@login_required
def monthly_report():
    month = datetime.now().strftime('%m/%Y')
    report_data = {}
    room_days_rented = {}
    total_days_rented = 0
    rooms = Room.query.all()
    for room in rooms:
        room_days_rented[room.name] = 0
    rental_records = Rental.query.filter(db.extract('month', Rental.start_date) == datetime.now().month).all()
    for record in rental_records:
        days_rented = (record.payment_date - record.start_date).days + 1
        total_days_rented += days_rented
        room_days_rented[record.room_name] += days_rented
    for index, room in enumerate(rooms, start=1):
        if total_days_rented > 0:
            percentage = (room_days_rented[room.name] / total_days_rented) * 100
        else:
            percentage = 0.0
        report_data[index] = {
            'room': room.name,
            'days_rented': room_days_rented[room.name],
            'percentage': percentage
        }
    return render_template('monthly_report.html', month=month, report_data=report_data)