from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from forms import RegisterForm
import creds
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

#Create the app instance
app = Flask(__name__)

app.config['SECRET_KEY'] = creds.secret_key 
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:password123@localhost/flaskblog'
db = SQLAlchemy(app)

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

# Defines the Users model 
class Users(db.Model):
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