from flask import request, Flask, jsonify, abort, make_response
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
from core.utils import REGISTER, GOODS, LEDGER, CONTACTS, PURCHASE, BALANCE, MAX_GOODS, MAX_COST, MAX_BALANCE, FEE, ADD_BANK_ACCOUNT, TRANSACTION, weekly_limit, daily_limit, PaymentGate, Currency, process_cur, EUR, USD, EGP, CURRENCY
#from core.queries.inserts import register, add_client, add_good, add_account
#from core.queries.gets import credid2cid, get_banking_id, get_name, get_good, get_all_goods, get_balance_by_credid, get_new_price, get_password
#from core.queries.updates import update_account, update_owner
import logging
from core.queries.database import database
db_configs="dbname='demo'  user='tahweela' password='tahweela'"
#conn = psycopg2.connect(db_configs)
#cur=conn.cursor()
db = database(db_configs)
logging.basicConfig(filename="server.log",\
                 format='%(asctime)s %(levelname)s %(message)s',\
                 filemode='w',
                 level=logging.DEBUG)
logger=logging.getLogger()

app = Flask('tahweela')
auth = HTTPBasicAuth()
#auth = HTTPDigestAuth()

client_passcode=None # credential pass-code
client_cred_id=None #credential id

logger.info("server initialized")

def get_credid():
    return int(3333333333333*random.random())

def is_email(email):
  return bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email))


@auth.verify_password
def authenticate(user, passcode):
    """authenticate user, with username/password

    user can be user's email, or registered name
    """
    print("AUTHENTICATING.....")
    '''
    #TODO (fix) it seams that is_email isn't strong enough, it fails for some emails
    if is_email(user):
      print('authenticating user by email: ', user)
      if db.exists.account_byemail(user):
        cid=db.gets.get_client_id_byemail(user)
      else:
        cid=-1
    else:
      print('authenticating user by name', user)
      if db.exists.account_byname(user, passcode):
        cid=db.gets.get_client_id_byname(user)
      else:
        cid=-1
    '''
    print('authenticating [{}+{}]...'.format(user, passcode))
    print('authenticating user by email: ', user)
    if db.exists.account_byemail(user):
      cid=db.gets.get_client_id_byemail(user)
    else:
      print('doesnt exist!')
      cid=-1
    if cid==-1:
      print('authenticating user by name', user)
      if db.exists.account_byname(user, passcode):
        cid=db.gets.get_client_id_byname(user)
      else:
        print('doesnt exist!')
        cid=-1
    #TODO support user as credid itself
    if cid==-1: #doesn't exists
        logger.critical("authentication failed")
        print('authentication failed ,doesnt exist')
        return None
    print('SET GLOBAL!')
    #TODO HOW TO MAKE SURE THAT CREDID IS UNIQUE?
    # brute force, keep trying new values that does exist,
    # is the simplest, otherwise use conguential generator
    global client_cred_id, client_passcode
    credid=db.gets.cid2credid(cid)
    #TODO implement cid2credid
    logger.debug("authenticating client with cred {}:{}". format(user, passcode))
    print('credid: ', credid)
    print("username: ", user)
    print("password: ", passcode)
    db.init()
    try:
      db.repeatable_read()
      passcode_eq= db.gets.get_password(credid)
      print("pass_code: ", passcode_eq)
      logger.info("username:"+str(user)+", passcode:"+str(passcode))
      if not passcode==passcode_eq:
        print('FAILURE PASSOWRD MISMATCH')
        raise Exception("password mismatch!")
      db.commit()
      print('AUTHENTICATION SUCCESS....')
    except psycopg2.DatabaseError as error:
      print('AUTHENTICATION FAILURE')
      db.rollback()
      logger.critical("authentication failed with error: "+str(error))
      abort(300)
      return None #doesn't reach here
    except:
      print('AUTHENTICATION FAILURE')
      db.rollback()
      logger.critical("authentication failed ")
      abort(300)
      return None #doesn't reach here!
    finally:
      db.close()
    client_cred_id=credid
    client_passcode=passcode
    return user

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': "forbidden access"}), 403)

