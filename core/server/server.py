from flask import request, Flask, jsonify, abort, make_response, session
from flask_httpauth import HTTPBasicAuth
import datetime
import json
import random
import random as rand
import psycopg2
import re
import os
#
seed=int.from_bytes(os.urandom(2), 'big')
random.seed(seed)
#
#from core.connection_cursor import conn, cur
#

from core.utils import REGISTER, GOODS, LEDGER, CONTACTS, PURCHASE, BALANCE, MAX_GOODS, MAX_COST, MAX_BALANCE, FEE, ADD_BANK_ACCOUNT, TRANSACTION, weekly_limit, daily_limit, PaymentGate, Currency, process_cur, EUR, USD, EGP, CURRENCY, get_credid, TOTAL_BALANCE
from core.configs import db_configs

import logging
from core.queries.database import database

#db_configs="dbname='db'  user='postgres" #' password='tahweela'
#conn = psycopg2.connect(db_configs)
#cur=conn.cursor()
db = database(db_configs)
logging.basicConfig(filename="/tmp/server.log",\
                 format='%(asctime)s %(levelname)s %(message)s',\
                 filemode='w',
                 level=logging.DEBUG)
logger=logging.getLogger()
app = Flask('tahweela')
app.secret_key=os.urandom(24)
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
auth = HTTPBasicAuth()
logger.info("server initialized")

'''
@app.route('/')
def index():
    #  view transactions here
    if 'username' in session:
        username = session['username']
        return 'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to log out</a></b>"
    return "You are not logged in <br><a href = '/login'>" + "click here to log in</a>"

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        # authenticate, then store credentials
        return redirect(url_for('index'))
    return '''
    <b>login username</b>
    <form action="" method="post">
    <p><input type=text name="username"/></p>
    <p><input type=text name="password"/></p>
    <p<<input type=submit value=Login/></p>
    </form>
    '''

@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    return redirect(url_for('index'))
'''

@auth.verify_password
def authenticate(user, passcode):
    """authenticate user, with username/password

    user can be user's email, or registered name
    """
    db.init()
    try:
        db.repeatable_read()
        if not db.exists.user(user, passcode):
            emsg='FAILURE PASSOWRD MISMATCH'
            logger.info(emsg)
            raise Exception(emsg)
        cid=db.gets.get_cid(user, passcode)
        credid=db.gets.cid2credid(cid)
        db.commit()
        session['credid']=credid
        logger.info('AUTHENTICATION SUCCESS....')
    except psycopg2.DatabaseError as error:
        db.rollback()
        emsg="authentication failed with error: {}".format(str(error))
        logger.critical(emsg)
        abort(500, emsg)
        return None #doesn't reach here
    except:
        db.rollback()
        emsg
        logger.critical("authentication failed ")
        abort(403, emsg)
        return None #doesn't reach here!
    finally:
      db.close()
    return user

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': "forbidden access"}), 403)

@app.route(REGISTER, methods=['POST'])
def register_client():
  """register new client with email/name + password, expected json body would have keys ["name", "email", "passcode"]

  the expected post keys are ["name", "email", "passcode", "cur_pref"]
  @param name: client name
  @param email: client email
  @param passcode: client password
  @param cur_pref: is client preference currency [optional]
  """
  req=request.get_json(force=True)
  name=req.get('name', None)
  passcode=req.get('passcode', None)
  email=req.get('email', None)
  cur_pref=req.get('cur_pref', EUR)
  if not req or name==None or email==None or passcode==None:
    logger.critical("url is incomplete")
    abort(401, 'incomplete post payload')
  cred_id=get_credid(email)
  logger.info("registering trader for client: {}".format(name))
  bid=0
  db.init()
  lock=2
  try:
      db.lock_advisory(lock)
      email_exists=db.exists.account_byemail(email)
      if email_exists:
          print('email exists')
          abort(400)
          logger.debug("account {}/{} + {} already exists".\
                       format(name, email, passcode))
          raise Exception("account already exists!")
      if not db.exists.currency(cur_pref):
          currency=Currency(cur_pref)
          if not currency.valid():
              raise Exception("currency isn't supported!")
          db.inserts.add_currency(cur_pref, currency.rate)
      cur_pref_id=db.gets.get_currency_id(cur_pref)
      cid=db.inserts.add_client(req['name'], req['email'], cur_pref_id)
      logger.debug("client added")
      db.inserts.register(cid, passcode, cred_id)
      db.commit(lock)
  except psycopg2.DatabaseError as error:
    db.rollback(lock)
    emsg="registering failed, error: ".format(str(error))
    logger.critical(emsg)
    abort(500, emsg)
  except:
    db.rollback(lock)
    emsg="registering failed"
    logger.critical(emsg)
    abort(403, emsg)
  finally:
    db.close()
    res = {'cred_id': cred_id}
  return jsonify(res), 201

