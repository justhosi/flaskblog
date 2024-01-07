from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from forms import RegisterForm, LoginForm, UpdateForm
import creds
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, logout_user, login_required, current_user

#Create the app instance
app = Flask(__name__)

app.config['SECRET_KEY'] = creds.secret_key 
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:password123@localhost/flaskblog'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def user_loader(user_id):
    return Users.query.get(user_id)


#Define the home page
@app.route('/')
def index():
    return render_template('index.html')

#Define the about page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the user register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    name = None
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_pw = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
            user = Users(name=form.name.data, email=form.email.data, username=form.username.data, favorite_color=form.color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        flash(f'{name}, you have registered successfully.', 'success')
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.color.data = ''
        form.password.data = ''
    our_users = Users.query.order_by(Users.date_registered)
    return render_template('register.html', form = form, name =name, our_users=our_users)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UpdateForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['color']

        try:
            db.session.commit()
            flash('Profile has been updated successfully', 'seccess')
            return render_template('profile.html')
        except:
            flash('Something went wrong...try again!', 'danger')
            return render_template('update.html', form = form, name_to_update = name_to_update)
    else:
        return render_template('update.html', form = form, name_to_update = name_to_update)

# Delete user from the databaase
@app.route('/delete/<int:id>')
def delete(id):
    user_to_del = Users.query.get_or_404(id)
    form = RegisterForm
    name = None
    try:
        db.session.delete(user_to_del)
        db.session.commit()
        flash('The user has been deleted', 'danger')
        our_users = Users.query.order_by(Users.date_registered)
        return redirect(url_for('register', form = form, name = name, our_users = our_users))
    
    except:
        flash('Something went wrong. Try again.', 'danger')
        return redirect(url_for('register', form = form, name = name, our_users = our_users))

# Create a login route  
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # When the form is submited
    if form.validate_on_submit():
        # Check if the user is in the database
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Login was successful', 'success')
                return render_template('profile.html', id=current_user.id)
            else:
                    flash('Please check email and password again!', 'danger')
        else:
                flash('Please check email and password again!', 'danger')
    return render_template('login.html', form = form)

# Create a profile page for users
@app.route('/profile')
# Prevent users access without being logged in
@login_required
def profile():
    return render_template('profile.html')






# Defines the Users model 
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(255))

    # Make sure the password is not accessible in database
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    # Set the password hash when the password is set
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # Verify the password and hashed password are same
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name


with app.app_context():
    db.create_all()


if __name__ == ('__main__'):
    app.run(debug=True)