#TODO add message to status code response
@app.route(REGISTER, methods=['POST'])
def register_client():
  """register new client with email/name + password, expected json body would have keys ["name", "email", "passcode"]

  """
  #TODO this can through exception, need to handle it
  req=request.get_json(force=True)
  print('req: ', req)
  name=req.get('name', None)
  passcode=req.get('passcode', None)
  email=req.get('email', None)
  cur_pref=req.get('cur_pref', EUR)
  if not req or name==None or email==None or passcode==None:
    logger.critical("url is incomplete missing name")
    print("incomplete!!!")
    abort(400)
  #TODO add constraint, and verification for the name/email, and passcode (at least not None!)
  cred_id=get_credid()
  logger.info("registering trader for client: "+ name)
  bid=0
  db.init()
  lock=2
  #TODO generalize get_credid
  #TODO add errors to response code
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
    print('REGISTRATION FAILURE')
    db.rollback(lock)
    logger.critical("registering failed, error: "+str(error))
    abort(300)
  except:
    print('REGISTRATION FAILURE')
    db.rollback(lock)
    logger.critical("registering failed")
    abort(400)
  finally:
    db.close()
    res = {'cred_id': cred_id}
  return jsonify(res), 201

@app.route(ADD_BANK_ACCOUNT, methods=['POST'])
@auth.login_required
def add_bank_account():
  """ register bank account for the authenticated client of the current session

  @param: the post body is expect to be json with keys ["bank_name", branch_number", "account_number", "name_reference"], a client can register more than one bank account for tahweela account.
  @return return bid (banking id), since multiple bank accounts are supported, bid need to be sent for each transaction so that, the transactions are done with it.
  """
  req=request.get_json(force=True)
  bank_name=req.get("bank_name", None)
  branch_number=req.get("branch_number", None)
  account_number=req.get("account_number", None)
  name_reference=req.get("name_reference", "")
  if not req or bank_name==None or branch_number==None or account_number==None:
    logger.critical("incomplete request")
    abort(401)
  db.init()
  ADD_BANK_ACCOUNT_LOCK=7
  lock=ADD_BANK_ACCOUNT_LOCK
  try:
    db.lock_advisory(lock)
    cid=db.gets.credid2cid(client_cred_id)
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
    print('err1')
    db.rollback(lock)
    logger.critical("assigning bank account failed, error: "+str(error))
    abort(300)
  except Exception as error:
    print('err2')
    db.rollback(lock)
    logger.critical("adding bank account failed, error: ", str(error))
    abort(300)
  finally:
    db.close()
  return jsonify({'balance':balance, 'base': base_currency}), 201

@app.route(CONTACTS, methods=['POST'])
@auth.login_required
def add_contact():
    """get the credential for the given contact
    """
    req=request.get_json(force=True)
    email=req.get('email', None)
    logger.info("requesting contact")
    if not req or email==None:
        logger.debug("incomplete URL")
        abort(401)
    payload={}
    db.init()
    try:
        db.repeatable_read()
        if not db.exists.account_byemail(email):
            logger.critical("contact doesn't exist")
            raise Exception("contact doesn't exists!")
        cid=db.gets.get_client_id_byemail(email)
        credid=db.gets.cid2credid(cid)
        # get name given cid
        name=db.gets.get_name(cid)
        payload = {"credid": credid}
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        logger.critical("request failed, error:"+str(error))
        abort(300)
    except Exception as error:
        db.rollback()
        logger.critical("requesting failed"+str(error))
        print('FAILURE, err: ', str(error))
        abort(400)
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
        cid=db.gets.credid2cid(client_cred_id)
        if not db.exists.bank_account_bycid(cid):
            raise Exception("no bank account added yet!")
        #this would return balance in bank base
        balance=db.gets.get_balance_by_credid(client_cred_id)
        # transform balance to user preference
        pref_cur=db.gets.get_preference_currency_bycid(cid)
        amount=balance['balance']
        print('|--------------> amount {}'.format(amount))
        base=balance['base']
        currency=Currency(pref_cur, base)
        pref_balance=currency.exchange(amount)
        print('|--------------> pref_balance {}'.format(pref_balance))
        payload={'balance': pref_balance, 'base':pref_cur}
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        logger.critical("failed request, error: "+str(error))
        abort(300)
    except:
        db.rollback()
        logger.critical("failed request")
        abort(300)
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
        logger.cirtical('incomplete url')
        abort(401)
    CURRENCY_LOCK=11
    lock=CURRENCY_LOCK
    db.init()
    try:
        db.lock_advisory(lock)
        if not db.exists.currency(base):
            currency=Currency(base)
            db.inserts.add_currency(basey, currency.rate)
        base_currency_id=db.gets.get_currency_id(base_currency)
        cid=db.gets.credid2cid(client_cred_id)
        db.updates.currency_preference(cid, base)
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        logger.critical("request failure, error: "+ str(error))
        abort(300)
    except Exception as error:
        db.rollback()
        logger.critical("request failure, error: "+ str(error))
        abort(300)
    finally:
        db.unlock_advisory(lock)
        db.close()

