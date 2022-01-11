from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,SelectField,TextAreaField,FileField,IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from flask_login import current_user

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',validators=[DataRequired(),Length(min=5,max=30)])
    
    submit = SubmitField('Login')