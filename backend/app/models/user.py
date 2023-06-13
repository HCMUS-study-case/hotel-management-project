from .. import db, argon2


class User(db.Model):
    __tablename__ = "user_account"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(8), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # role is a choice field, so we need to specify the choices (AD, HR, SA, WA, AC)
    role = db.Column(db.String(2), nullable=False)
    identify_number = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    # identify_card_front and identify_card_back are file paths
    identify_card_front = db.Column(db.String(255), nullable=False)
    identify_card_back = db.Column(db.String(255), nullable=False)
    # avatar is a file path
    avatar = db.Column(db.String(255), nullable=False)
    # phone_number is a string at most 10 digits
    phone_number = db.Column(db.String(10), nullable=False)
    # address is a string at most 255 characters
    address = db.Column(db.String(255), nullable=False)
    # status is a choice field, so we need to specify the choices (A, I, P)
    status = db.Column(db.String(1), nullable=False)

    # created_at and updated_at are timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    @property
    def password(self):
        raise AttributeError("password: write-only field")

    @password.setter
    def password(self, password):
        self.password_hash = argon2.generate_password_hash(password)

    def check_password(self, password):
        return argon2.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User '{}'>".format(self.username)


class UserFile(db.Model):
    __tablename__ = "user_file"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column()
