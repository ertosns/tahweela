from faker import Faker
import json
import random
import math
import requests
from requests.auth import HTTPBasicAuth
import psycopg2
from argparse import ArgumentParser
import logging
import pandas as pd
#from core.queries.exists import credential_exists
#from core.queries.inserts import new_cred
#from core.queries.gets import get_last_timestamp
#from core.connection_cursor import conn, cur
from core.utils import CONTACTS_URL, GOODS_URL, REGISTER_URL, LEDGER_URL, PURCHASE_URL, BALANCE_URL, MAX_GOODS, MAX_COST, STOCHASTIC_TRADE_THRESHOLD
from core.queries.database import database

db_configs="dbname='demo_client'  user='tahweela_client' password='tahweela'"

logging.basicConfig(filename="client.log", \
                    format='%(asctime)s %(message)s', \
                    filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)

class good(object):
    def __init__(self, fake, gid=None, gname=None, gcost=None, gquality=None):
        self.gid = 0 if gid==None else gid
        self.name = fake.name() if gname==None else gname
        self.cost = random.random()*MAX_COST if gcost==None else gcost
        self.quality = random.random() if gquality==None else gquality
1
class Client(object):
    def __init__(self, seed):
        self.uname=None
        self.pas=None
        self.db = database(db_configs)
        self.my_contacts = []
        self.all_goods = []
        self.faker = Faker()
        random.seed(seed)
        Faker.seed(seed)
        self.__register()
        self.__init_goods()
        # credentials username:password
        logger.info("client initialized")

    def auth(self):
        logger.info("auth ("+str(self.uname)+":"+str(self.pas)+")")
        return HTTPBasicAuth(self.uname, self.pas)
    def __get_dict(self, ret):
        res=ret.decode('utf8')#.replace('"', "'")
        return json.loads(res)
    def __init_goods(self):
        """fetch all market goods, this should run in the background,
        and constantly find new updates

        note (make sure the user is registered before calling this function)
        """
        ret = requests.get(GOODS_URL, auth=self.auth())
        #TODO assert res.status_code == requests.codes.ok
        response = ret.content.decode('utf8')#.replace('"', "'")
        res = json.loads(response)
        print("init_goods, res: ", res)
        if 'goods' not in res:
            print("response crud", response)
            print("response in json", res)
            logger.critical("not goods received from the market!")
            raise Exception("failed request")
        goods = pd.read_json(res['goods'])
        self.all_goods = [good(goods.iloc[i]['id'], goods.iloc[i]['good_name'],  goods.iloc[i]['good_cost'], goods.iloc[i]['good_quality']) for i in range(len(goods)-1)]
    def __register(self):
        """ check if this client has credentials, if not register

        """
        #check if user have credentials
        self.db.init()
        try:
            user_exists=self.db.exists.credential_exists(1)
            if not user_exists:
                #register user
                name = self.faker.name()
                #email = self.faker.email()
                #country = self.faker.country()
                #address = self.faker.address()
                my_goods = [good(self.faker) for i in range(math.ceil(random.random()*MAX_GOODS))]
                #TODO check repose status_code makes sure it's request.codes.ok
                res=requests.post(REGISTER_URL, data=json.dumps({'name':name}))
                print(type(res))
                print(res)
                print(res.text)
                response = json.loads(res.text)
                #response = json.loads(res.text.replace("'", '"'))
                self.uname=response['cred_id']
                self.pas=response['passcode']
                print("add_cred")
                self.db.inserts.add_cred(response['passcode'], response['cred_id'])
                print("add_cred success")
                logger.debug("username:"+str(self.uname)+", passcode: "+str(self.pas))
                ##############
                # post goods #
                ##############
                payload=json.dumps({'goods': [(g.name, g.cost, g.quality) for g in my_goods]})
                requests.post(GOODS_URL, data=payload, auth=self.auth())
                #TODO assert that requests.text is equivalent to payload
            else:
                self.__update_ledger()
            self.db.commit()
        except psycopg2.DatabaseError as error:
            logger.critical("registration failed!, error: "+ str(error))
            print("register failed!, error: "+str(error))
            self.db.rollback()
        finally:
            self.db.close()
    def add_contact(self, credid):
        """Fetch the client with credential id (credid)

        @param credid: client credential id
        """
        ret=requests.post(CONTACTS_URL, data=json.dumps({'cred_id': credid}), auth=self.auth())
        respose=ret.text.decode('utf8')#.replace('"', "'")
        res = json.laods(response)
        contact = res['contact']
        self.db.init()
        try:
            self.db.inserts.add_contact(contact['contact_id'], \
                                        contact['contact_name'], \
                                        contact['bank_account_id'])
            self.db.commit()
        except psycopg2.DatabaseError as error:
            self.db.rollback()
        finally:
            self.db.close()
    def __purchase(self, gid):
        pur_item = {'id': gid}
        ret=requests.post(PURCHASE_URL, data=json.dumps(pur_item), auth=self.auth())
        response=ret.text#ret.text.decode('utf8')#.replace('"', "'")
        trx=json.loads(response)
        return trx
    def __add_trax(self, trans):
        trans=trans['transactions'] #TODO (res)
        self.db.init()
        try:
            print("trans: ", trans)
            #self.db.inserts.insert_trx(trans["trx_src"], trans['trx_dest'], trans['trx_gid'])
            self.db.inserts.insert_trx(trans["trx_src"], trans['trx_dest'], trans['good_id'])
            self.db.commit()
        except psycopg2.DatabaseError as error:
            self.db.rollback()
        finally:
            self.db.close()
    def __update_balance(self, balance):
        #TODO fix
        if type(balance)==dict:
            self.balance=balance['balance']
            return
        self.balance=balance
    def __ledger_timestamp(self):
        dt=None
        self.db.init()
        try:
            dt=self.db.gets.get_last_timestamp()
            self.db.commmit()
        except psycopg2.DatabaseError as error:
            logger.critical("failed to retrieve ledger time stamp")
            self.db.rollback()
        finally:
            self.db.close()
        print("timestamp: ", dt)
        return dt
    def __update_ledger(self):
        """update ledger with sold goods, and update balance
        """
        ret=requests.post(LEDGER_URL, data=json.dumps({'trx_dt': self.__ledger_timestamp()}), auth=self.auth())
        #TODO always process the status code!
        res = json.loads(ret.text) #self.__get_dict(ret.text)
        print("new balance: ", res['balance'])
        self.__update_balance(res['balance'])
        self.db.init();
        try:
            new_trxs=res['transactions']
            print("trxs: ", new_trxs)
            transactions=pd.read_json(new_trxs)
            print("trxs pandas: ", transactions)
            if len(transactions)==0:
                raise Exception("empty transaction!")
            for i in range(len(transactions)-1):
                self.__add_trax(transactions.iloc[i])
        except psycopg2.DatabaseError as error:
            self.db.rollback()
        except:
            self.db.rollback()
        finally:
            self.db.close()
    def autotrade(self):
        """Stochastic fake auto-trading

        trade with randomly with maintained contacts with 0.5 probability for each, and 0.1 probability for all contacts goods, update balance, and goods for each contact
        """
        #update balance, and add new transactions
        self.__update_ledger()
        for good in self.all_goods:
            print("gcost: ", good.cost)
            print("balance: ", self.balance)
            if random.random()> STOCHASTIC_TRADE_THRESHOLD and \
               good.cost <= self.balance:
                #TODO (fix) doesn't work!
                #trx=self.__purchase(good.gid)
                trx=self.__purchase(1)
                self.__add_trax(trx)
                self.__update_balance(trx)

#TODO add contacts from the command line
parser = ArgumentParser()
parser.add_argument('-c', '--add_contact', type=int)
parser.add_argument('-s', '--seed', type=int)
args=parser.parse_args()
cred_id=args.add_contact
seed=args.seed
seed=seed if not seed==None else 4321
trader = Client(seed)
if cred_id:
    trader.add_contact(int(cred_id))
trader.autotrade()