@app.route(ADD_BANK_ACCOUNT, methods=['POST'])
@auth.login_required
def add_bank_account():
  """ register bank account for the authenticated client of the current session

  the post body is expect to be json with keys ["bank_name", branch_number", "account_number", "name_reference"], a client can register more than one bank account for tahweela account.
  the keys expected are ['bank_name', 'branch_number', 'account_number', 'name_reference']

  @return json with keys ['balance', 'base']
  """
  req=request.get_json(force=True)
  bank_name=req.get("bank_name", None)
  branch_number=req.get("branch_number", None)
  account_number=req.get("account_number", None)
  name_reference=req.get("name_reference", "")
  if not req or bank_name==None or branch_number==None or account_number==None:
      emsg="incomplete request"
      logger.critical(emsg)
      abort(401, emsg)
  db.init()
  ADD_BANK_ACCOUNT_LOCK=7
  lock=ADD_BANK_ACCOUNT_LOCK
  try:
    db.lock_advisory(lock)
    cid=db.gets.credid2cid(session['credid'])
    logger.debug("client added")
    bank=PaymentGate(bank_name, branch_number, account_number, name_reference)
    if not bank.authenticated():
        raise Exception('payment gate authentication failure!')
    balance_dt=bank.get_balance()
    balance=balance_dt['balance']
    base_currency=balance_dt['base']
    if not db.exists.currency(base_currency):
        currency=Currency(base_currency)
        db.inserts.add_currency(base_currency, currency.rate)
    base_currency_id=db.gets.get_currency_id(base_currency)
    db.inserts.add_bank_account(cid, balance, bank_name, branch_number, account_number, name_reference, base_currency_id)
    db.commit(lock)
  except psycopg2.DatabaseError as error:
    db.rollback(lock)
    emsg="assigning bank account failed, error: "+str(error)
    logger.critical(emsg)
    abort(500, emsg)
  except:
    db.rollback(lock)
    emsg="adding bank account failed"
    logger.critical(emsg)
    abort(401)
  finally:
    db.close()
  return jsonify({'balance':balance, 'base': base_currency}), 201

@app.route(CONTACTS, methods=['POST'])
@auth.login_required
def add_contact():
    """get the credential for the given contact, it's verification function that a contact exists

    the expected json keys are ['email']
    @param 'email' is the contact email
    @return json with key 'credid', which is the credential id used in transaction
    """
    req=request.get_json(force=True)
    email=req.get('email', None)
    logger.info("requesting contact")
    if not req or email==None:
        emsg="incomplete URL"
        logger.debug(emsg)
        abort(401, emsg)
    payload={}
    db.init()
    try:
        db.repeatable_read()
        if not db.exists.account_byemail(email):
            emsg="contact doesn't exist"
            logger.critical(emsg)
            raise Exception(emsg)
        #get credid for the email/password
        dest_cid=db.gets.get_client_id_byemail(email)
        dest_credid=db.gets.cid2credid(dest_cid)
        payload = {"credid": dest_credid}
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        emsg="request failed, error: {}".format(str(error))
        logger.critical(emsg)
        abort(500, emsg)
    except Exception as error:
        db.rollback()
        emsg="requesting failed, error: {}".format(+str(error))
        logger.critical(emsg)
        abort(401, emsg)
    finally:
        db.close()
    return jsonify(payload), 201

