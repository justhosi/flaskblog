from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from forms import RegisterForm, LoginForm, UpdateForm, PostForm, SearchForm
import creds
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, logout_user, login_required, current_user
from flask_migrate import Migrate

#Create the app instance
app = Flask(__name__)

app.config['SECRET_KEY'] = creds.secret_key 
# Local database
# app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:password123@localhost/flaskblog'
# Heroku database
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://ayocknqsmlqqlg:dfeaf62427a370140e4e9811cbdcbbf24332f94f93f86cbe7271efa8449da294@ec2-3-232-218-211.compute-1.amazonaws.com:5432/d7do2qdhrcvmj0'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, user_id)


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
            flash('Profile has been updated successfully', 'success')
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

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return render_template('index.html')

# Create a profile page for users
@app.route('/profile')
# Prevent users access without being logged in
@login_required
def profile():
    return render_template('profile.html')

#To add post to blog
@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title = form.title.data, content= form.content.data, poster_id=poster, slug = form.slug.data)
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''  
        db.session.add(post)
        db.session.commit()
        flash('The post has been sent', 'success')
    
    return render_template('add_post.html', form=form)

@app.route('/posts')
def posts():
    id = current_user.id
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts, id = id)

@app.route('/posts/<int:id>')
def post(id):
    user_id = current_user.id
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post, user_id = user_id)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.slug = form.slug.data
        post.content = form.content.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated', 'success')
        return redirect(url_for('post', id = post.id))

    form.title.data = post.title
    form.slug.data = post.slug
    form.content.data =post.content
    return render_template('edit_post.html', form = form)

@app.route('/posts/delete/<int:id>')
@login_required
def post_to_delete(id):
    post_to_delete = Posts.query.get_or_404(id)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash('The post is deleted', 'danger')
        return redirect(url_for('posts'))

    except:
        flash('There was a problem! please try again.')
        return redirect(url_for('posts'))

# Create admin area and make user with id num 1 as admin 
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    users = Users.query.order_by(Users.id).all()
    if id == 1:
        return render_template('admin.html', users = users)
    else:
        flash('You dont have access to this page')
        return redirect(url_for('profile'))

# Create a search function 
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        # Get data from form
        post.searched = form.searched.data
        # Query the database
        posts = Posts.query.filter(Posts.content.like('%' + post.searched + '%'))
        posts = Posts.query.order_by(Posts.title).all()
        return render_template('search.html', form=form, posts=posts)

# Inject form into navbar template
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)



# Defines the Users model 
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(255))
    posts = db.relationship('Posts', backref= 'poster')

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

# Create a post database model    
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # To detemine who is the author of the post
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


with app.app_context():
    db.create_all()


if __name__ == ('__main__'):
    app.run(debug=True)