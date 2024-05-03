from flask import render_template, Flask, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length

from flask_sqlalchemy import SQLAlchemy

from flask_login import login_user, logout_user, LoginManager, login_required, login_remembered, current_user

db=SQLAlchemy()
app = Flask(__name__)
app.config["SECRET_KEY"] = "ekjfhawidukawhjdjkadhb"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///video-meeting.sqlite"
db.init_app(app)


login_manager=LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20), nullable=False )
    lastname = db.Column(db.String(20), nullable=False )
    username = db.Column(db.String(20), nullable=False, unique=True )
    password = db.Column(db.String(20), nullable=False )
    email = db.Column(db.String(50), nullable=False, unique=True )

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

with app.app_context():
    db.create_all()

class LoginForm(FlaskForm):
    username = StringField(label="User Name", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])


class RegisterForm(FlaskForm):
    
    firstname = StringField(label="First Name", validators=[DataRequired()])
    lastname = PasswordField(label="Last Name", validators=[DataRequired()])
    email = EmailField(label="Email", validators=[DataRequired()])
    username = StringField(label="User Name", validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField(label="Password", validators=[DataRequired(), Length(min=6, max=20)])



@app.route("/")
def home():
    return "hello"

@app.route("/login", methods = ["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "GET":
        return render_template("login.html", form = form)
    else:
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", form = form)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if request.method == "POST" and form.validate_on_submit():
        firstname = form.firstname.data
        lastname=form.lastname.data
        email = form.email.data
        username = form.username.data
        password = form.password.data
        
        user = User(firstname=firstname,
                    lastname = lastname,
                    email = email,
                     username = username,
                     password = password )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    
    return render_template("register.html", form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", first_name = current_user.firstname, last_name = current_user.lastname)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/meeting")
@login_required
def meeting():
    return render_template("meeting.html", username = current_user.username)


@app.route("/join", methods=["GET", "POST"])
@login_required
def join():
    if request.method == "POST":
        room_id = request.form.get("roomID")
        return redirect(f"/meeting?roomID={room_id}")
    return render_template("join.html")