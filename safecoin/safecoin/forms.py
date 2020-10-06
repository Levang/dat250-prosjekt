import email_validator
from flask_wtf import FlaskForm
import flask_scrypt
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from safecoin.models import User


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "email@example.com"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "password"})
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        hashed_email = flask_scrypt.generate_password_hash(email.data, "")
        email = User.query.filter_by(email=hashed_email).first()
        if email:
            raise ValidationError('Something went wrong')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "email@example.com"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "password"})
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

class RemoveForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "email@example.com"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "password"})
    submit = SubmitField('Remove')
