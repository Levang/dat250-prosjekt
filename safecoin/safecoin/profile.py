from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user, logout_user, fresh_login_required
from safecoin import app, db, redis, disable_caching
from safecoin.accounts_db import accStr_to_accList
from safecoin.encryption import decrypt, getCurUsersEmail, verify_pwd_2FA
from safecoin.forms import DeleteUserForm
from safecoin.logging import log_deleteuser


@app.route('/profile/', methods=["GET", "POST"])
@login_required
@fresh_login_required
def profilePage():
    form = DeleteUserForm()

    # True if form is validated and submitted correctly
    if form.validate_on_submit():
        # True if password an 2FA is correct
        err = deleteCurUser(form.password_deleteuser.data,
                            form.otp_deleteuser.data)  # Delete user, if all accounts is empty
        if not err:  # Return to home if no errors
            flash("User successfully deleted!", "success")
            return redirect(url_for('home')), disable_caching
        else:
            flash(err, "error")  # Flashes if authentication failed
    elif form.is_submitted():
        flash("Couldn't delete account due to an error")
    return render_template('profile.html', form=form, email=getCurUsersEmail().upper()), disable_caching


# Delete user from db if all accounts are empty
def deleteCurUser(password, otp):
    authenticated, user = verify_pwd_2FA(password, otp)
    if not authenticated:
        try:
            log_deleteuser(False, current_user.email, "NotAuthenticated")
        except:
            log_deleteuser(False, "NotAuthenticated")
        return "Couldn't delete account due to an error"

    if user.accounts:
        # Get list of users accounts
        enKey = decrypt(password, user.enKey, True)
        accStr = decrypt(enKey, user.accounts).decode("utf-8")
        accList = accStr_to_accList(accStr)

        # Loops through accounts and verifies that all accounts are empty
        for acc in accList:
            if acc[2] != 0.0:
                log_deleteuser(False, user.email, "HasAccounts")
                return "All bank accounts must be empty before you delete your user."

    # Delete user from db
    redis.delete(current_user.email)
    logout_user()
    db.session.delete(user)
    db.session.commit()
    log_deleteuser(True, user.email)
