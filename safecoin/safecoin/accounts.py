from flask import render_template, request, flash, redirect
from flask_login import current_user, login_required, logout_user
from flask_wtf import FlaskForm
from cryptography.fernet import InvalidToken

from safecoin import app, redis, json, db, disable_caching
from safecoin.forms import AccountsForm, flash_all_but_field_required, CreateAccountForm, CreateDeleteForm
from safecoin.tmp import TmpAcc
from safecoin.models import Account
from safecoin.accounts_db import format_account_number, format_account_balance, addNewAccountToCurUser, deleteCurUsersAccountNumber
from safecoin.encryption import verify_pwd_2FA


# Formaterer
def format_account_list(acc_list: list):
    if acc_list is None:
        return None

    # Check the formatting
    if type(acc_list) != list or len(acc_list) < 1 or len(acc_list[0]) < 3 or type(acc_list[0][1]) != int:
        return None
    try:
        for account in acc_list:
            account[1] = format_account_number(account[1])
            account[2] = format_account_balance(account[2])
    except ValueError:
        print("ACC list formatting fucked itself!!!!!!!!!!!!!!!!!!!!!!!")
        return None


@app.route("/accounts/", methods=["GET", "POST"])
@login_required
def accounts():
    # Retrive the accounts list
    account_list = getAccountsList()

    # Declare form class
    form = AccountsForm()

    # Definer hva som skal ligge i dropdown liste
    # Denne bør være navn og kontonummer
    form.get_select_field(account_list)

    # Formater accounts om til list of lists
    format_account_list(account_list)

    # Create Account Form
    create_form = CreateAccountForm()

    # Delete Account Form
    delete_form = CreateDeleteForm()

    if account_list is None:
        account_list = [['', 'Please open an account', '']]

    # True if a button on accounts page is pressed
    do_action = False
    if form.create_account.data or form.delete_account.data:
        do_action = True

    # True if create account form on accounts page is correctly filled
    create_form_start = False
    if form.create_account.data and form.account_name.data:
        create_form_start = True

    # True if delete account form on accounts page is correctly filled
    delete_form_start = False
    if form.delete_account.data and form.account_select.data:
        delete_form_start = True

    # If the create form is submitted
    if create_form.validate_on_submit():
        # ADDS A new account to the user
        err = addNewAccountToCurUser(create_form.password_create.data, create_form.otp_create.data, create_form.account_name.data)
        # If an error occurs when creating an account flash it and re render the page
        if err:
            flash(err, "error")
            return render_template('accounts.html', account_list=account_list, form=form), disable_caching
        flash(f"Successfully Created Account {create_form.account_name.data}!", "success")
    elif create_form.proceed_create.data:
        flash("Didn't make any changes, due to an error")

    # If delete form is submitted
    if delete_form.validate_on_submit():
        # Call delete account function
        # If an error occurs when deleting an account flash it and re render the page
        err = deleteCurUsersAccountNumber(delete_form.account_select.data, delete_form.password_delete.data, delete_form.otp_delete.data)
        if err:
            flash(err, "error")
            return render_template('accounts.html', account_list=account_list, form=form), disable_caching
        flash(f"Successfully Deleted Account {delete_form.account_select.data}!", "success")
    elif delete_form.proceed_delete.data:
        flash("Didn't make any changes, due to an error")

    if do_action:

        # If user pressed create account and name field is filled
        if create_form_start:
            if form.create_account.data:

                flash(f"Validate creation of account")
                return render_template('validate_create_account.html', form=create_form), disable_caching

            flash("Please enter a name for your account", "error")
            return render_template('accounts.html', account_list=account_list, form=form), disable_caching

        # If user pressed delete account and an account is selected from the select form
        if delete_form_start:
            if form.account_select.data == 'x':
                flash("Please select an account", "error")
                return render_template('accounts.html', account_list=account_list, form=form), disable_caching
            flash(f"Validate deletion of account ")
            return render_template('validate_delete_account.html', form=delete_form), disable_caching

    return render_template('accounts.html', account_list=account_list, form=form), disable_caching


def getAccountsList():
    # Hent account info fra redis
    userDict = redis.get(current_user.email)

    # Konverter til dictionary
    userDict = json.loads(userDict)

    try:
        # Checking if user has any accounts
        userDict['accounts']
    except:
        # #if the user does not have any accounts
        return None

    i = 0
    account_list = []
    for accountnr in userDict['accounts']:  # Denne fungerer men må ryddes opp i, gjør det om til en funksjon elns.
        # accountnumber is a string so convert back to an int
        numberUsr = int(accountnr)

        # Henter første verdi fra accounts listen til accountnummer
        name = userDict['accounts'][accountnr][0]

        # Hent kontobalansen fra accounts database
        accountDB = Account.query.filter_by(number=numberUsr).first()

        # dersom verdien eksisterer
        if accountDB:
            balance = accountDB.balance

            # Formater info og legg dette i en liste
            account_list.append([name, numberUsr, balance])
        else:
            # Dersom vi søker på en konto som ikke ligger i databasen skal vi returnere umiddelbart
            # Hvordan fikk brukeren denne i listen sin
            # TODO Vurder om det skal logges
            # Kontoen ligger ikke i kontodatabasen
            return None

        i += 1
    return account_list
