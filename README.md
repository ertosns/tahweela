# overview
the code is divided into the server ./core/server/server.py, and database ./core/queries/database.py, and tests ./core/tests/
the code has more features not mentioned in the criteria, specially at the database level, for the rest some of them aren't complete, others are halfway.

# documentation
to understand code you can refer to the documentation  to generate the documentation run 'make docgen' in this directory, also available under ./out


# preparing the environment, installing necessary libraries, and running the server is by executing 'sudo python3 install.sh'


# execution
to run the server execute sudo -u postgres python3 ./core/server/server.py.

# test
to run the tests execute 'sudo -u postgres python3 ./core/tests/database.py for testing the database', (15 test cases) and 'sudo -u postgres python3 ./core/tests/core_test.py' for testing the core stories (5 test cases)

# docker build
```console
    docker build -t mohabmetwally/tahweela
```
# docker run
```console
    docker run mohabmetwally/tahweela
```

# tahweela pull
```console
    docker pull mohabmetwally/tahweela
```

## tahweela stateless api

# [POST] /api/v0.1/register: register new user to tahweela server
the expected post json keys are ["name", "email", "passcode", "cur_pref"]
passcode: client password
cur_pref: [optional] currency preference
return json with keys ['cred_id']
cred_id: the credential id for the user, have no human interpretation, useful for wallet, only make sense to the server, also it's the has of the user email

# [POST] /api/v0.1/addbank: link new bank account to tahweela account (more than one account can be added)
the keys expected are ['bank_name', 'branch_number', 'account_number', 'name_reference']
return json with keys ['balance', 'base']
balance: is the client account balance in the bank account
base: is the currency base used by the bank

# [POST] /api/v0.1/contacts: add contact, used for verification purpose that a contact exist in tahweela network.
the expected json keys are ['email']
email: is the contact email
return json with keys ['credid']
credid: which is the credential id used in transaction, the same as 'cred_id' returned in registration step

# [GET] /api/v0.1/balance: to know the user balance (for single bank account)
return json with keys ['balance', 'base'] for single acccount
base: is the currency name of the balance (which is also the preference currency set by the client)

# ['GET']/api/v0.1/totalbalance:  get total balance (for more than a bank account, all accounts linked)
return json with keys ['balance', 'base'] for multiple accounts
base: is the currency name of the balance (which is also the preference currency set by the client)

# ['POST'] /api/v0.1/currency:  update balance preference
expect json with keys ['base']
base: is the new preference currency

# ['POST'] /api/v0.1/ledger: it update the client e_wallet with all transactions made, from starting date
expected keys ['trx_dt']
trx_dt: is the pivot date for transactions
return json with keys ['transactions', 'balance']
transactions: is json body with all transaction made
balance: is json body with with amount, and currency name

the documentation required that transaction is made by user email/email, see [POST] /api/v0.1/contacts, this is first called to return destination 'credid' which is further used to make transaction, this function isn't called directly if the 'credid' isn't known of course, but i imagine the scenario of using e_wallet, accessing another contact can be made more general, the transactions can be a bit anonymous (not from the server side, and can't be using fiat currency), but from the e_wallet prespective all is  needed for transaction is a hash key, no identity required, for this reason i provided two steps.
['POST'] /api/v0.1/transaction: make transaction by credid
expected paramters ['credid', 'amount', 'currency', 'trx_name']
currency: [optional]
trx_name: name of each transaction [optional]
return ['transactions', 'balance']
transactions: is json body with all transaction made
balance: is json body with with amount, and currency name
