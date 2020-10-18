from flask import render_template, request, flash, redirect
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from safecoin.accounts_db import addNewAccountToCurUser, deleteCurUsersAccountNumber

from safecoin import app, redis, json, db
from safecoin.forms import AccountsForm, flash_all_but_field_required, CreateAccountForm, CreateDeleteForm
from safecoin.tmp import TmpAcc
from safecoin.models import Account
from safecoin.accounts_db import format_account_number


#Formaterer
def format_account_list(acc_list: list):
    if type(acc_list) != list or len(acc_list) < 1 or len(acc_list[0]) < 3 or type(acc_list[0][1]) != int:
        return None
    try:
        for account in acc_list:
            account[1] = format_account_number(account[1])
    except ValueError:
        return None


@app.route("/accounts/", methods=["GET", "POST"])
@login_required
def accounts():
    #Retrive the accounts list
    account_list = getAccountsList()

    #Declare form class
    form = AccountsForm()

    #Definer hva som skal ligge i dropdown liste
    form.get_select_field(account_list)

    #
    format_account_list(account_list)

    create_form = CreateAccountForm()
    delete_form = CreateDeleteForm()


    do_action = form.create_account.data or form.delete_account.data
    create_form_start = form.create_account.data and form.account_name.data
    delete_form_start = form.delete_account.data and form.account_select.data

    if create_form.validate_on_submit():
        err = addNewAccountToCurUser(create_form.account_name.data, create_form.password_create.data)
        if err:
            flash(err, "error")
            return render_template('accounts.html', account_list=account_list, form=form)
        flash(f"Successfully Created Account {create_form.account_name.data}!", "success")

    if delete_form.validate_on_submit():
        err = deleteCurUsersAccountNumber(str(delete_form.account_select.data), delete_form.password_delete.data)
        if err:
            flash(err, "error")
            return render_template('accounts.html', account_list=account_list, form=form)
        flash(f"Successfully Deleted Account {delete_form.account_select.data}!", "success")

    if do_action:

        # If user pressed create account
        if form.create_account.data:
            if create_form_start:
                flash(f"Validate to create a new account with the name {form.account_name.data}")
                return render_template('validate_create_account.html', form=create_form)
            flash("Please enter a nickname for your account", "error")
            return render_template('accounts.html', account_list=account_list, form=form)

        # If user pressed delete account
        if delete_form_start:
            if form.account_select.data == 'x':
                flash("Please select an account", "error")
                return render_template('accounts.html', account_list=account_list, form=form)
            flash(f"Validate to delete your account with the name {form.account_select.data}")
            return render_template('validate_delete_account.html', form=delete_form)

    return render_template('accounts.html', account_list=account_list, form=form)


def getAccountsList():
    #Hent account info fra redis
    userDict = redis.get(current_user.email)
    #Konverter til dictionairy
    userDict = json.loads(userDict)

    i = 0
    account_list = []
    for accountnr in userDict['accounts']:  # Denne fungerer men må ryddes opp i, gjør det om til en funksjon elns.
        #accountnuber is a string so convert back to an int
        numberUsr = int(accountnr)

        #Henter første verdi fra accounts listen til accountnummer
        name = userDict['accounts'][accountnr][0]  # noe galt her no time to fix atm. Fikser senere

        #Hent kontobalansen fra accounts database
        accountDB = Account.query.filter_by(number=numberUsr).first()

        #dersom verdien eksisterer  
        if accountDB:
            balance = accountDB.balance

            # Formater info og legg dette i en liste
            account_list.append([name, numberUsr, balance])
        else:
            #Dersom vi søker på en konto som ikke ligger i databasen skal vi returnere umiddelbart
            #Hvordan fikk brukeren denne i listen sin
            #TODO Vurder om det skal logges
            #Kontoen ligger ikke i kontodatabasen
            return None

        i += 1
    return account_list