@app.route(BALANCE, methods=['GET'])
@auth.login_required
def get_balance():
    """ get balance of the current client

    @return {'balance': balance, 'base': base}
    """
    balance=None
    logger.info("balance requested")
    db.init()
    try:
        db.repeatable_read()
        cid=db.gets.credid2cid(session['credid'])
        if not db.exists.bank_account_bycid(cid):
            raise Exception("no bank account added yet!")
        #this would return balance in bank base
        balance=db.gets.get_balance_by_credid(session['credid'])
        # transform balance to user preference
        pref_cur=db.gets.get_preference_currency_bycid(cid)
        amount=balance['balance']
        base=balance['base']
        currency=Currency(pref_cur, base)
        pref_balance=currency.exchange(amount)
        payload={'balance': pref_balance, 'base':pref_cur}
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        emsg="failed request, error: {} ".format(+str(error))
        logger.critical()
        abort(300, emsg)
    except:
        db.rollback()
        emsg="failed request"
        logger.critical(emsg)
        abort(300, emsg)
    finally:
        db.close()
    return jsonify(payload), 201


@app.route(TOTAL_BALANCE, methods=['GET'])
@auth.login_required
def get_total_balance():
    """ get total balance of the current client

    @return {'balance': balance, 'base': base}
    """
    balance=None
    logger.info("balance requested")
    db.init()
    try:
        db.repeatable_read()
        cid=db.gets.credid2cid(session['credid'])
        if not db.exists.bank_account_bycid(cid):
            raise Exception("no bank account added yet!")
        #this would return balance in bank base
        balance=db.gets.get_total_balance_by_credid(session['credid'])
        # transform balance to user preference
        pref_cur=db.gets.get_preference_currency_bycid(cid)
        amount=balance['balance']
        base=balance['base']
        currency=Currency(pref_cur, base)
        pref_balance=currency.exchange(amount)
        payload={'balance': pref_balance, 'base':pref_cur}
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        emsg="failed request, error: {} ".format(+str(error))
        logger.critical()
        abort(300, emsg)
    except:
        db.rollback()
        emsg="failed request"
        logger.critical(emsg)
        abort(300, emsg)
    finally:
        db.close()
    return jsonify(payload), 201

@app.route(CURRENCY, methods=['POST'])
@auth.login_required
def update_balance_preference():
    """update balance preference

    """
    req=request.get_json(force=True)
    base = req.get('base', None)
    logger.info("updating balance preference")
    if not req or base==None:
        emsg='incomplete url'
        logger.cirtical(emsg)
        abort(401, emsg)
    CURRENCY_LOCK=11
    lock=CURRENCY_LOCK
    db.init()
    try:
        db.lock_advisory(lock)
        if not db.exists.currency(base):
            currency=Currency(base)
            db.inserts.add_currency(basey, currency.rate)
        base_currency_id=db.gets.get_currency_id(base_currency)
        cid=db.gets.credid2cid(session['credid'])
        db.updates.currency_preference(cid, base)
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        emsg="request failure, error: {} ".format(str(error))
        logger.critical(emsg)
        abort(500, emsg)
    except Exception as error:
        db.rollback()
        emsg="request failure, error: {}".format(str(error))
        logger.critical(emsg)
        abort(401, emsg)
    finally:
        db.unlock_advisory(lock)
        db.close()

@app.route(LEDGER, methods=['POST'])
@auth.login_required
def update_ledger():
    req=request.get_json(force=True)
    logger.info("requesting ledger update")
    if not req:
        emsg="incomplete URL empty request!"
        logger.critical(emsg)
        abort(401, emsg)
    st_dt=req['trx_dt']
    payload={}
    db.init()
    lock=3
    try:
        db.lock_advisory(lock)
        sells_trax=db.gets.get_sells(session['credid'], st_dt).to_json()
        logger.debug("sells: {}".format(sells_trax))
        balance=db.gets.get_balance_by_credid(session['credid'])
        payload={'transactions': sells_trax, \
                 'balance': balance}
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        emsg="request failure, error: {}".format(str(error))
        logger.critical(emsg)
        abort(500, emsg)
    except:
        db.rollback()
        emsg="request failure"
        logger.critical(emsg)
        abort(401, emsg)
    finally:
        db.unlock_advisory(lock)
        db.close()
    return jsonify(payload), 201

