import os
import secrets
from PIL import Image
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_login import LoginManager, login_user, current_user, logout_user, UserMixin, login_required


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dfdffdf'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(email):
    return User.query.filter_by(email=email).first()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    info = db.Column(db.String(20))
    birthday = db.Column(db.Date)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    time_online = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User'{self.username}', '{self.email}', '{self.image_file}', '{self.is_active}','{self.time_online}'," \
            f"'{self.phone}', '{self.info}''{self.birthday}'"

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.email)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime(120), nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text(20), nullable=False, )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post'{self.title}', '{self.date_posted}'"


@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.order_by("date_posted desc").all()
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.birthday = form.birthday.data
        current_user.info = form.info.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.birthday.data = current_user.birthday
        form.info.data = current_user.info
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('profile.html', title='Profile',
                           image_file=image_file, form=form)


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


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ReqistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created!', 'success')
        flash(f'Please update your profile info after login!!', "warning")
        return redirect(url_for('profile'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            user.is_active = True
            db.session.merge(user)
            db.session.commit()
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    current_user.is_active = False
    db.session.merge(current_user)
    db.session.commit()
    logout_user()
    return redirect(url_for('home'))


@app.route("/status", methods=['GET', 'POST'])
@login_required
def change_status():
    status = request.args.get('status')
    if int(status) == 1:
        current_user.is_active = True
    elif int(status) == 0:
        current_user.is_active = False
    db.session.merge(current_user)
    db.session.commit()
    return jsonify(current_user.is_active)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("New post added!", "success")
        return redirect(url_for('home'))
    return render_template('create_post.html', title="New Post", form=form)


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post, user_id=post.user_id)


@app.route("/users")
@login_required
def show_users():
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route("/user/<int:user_id>")
@login_required
def user(user_id):
    form = UpdateAccountForm()
    user = User.query.get_or_404(user_id)
    return render_template('user.html', title=user.username, user=user, form=form)


@app.before_request
def update_lastime():
    if current_user.is_authenticated:
        current_user.time_online = datetime.now()
        db.session.merge(current_user)
        db.session.commit()
    else:
        pass


if __name__ == '__main__':
    from form import ReqistrationForm, LoginForm, UpdateAccountForm, PostForm, DateField

    app.run(debug=True, host="0.0.0.0")
