import email_validator
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
import flask_scrypt
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional

from safecoin.models import User

# Remove when integrated with db
from safecoin.tmp import account_list


def flash_all_but_field_required(form_field, flash_type="error"):
    for string in form_field.errors:
        if string != "This field is required.":
            flash(string, flash_type)


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
    to = IntegerField('To*', validators=[DataRequired()], render_kw={"placeholder": "xxxxx.xx.xxxx"})
    msg = StringField('KID/message', validators=[Optional()], render_kw={"placeholder": "KID/message"})
    kr = IntegerField('Amount*', validators=[DataRequired()], render_kw={"placeholder": "0"})
    ore = IntegerField(validators=[Optional()], render_kw={"placeholder": "00"})
    pay = SubmitField('Pay')

    def get_select_field(self, user):
        choice_list = []
        global account_list
        for account in account_list:
            choice_list.append((account.number, f"{account.name} ({account.number})"))
        self.tfrom.choices = choice_list


class ValidatePaymentForm(FlaskForm):
    tfrom = IntegerField('From', render_kw={"readonly": True})
    to = IntegerField('To', render_kw={"readonly": True})
    msg = IntegerField('KID/message', render_kw={"readonly": True, "placeholder": "No KID/message"})
    kr = IntegerField('Amount', render_kw={"readonly": True})
    ore = IntegerField('Decimal', render_kw={"readonly": True, "placeholder": "00"})
    email_payment = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "email@example.com"})
    password_payment = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "password"})
    proceed_payment = SubmitField('Proceed')


class AccountsForm(FlaskForm):
    account_name = StringField('Account Name', validators=[Optional()], render_kw={"placeholder": "Account Name"})
    create_account = SubmitField('Create New Account')
    account_select = SelectField('Select Account', validators=[Optional()])
    delete_account = SubmitField('Delete')

    def get_select_field(self, user):
        choice_list = []
        global account_list
        for account in account_list:
            if account.balance != 0:
                continue
            choice_list.append((account.number, f"{account.name} ({account.number})"))
        self.account_select.choices = choice_list


class CreateAccountForm(FlaskForm):
    account_name = StringField('Account Name', render_kw={"readonly": True})
    email_create = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "email@example.com"})
    password_create = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "password"})
    proceed_create = SubmitField('Proceed')


class CreateDeleteForm(FlaskForm):
    account_select = IntegerField('Account Name', render_kw={"readonly": True})
    email_delete = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "email@example.com"})
    password_delete = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "password"})
    proceed_delete = SubmitField('Proceed')
