from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, DateField, PasswordField, SubmitField, BooleanField, RadioField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from hotelManagement.models import User, Room, Rental

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
    username = StringField('Tên đăng nhập:')
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Đăng ký')
    def validate_citizen_id(self, citizen_id):
        user = User.query.filter_by(citizen_id=citizen_id.data).first()
        if user:
            raise ValidationError('Căc cước công dân đã tồn tại.')


class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập')
    password = PasswordField('Mật khẩu')
    remember = BooleanField('Nhớ tài khoản')
    submit = SubmitField('Đăng nhập')


class UpdateAccountForm(FlaskForm):
    name = StringField('Họ và tên', validators=[DataRequired()])
    citizen_id = StringField('Căn cước công dân', validators=[DataRequired()])
    place_issued = StringField('Nơi cấp', validators=[DataRequired()])
    birthdate = DateField('Ngày sinh', format='%Y-%m-%d', validators=[DataRequired()])
    home_town = StringField('Quê quán', validators=[DataRequired()])
    gender = RadioField('Giới tính', choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')], validators=[DataRequired()])
    address = StringField('Địa chỉ', validators=[DataRequired()])
    phone_number = StringField('SĐT', validators=[DataRequired()])
    role = SelectField('Vai trò', choices=[('AD', 'Admin'), ('HR', 'Nhân sự'), ('RE', 'Lễ tân'), ('AC', 'Kế toán'), ('WA', 'Phục vụ')], 
                        validators=[DataRequired()])
    username = StringField('Tên đăng nhập', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Mật khẩu', validators=[DataRequired()])
    picture = FileField('Cập nhật ảnh', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Cập nhật')
    def validate_citizen_id(self, citizen_id):
        if citizen_id.data != current_user.citizen_id:
            user = User.query.filter_by(citizen_id=citizen_id.data).first()
            if user:
                raise ValidationError('Căn cước công dân đã tồn tại!')


class RoomForm(FlaskForm):
    name = StringField('Tên phòng', validators=[DataRequired()])
    type = SelectField('Loại phòng', choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], validators=[DataRequired()])
    price = IntegerField("Giá phòng", validators=[DataRequired()])
    status = SelectField('Tình trạng', choices=[('Đầy', 'Đầy'), ('Có người', 'Có người'), ('Trống', 'Trống')], 
                        validators=[DataRequired()], default="Trống")
    note = StringField('Ghi chú')
    submit = SubmitField('Tạo phòng')
    def validate_name(self, field):
       existing_room = Room.query.filter_by(name=field.data).first()
       if existing_room:
        raise ValidationError('Tên phòng đã tồn tại. Vui lòng chọn tên khác.')


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