@app.route(TRANSACTION, methods=['POST'])
@auth.login_required
def make_transaction():
    req=request.get_json(force=True)
    recipt_credid=req['credid']
    # the amount of transaction in Euro
    orig_amount=req['amount']
    currency_base=req.get('currency', EUR)
    #exchange amount to euro for processing
    to_euro = Currency(EUR, currency_base)
    amount=to_euro.exchange(orig_amount)
    trx_name=req.get('trx_name', '')
    #TRANSACTION LIMITS IN EUROS
    max_daily=daily_limit()
    max_weekly=weekly_limit()
    #here the weekly/daily conditions are pivoted by the current moment only, note that the bank system can have specific pivot hour (the first momemnt of the day, it's specific for the bank system, and need to be known before hand)
    week_past=datetime.datetime.now()-datetime.timedelta(days=7)
    day_past=datetime.datetime.now()-datetime.timedelta(days=1)
    #TODO abide to the  the constrains
    logger.info("making purchase")
    if not req or amount==None or recipt_credid==None:
        emsg="incomplete URL empty request"
        logger.critical(emsg)
        abort(401, emsg)
    #gid=req['id']
    db.init()
    MAKE_TRANSACTION_LOCK=9
    lock=MAKE_TRANSACTION_LOCK
    print('start transaction')
    try:
        db.lock_advisory(lock)
        #if this client have a bank account yet
        cid=db.gets.credid2cid(session['credid'])
        if not db.exists.bank_account_bycid(cid):
            raise Exception("client doesn't have any associated bank account!")
        #balance in bank base
        src_balance=db.gets.get_balance_by_credid(session['credid'])
        src_balance_exchange=Currency(EUR, src_balance['base'])
        src_balance_euro=src_balance_exchange.exchange(src_balance['balance'])
        if src_balance_euro<amount+FEE:
            emsg="client doesn't have enough credit to make transaction"
            logger.critical(emsg)
            raise Exception(emsg)
        #get transaction sum in euro
        weekly_trx_sum=db.gets.get_transactions_sum(session['credid'], week_past)
        daily_trx_sum=db.gets.get_transactions_sum(session['credid'], day_past)
        print('got trx sum! weekly: {}, daily{}'.format(weekly_trx_sum, daily_trx_sum))
        if weekly_trx_sum+amount>max_weekly or daily_trx_sum+amount>max_daily:
            emsg="client passed the daily/weekly limit"
            logger.info(emsg)
            raise Exception(emsg)
        cur_id=db.gets.get_currency_id(currency_base)
        #add transaction
        db.inserts.insert_trx(recipt_credid, session['credid'], amount, cur_id, trx_name)
        #TODO this can be minimized directly by credid
        #dest balance in bank base
        dest_balance=db.gets.get_balance_by_credid(recipt_credid)
        dest_balance_exchange=Currency(EUR, dest_balance['base'])
        dest_balance_euro=dest_balance_exchange.exchange(dest_balance['balance'])
        src_balance_new=src_balance_euro-(amount+FEE)
        dest_balance_new=dest_balance_euro+amount
        #exchange back to bank bas
        src_balance_new=src_balance_exchange.exchange_back(src_balance_new)
        dest_balance_new=dest_balance_exchange.exchange_back(dest_balance_new)
        src_cid=db.gets.credid2cid(session['credid'])
        des_cid=db.gets.credid2cid(recipt_credid)
        if src_cid==des_cid:
            print("src/dest {}/{}".format(src_cid, des_cid))
            emsg="you can't make transaction with oneself!"
            logger.critical(emsg)
            raise Exception(emsg)
        db.updates.update_account(src_cid, src_balance_new)
        db.updates.update_account(des_cid, dest_balance_new)
        trx = {'trx_dest': recipt_credid,  \
               'trx_src': session['credid'], \
               'trx_cost': orig_amount, \
               'trx_name':trx_name}
        payload={'balance': src_balance_new, \
                 'transactions': trx}
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        emsg="transaction failed, error: {}".format(str(error))
        logger.critical(emsg)
        abort(500, emsg)
    except:
        db.rollback()
        emsg="transaction failed"
        logger.critical(emsg)
        abort(401, emsg)
    finally:
        db.unlock_advisory(lock)
        db.close()
    return jsonify(payload), 201