@app.route(LEDGER, methods=['POST'])
@auth.login_required
def update_ledger():
    req=request.get_json(force=True)
    logger.info("requesting ledger update")
    if not req:
        logger.critical("incomplete URL empty request!")
        abort(401)
    st_dt=req['trx_dt']
    payload={}
    db.init()
    lock=3
    try:
        db.lock_advisory(lock)
        print("getting sells")
        sells_trax=db.gets.get_sells(client_cred_id, st_dt).to_json()
        print("sells: ", sells_trax)
        balance=db.gets.get_balance_by_credid(client_cred_id)
        payload={'transactions': sells_trax, \
                 'balance': balance}
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        logger.critical("request failure, error: "+ str(error))
        abort(300)
    except:
        db.rollback()
        logger.critical("request failure")
        abort(300)
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
        logger.critical("incomplete URL empty request")
        abort(401)
    #gid=req['id']
    db.init()
    MAKE_TRANSACTION_LOCK=9
    lock=MAKE_TRANSACTION_LOCK
    print('start transaction')
    try:
        db.lock_advisory(lock)
        #if this client have a bank account yet
        cid=db.gets.credid2cid(client_cred_id)
        if not db.exists.bank_account_bycid(cid):
            raise Exception("client doesn't have any associated bank account!")
        #balance in bank base
        src_balance=db.gets.get_balance_by_credid(client_cred_id)
        src_balance_exchange=Currency(EUR, src_balance['base'])
        src_balance_euro=src_balance_exchange.exchange(src_balance['balance'])
        if src_balance_euro<amount+FEE:
            logger.info("client doesn't have enough credit to make transaction")
            raise Exception("no enough balance to make transaction")
        #get transaction sum in euro
        weekly_trx_sum=db.gets.get_transactions_sum(client_cred_id, week_past)
        daily_trx_sum=db.gets.get_transactions_sum(client_cred_id, day_past)
        print('got trx sum! weekly: {}, daily{}'.format(weekly_trx_sum, daily_trx_sum))
        if weekly_trx_sum+amount>max_weekly or daily_trx_sum+amount>max_daily:
            logger.info("client passed the daily/weekly limit")
            raise Exception("client passed the daily/weekly limits")
        cur_id=db.gets.get_currency_id(currency_base)
        #add transaction
        db.inserts.insert_trx(recipt_credid, client_cred_id, amount, cur_id, trx_name)
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
        src_cid=db.gets.credid2cid(client_cred_id)
        des_cid=db.gets.credid2cid(recipt_credid)
        if src_cid==des_cid:
            logger.critical("you can't make transaction with oneself!")
            abort(403)
            raise Exception("you can't make transaction with oneself!")
        db.updates.update_account(src_cid, src_balance_new)
        db.updates.update_account(des_cid, dest_balance_new)
        trx = {'trx_dest': recipt_credid,  \
               'trx_src': client_cred_id, \
               'trx_cost': orig_amount, \
               'trx_name':trx_name}
        payload={'balance': src_balance_new, \
                 'transactions': trx}
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        logger.critical("transaction failed, error: "+str(error))
        abort(300)
    except:
        db.rollback()
        logger.critical("transaction failed")
        abort(300)
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
        cid=db.gets.credid2cid(client_cred_id)
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
        src_balance=db.gets.get_balance_by_credid(client_cred_id)-(cost+FEE)
        des_balance=db.gets.get_balance_by_credid(credid)+cost
        src_cid=db.gets.credid2cid(client_cred_id)
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
               'trx_src': client_cred_id,
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
