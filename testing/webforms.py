from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length

# Create Login Form
class LoginForm(FlaskForm):
    
	""" Create login form for the login page.
	"""
	username = StringField("Username", validators=[DataRequired()], render_kw={"placeholder": "Username"})
	password = PasswordField("Password", validators=[], render_kw={"placeholder": "Password"})
	submit = SubmitField("Submit")