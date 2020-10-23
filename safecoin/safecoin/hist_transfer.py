from flask import render_template
from flask_login import current_user, login_required

from safecoin import app, redis, json, disable_caching
from safecoin.forms import TransHistory
from safecoin.models import Transactions
from safecoin.accounts_db import format_account_number, format_account_balance
from safecoin.accounts import getAccountsList
from safecoin.encryption import illegalChar


@app.route("/transactions/", methods=["GET", "POST"])
@login_required
def transactions():

    transForm = TransHistory()

    accountList=getAccountsList()
    transForm.get_select_field(accountList)

    TransList=[]

    if transForm.view_hist.data and transForm.accountSelect.data!="x":

        #Sanetize input
        illegal=illegalChar(transForm.accountSelect.data,11,"0123456789")

        if (str(transForm.accountSelect.data) in str(accountList)) and illegal==False:
            query=Transactions.query.filter((Transactions.accountFrom == transForm.accountSelect.data) | (Transactions.accountTo == transForm.accountSelect.data))

            TransList=QueryToList(query, accountList, transForm.accountSelect.data)
        else:
            #TODO LOG THIS!

    return render_template('hist_transfer.html', transHistory=TransList, form=transForm), disable_caching


def QueryToList(query,accountList,currentAccount):

    user_dict = json.loads(redis.get(current_user.email))


    listTrans=[]

    for i in query:
        if i.accountFrom in str(accountList):
            name = user_dict['accounts'][i.accountFrom][0]
            accountFrom=f'{name} ( {format_account_number(i.accountFrom)} )'
        else:
            accountFrom = i.accountFrom

        if i.accountTo in str(accountList):
            name=user_dict['accounts'][i.accountTo][0]
            accountTo=f'{name} ( {format_account_number(i.accountTo)} )'
        else:
            accountTo = i.accountTo

        amount = format_account_balance(i.amount)
        in_ = "──"
        out = "──"

        if str(i.accountFrom) == str(currentAccount):
            out = amount
            in_ = "──"

        if str(i.accountTo) == str(currentAccount):
            out = "──"
            in_ = amount

        message = i.message
        time = str(i.time)[:-7]

        listTrans.append([accountFrom,accountTo,message,in_,out,time])


    return listTrans
