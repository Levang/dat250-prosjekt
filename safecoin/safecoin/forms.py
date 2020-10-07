import email_validator
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
import flask_scrypt
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional

from safecoin.models import User

# Remove when integrated with db
from safecoin.accounts import account_list


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


class PayForm(FlaskForm):
    tfrom = SelectField('From*', validators=[DataRequired()])
    to = StringField('To*', validators=[DataRequired()], render_kw={"placeholder": "xxxxx.xx.xxxx"})
    msg = StringField('KID/message', validators=[Optional()], render_kw={"placeholder": "KID/message"})
    kr = IntegerField('Amount*', validators=[DataRequired()], render_kw={"placeholder": "0"})
    ore = IntegerField(validators=[Optional()], render_kw={"placeholder": "00"})
    pay = SubmitField('Pay')

    def get_select_field(self, user):
        choice_list = []
        global account_list
        for account in account_list:
            choice_list.append((account.number, account.number))
        self.tfrom.choices = choice_list