'''
@app.route(GOODS, methods=['POST'])
@auth.login_required
def add_goods():
    req=request.get_json(force=True)
    logger.info("adding new good to the market")
    #TODO goods should be passed with authentication,
    # how to authenticate both in requests, and in flask
    if not req or 'goods' not in req:
        logger.critical("URL is incomplete missing goods")
        abort(401)
    goods={}
    db.init()
    lock=1
    try:
        db.lock_advisory(lock)
        cid=db.gets.credid2cid(session['credid'])
        if cid==None:
            logger.critical("client not found associated with given id")
            abort(403)
            raise Exception("invalid client")
        goods=req['goods']
        for good in goods:
            print("good", good[0], good[1], good[2])
            gid=db.inserts.add_good(good[0], good[1], good[2])
            db.inserts.add_owner(cid, gid)
        db.commit(lock)
    except psycopg2.DatabaseError as error:
        db.rollback(lock)
        logger.critical("error adding good, error: "+str(error))
        abort(300)
    except:
        db.rollback(lock)
        logger.critical("error adding good")
        abort(300)
    finally:
        db.close()
    return jsonify({'goods':goods}), 201

@app.route(GOODS, methods=['GET'])
@auth.login_required
def get_goods():
    logger.info("requesting good")
    goods={}
    db.init()
    try:
        db.repeatable_read()
        goods = db.gets.get_all_goods()
        print('goods:', goods)
        db.commit()
    except psycopg2.DatabaseError as error:
        print('db except!')
        db.rollback()
        logger.critical("process failed, error: "+str(error))
        abort(300)
    except:
        print("except")
        db.rollback()
        logger.critical("process failed")
        abort(300)
    finally:
        db.close()
        #TODO change column names
    return jsonify({"goods": goods}), 201
@app.route(PURCHASE, methods=['POST'])
@auth.login_required
def make_purchase():
    req=request.get_json(force=True)
    logger.info("making purchase")
    if not req:
        logger.critical("incomplete URL empty request")
        abort(401)
    gid=req['id']
    db.init()
    lock=4
    try:
        db.lock_advisory(lock)
        # cross reference owner_id, with good_id, with credentials
        # return credential id of the owner
        credid=db.gets.get_credid_with_gid(gid)
        # make, and add new transaction such that increase,
        # and decrease of the src/des balance need to be performed in single transaction, then add the transactioin to the ledger, if failed rollback
        cost=db.gets.get_new_price(gid)+FEE
        src_balance=db.gets.get_balance_by_credid(session['credid'])-(cost+FEE)
        des_balance=db.gets.get_balance_by_credid(credid)+cost
        src_cid=db.gets.credid2cid(session['credid'])
        des_cid=db.gets.credid2cid(credid)
        if src_cid==des_cid:
            logger.critical("you can't make purchase with oneself!")
            abort(403)
            raise Exception("you can't make purchase with oneself!")
        db.updates.update_account(src_cid, src_balance)
        db.updates.update_account(des_cid, des_balance)
        #TODO the ownership in the client side need to be updated as well,
        # in the database, and in the stateful list in memory
        # also fetch corresponding oid!
        #update_owner(oid, gid)
        trx = {'trx_dest': credid,
               'trx_src': session['credid'],
               'good_id': gid}
        payload={'balance': src_balance,
                 'transactions': trx}
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        logger.critical("purchase failed, error: "+str(error))
        abort(300)
    except:
        db.rollback()
        logger.critical("purchase failed")
        abort(300)
    finally:
        db.unlock_advisory(lock)
        db.close()
    return jsonify(payload), 201
'''

if __name__=="__main__":
    app.run(debug=True)
