from faker import Faker
import json
import datetime
import random
import math
import requests
from requests.auth import HTTPBasicAuth
import psycopg2
from argparse import ArgumentParser
import logging
import pandas as pd
import string
import os
#from core.queries.exists import credential_exists
#from core.queries.inserts import new_cred
#from core.queries.gets import get_last_timestamp
#from core.connection_cursor import conn, cur
from core.utils import CONTACTS_URL, GOODS_URL, REGISTER_URL, LEDGER_URL, PURCHASE_URL, BALANCE_URL, MAX_GOODS, MAX_COST, STOCHASTIC_TRADE_THRESHOLD, TIMESTAMP_FORMAT, ADD_BANK_ACCOUNT_URL
from core.queries.database import database

db_configs="dbname='demo_client'  user='tahweela_client' password='tahweela'"

logging.basicConfig(filename="client.log", \
                    format='%(asctime)s %(message)s', \
                    filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)

'''
class good(object):
    def __init__(self, fake, gid=None, gname=None, gcost=None, gquality=None):
        self.gid = 0 if gid==None else gid
        self.name = fake.name() if gname==None else gname
        self.cost = random.random()*MAX_COST if gcost==None else gcost
        self.quality = random.random() if gquality==None else gquality
'''

seed=int.from_bytes(os.urandom(2), 'big')
random.seed(seed)
faker=Faker(seed)

def get_bank_name():
    return faker.name().split()[0]
def get_branch_number():
    return int(33*random.random())
def get_account_number():
    return int(3333333*random.random())
def get_name_reference():
    return faker.name().split()[1]
def get_name():
    return faker.name()
def get_email():
    return faker.email()
def get_balance():
    return 333*random.random()
def get_credid():
    return int(3333333333333*random.random())
def get_rand_pass(L=9):
    passcode=''.join(random.choice(string.ascii_uppercase+\
                                 string.ascii_lowercase+\
                                 string.digits)\
                     for _ in range(L))
    return passcode
def rand_alphanum(L=9):
    passcode=''.join(random.choice(string.ascii_uppercase+\
                                 string.ascii_lowercase+\
                                 string.digits)\
                     for _ in range(L))
    return passcode

