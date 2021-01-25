from flask import request, Flask, jsonify, abort, make_response
from flask_httpauth import HTTPBasicAuth
#from flask_httpauth import HTTPDigestAuth
import json
import random as rand
import psycopg2

#from core.connection_cursor import conn, cur
from core.utils import REGISTER, GOODS, LEDGER, CONTACTS, PURCHASE, BALANCE, MAX_GOODS, MAX_COST, MAX_BALANCE, FEE
#from core.queries.inserts import register, add_client, add_good, add_account
#from core.queries.gets import credid2cid, get_banking_id, get_name, get_good, get_all_goods, get_balance_by_credid, get_new_price, get_password
#from core.queries.updates import update_account, update_owner
import logging as logg
from core.queries.database import database
db_configs="dbname='demo'  user='tahweela' password='tahweela'"
#conn = psycopg2.connect(db_configs)
#cur=conn.cursor()
db = database(db_configs)
logg.basicConfig(filename="/tmp/tahweela_server.log",\
                 format='%(asctime)s %(levelname)s %(message)s',\
                 filemode='w',
                 level=logg.DEBUG)
logger=logg.getLogger()

app = Flask('tahweela')
auth = HTTPBasicAuth()
#auth = HTTPDigestAuth()

client_passcode=None # credential pass-code
#client_cid=None #credential id
client_passcode=None
logger.info("server initialized")


@auth.verify_password
def authenticate(username, password):
    global client_cred_id, client_passcode
    logger.debug("authenticating client")
    print("username: ", username)
    print("password: ", password)
    db.init()
    try:
        uname_bigint=float(username)
        pass_code= db.gets.get_password(uname_bigint)
        print("pass_code: ", pass_code)
        logger.info("username:"+str(username)+", passcode:"+str(pass_code))
        if not password==pass_code:
            raise Exception("password mismatch!")
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        logger.critical("authentication failed with error: "+str(error))
        abort(300)
        return None #doesn't reach here
    except:
        db.rollback()
        logger.critical("authentication failed ")
        abort(300)
        return None #doesn't reach here!
    finally:
        db.close()
    client_passcode=pass_code
    client_cred_id=uname_bigint
    return username

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': "forbidden access"}), 403)

@app.route(REGISTER, methods=['POST'])
def register_client():
    req=request.get_json(force=True)
    if not req or 'name' not in req:
        logging.critical("url is incomplete missing name")
        abort(400)
    logger.info("registering trader for client: "+ req['name'])
    cred_id=0
    passcode=None
    bid=0
    db.init()
    try:
        cid=db.inserts.add_client(req['name'])
        logger.debug("client added")
        cred_id, passcode = db.inserts.register(cid)
        bid=db.inserts.add_account(cid, rand.random()*MAX_BALANCE)
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        logger.critical("registering failed, error: "+str(error))
        abort(300)
    except:
        db.rollback()
        logger.critical("registering failed")
        abort(300)
    finally:
        db.close()
        res = {'cred_id': cred_id,
               'passcode': passcode,
               'bid': bid}
    return jsonify(res), 201

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
    try:
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
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        logger.critical("error adding good, error: "+str(error))
        abort(300)
    except:
        db.rollback()
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

@app.route(CONTACTS, methods=['POST'])
@auth.login_required
def get_contact():
    req=request.get_json(force=True)
    logger.info("requesting contact")
    if not req:
        logger.debug("incomplete URL")
        abort(401)
    payload={}
    db.init()
    try:
        cid=db.gets.credid2cid(req['cred_id']) # remote contact cred_id
        bid=db.gets.get_banking_id(cid)
        # get name given cid
        name=db.gets.get_name(cid)
        payload = {"contact_id": cid,
                   "contact_name": name,
                   "bank_account_id": bid}
        db.commit()
    except psycopg2.DatabaseError as error:
        db.rollback()
        logger.critical("requesting failed, error:"+str(error))
        abort(300)
    except:
        db.rollback()
        logger.critical("requesting failed")
        abort(300)
    finally:
        db.close()
    return jsonify(payload), 201

@app.route(BALANCE, methods=['GET'])
@auth.login_required
def get_balance():
    """ get balance of the current client

    """
    balance=None
    logger.info("balance requested")
    db.init()
    try:

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
    return balance

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
    try:
        print("getting sells")
        sells_trax=db.gets.get_sells(client_cred_id, st_dt).to_json()
        print("sells: ", sells_trax)
        balance=db.gets.get_balance_by_credid(client_cred_id)
        payload={'transactions': sells_trax,
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
        db.close()
    return jsonify(payload), 201

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
    try:
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
        db.close()
    return jsonify(payload), 201

if __name__=="__main__":
    app.run(debug=True)
