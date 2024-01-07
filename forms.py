from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, SelectField
from wtforms.validators import DataRequired, length, EqualTo, Email

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
    color = SelectField(u'What is your favorite color?', choices=[('F6F7C4', 'Yellow'), ('FF6969', 'Red'), ('AEE2FF', 'Blue'), ('D0F5BE', 'Green')])
    submit = SubmitField('Update')

class LoginForm(FlaskForm):
    email = StringField('Please enter your email address', validators=[Email()])
    password = PasswordField('Enter your pasword', validators=[DataRequired()])
    submit = SubmitField('Sign in')