class Client(object):
    def __init__(self):
        seed=int.from_bytes(os.urandom(2), 'big')
        self.faker = Faker()
        random.seed(seed)
        Faker.seed(seed)
        #
        self.name=get_name()
        self.passcode=get_rand_pass()
        self.email=get_email()
        self.bank_name=get_bank_name()
        self.branch_number=get_branch_number()
        self.account_number=get_account_number()
        self.name_reference=get_name_reference()
        #
        self.db = database(db_configs)
        self.my_contacts = []
        #Register user int he network
        self.register()
        #register user with bank account
        self.__register_bank_account(self.bank_name, self.branch_number, self.account_number, self.name_reference)
        logger.info("client initialized")
        #self.all_goods = []
        #self.__init_goods()
        # credentials username:password

    def auth(self):
        logger.info("auth ("+str(self.email)+":"+str(self.passcode)+")")
        return HTTPBasicAuth(self.email, self.passcode)

    def register(self):
        """ check if this client has credentials, if not register

        """
        #check if user have credentials
        self.db.init()
        try:
            if not self.db.exists.credential_exists(1):
                #register user
                #my_goods = [good(self.faker) for i in range(math.ceil(random.random()*MAX_GOODS))]
                #TODO check repose status_code makes sure it's request.codes.ok
                payload={'name':self.name, \
                         'email': self.email, \
                         'passcode': self.passcode}
                print('payload: ', payload)
                res=requests.post(REGISTER_URL, data=json.dumps(payload))
                response = json.loads(res.text)
                assert res.status_code==201, "status code is error {} ".format(res.status_code)
                print(response)
                credid=response['cred_id']
                #cid set to 0, since it never matters in the client side
                ###############TODO credid
                self.db.inserts.register(0, self.passcode, credid)
                logger.debug("user registered with credentials username: {}, email: {}, passcode: {}"\
                             .format(name, email, passcode))
                ##############
                # post goods #
                ##############
                #payload=json.dumps({'goods': [(g.name, g.cost, g.quality) for g in my_goods]})
                #requests.post(GOODS_URL, data=payload, auth=self.auth())
                #TODO assert that requests.text is equivalent to payload
            else:
                self.__update_ledger()
            self.db.commit()
            self.uname=email
            self.pas=passcode
        except psycopg2.DatabaseError as error:
            logger.critical("registration failed!, error: "+ str(error))
            print("register failed!, error: "+str(error))
            self.db.rollback()
        finally:
            self.db.close()
    def __register_bank_account(self, bank_name=None, branch_number=None, account_number=None, name_reference=None):
        """ check if this client has credentials, if not register

        """
        #check if user have credentials
        BRANCH_NUM_MAX=100
        ACCOUNT_NUMBER_MAX=10000000000
        self.db.init()
        try:
            #register user
            bank_name = self.faker.name() if bank_name==None else bank_name
            branch_number = random.random()*BRANCH_NUM_MAX if branch_number==None else branch_number
            account_number= random.random()*ACCOUNT_NUMBER_MAX if account_number==None else account_number
            name_reference= self.faker.name() if name_reference==None else name_reference
            payload={'bank_name':bank_name,
                     'branch_number':branch_number,
                     'account_number':account_number,
                     'name_reference':name_reference}
            res=requests.post(ADD_BANK_ACCOUNT_URL, \
                              data=json.dumps(payload), \
                              auth=self.auth())
            response = json.loads(res.text)
            scode=res.status_code
            #TODO support multiple accounts
            #create local client table for banking,
            #to insert balance, or each account.
            print('response for balance:  ', response)
            self.balance=response['balance']
            self.db.commit()

        except psycopg2.DatabaseError as error:
            logger.critical("bank account registration failed!, error: "+ str(error))
            print("bank account register failed!, error: "+str(error))
            self.db.rollback()
        finally:
            self.db.close()
    def add_contact(self, email, name):
        """Fetch the client with given email/name

        @param email: contact email
        @param name: contact name
        """
        #get client credential id
        cred={'email': email}
        ret=requests.post(CONTACTS_URL, \
                          data=json.dumps(cred), \
                          auth=self.auth())
        response=ret.text#.decode('utf8')#.replace('"', "'")
        print('add contact response: ', response)
        res = json.loads(response)
        credid = res['credid']
        self.db.init()
        try:
            self.db.inserts.insert_contact(email, name, credid)
            self.db.commit()
        except psycopg2.DatabaseError as error:
            self.db.rollback()
        finally:
            self.db.close()
    def __transact(self, credid, amount, currency='USD'):
        pur_item = {'credid': credid,
                    'amount':amount,
                    'currency': 'USD'}
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
            self.db.inserts.insert_trx(trans["trx_src"], trans['trx_dest'], trans['trx_cost'])
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


        return dt if not dt==None else datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
    def __update_ledger(self):
        """update ledger with sold goods, and update balance

        """
        ret=requests.post(LEDGER_URL, data=json.dumps({'trx_dt': self.__ledger_timestamp()}), auth=self.auth())
        #TODO always process the status code!
        print('status code: ', ret.status_code)
        res = json.loads(ret.text) #self.__get_dict(ret.text)
        print('res: ', res)
        print("new balance: ", res['balance'])
        self.__update_balance(res['balance'])
        self.db.init()
        try:
            new_trxs=res['transactions']
            print("trxs: ", new_trxs)
            transactions=pd.read_json(new_trxs)
            print("trxs pandas: ", transactions)
            if len(transactions)==0:
                logger.info("ledger is up to date!")
                return
            for i in range(len(transactions)-1):
                self.__add_trax(transactions.iloc[i])
            db.commit()
        except psycopg2.DatabaseError as error:
            print('FAILURE LEDGER UPDATE: ', str(error))
            self.db.rollback()
        except Exception as error:
            print('FAILURE LEDGER UPDATE: ', str(error))
            self.db.rollback()
        finally:
            self.db.close()
    def autotract(self):
        """Stochastic fake auto-tracting

        trade with randomly with maintained contacts with 0.5 probability for each, and 0.1 probability for all contacts goods, update balance, and goods for each contact
        """
        #update balance, and add new transactions
        MAX_TRACT_BALANCE=100000
        self.__update_ledger()
        for i in range(len(contacts_df-1)):
            contact_credid=contacts_df.iloc[i]['contact_id']
            contact_name=contacts_df.iloc[i]['contact_name']
            contact_email=contacts_df.iloc[i]['contact_email']
            amount=random.random()*MAX_TRACT_BALANCE
            logger.info("making transaction with {}[{}] by amount: {}".\
                        format(contact_name, contact_email, amount))
            #if random.random()> STOCHASTIC_TRADE_THRESHOLD and good.cost <= self.balance:
            #TODO (fix) doesn't work!
            #trx=self.__purchase(good.gid)
            trx=self.__transact(contact_credid, amount)
            self.__add_trax(trx)
            self.__update_balance(trx)
    '''
    def __get_dict(self, ret):
        res=ret.decode('utf8')#.replace('"', "'")
        return json.loads(res)
    '''
    '''
    def get_contacts(self):
        """ get all contacts data frame

        """
        self.db.init()
        try:
            contacts_df=self.db.gets.get_all_contacts()
            self.db.commit()
        except Exception as error:
            logger.info('getting contact failed! '+str(error))
            self.db.rollback
        finally:
            self.db.close()
        return contacts_df
    '''
    '''
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
'''
#TODO add contacts from the command line
parser = ArgumentParser()
parser.add_argument('-c', '--add_contact', type=int)
args=parser.parse_args()
cred_id=args.add_contact
trader1 = Client()
trader2 = Client()

#for _ in range(10):
    #trader1.add_contact(get_email(), get_name())

if cred_id:
    trader1.add_contact(int(cred_id))
trader1.autotract()
