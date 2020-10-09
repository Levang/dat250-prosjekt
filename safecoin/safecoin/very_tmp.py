do_action = True if form.create_account.data or form.delete_account.data else False
create_form_ok = True if form.create_account.data and form.account_name.data else False
delete_form_ok = True if form.delete_account.data and form.account_select.data else False
validation_submitted = True if form_validate.proceed.data else False
validation_validated = True if form_validate.validate() else False


if do_action:
    if form.create_account.data and not create_form_ok:
        # Pressed create account, but form is not correctly filled
        # Don't check if account number is valid yet, because of security reasons
        flash("Please enter a valid account number", "error")
        return render_template('accounts.html', account_list=account_list, form=form)
    return render_template("validate_request.html", form=form_validate)

if validation_submitted:
    # Run if submit button on auth page is pressed
    if validation_validated:
        # Run if valid info in auth form
        # TODO: Verify that auth is correct
        if form.create_account.data:
            pressed_create_account()
        elif form.delete_account.data:
            pressed_delete_account(form.account_select.data)
        return render_template("overview.html")
    else:
        # Run if form is incorrectly filled (aka not email in email field)
        flash_all_but_field_required(form_validate.email)
    return render_template("validate_request.html", form=form_validate)

