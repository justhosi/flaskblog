from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, SelectField, TextAreaField
from wtforms.validators import DataRequired, length, EqualTo, Email
from wtforms.widgets import TextArea

class RegisterForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    username = StringField('Choose a username', validators=[DataRequired()])
    email = StringField('Please enter your email address', validators=[Email()])
    color = SelectField(u'What is your favorite color?', choices=[('F6F7C4', 'Yellow'), ('FF6969', 'Red'), ('AEE2FF', 'Blue'), ('D0F5BE', 'Green')])
    password = PasswordField('Choose a password', validators=[DataRequired(), length(min=3)])
    confirm_password = PasswordField('Confirm your password', validators=[EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

class UpdateForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    username = StringField('Choose a username', validators=[DataRequired()])
    email = StringField('Please enter your email address', validators=[Email()])
    color = SelectField(u'What is your favorite color?', choices=[('warning', 'Yellow'), ('danger', 'Red'), ('primary', 'Blue'), ('success', 'Green')])
    submit = SubmitField('Update')

class LoginForm(FlaskForm):
    email = StringField('Please enter your email address', validators=[Email()])
    password = PasswordField('Enter your pasword', validators=[DataRequired()])
    submit = SubmitField('Sign in')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('What is on your mind?',widget=TextArea(), validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField('Post')

class SearchForm(FlaskForm):
    searched = StringField('Searched', validators=[DataRequired()])
    submit = SubmitField('Search')