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
import unittest
from core.server.server import app
import os
import string
from core.utils import CONTACTS_URL, GOODS_URL, REGISTER_URL, LEDGER_URL, PURCHASE_URL, BALANCE_URL, BALANCE, MAX_GOODS, MAX_COST, STOCHASTIC_TRADE_THRESHOLD, TRANSACTION_URL, ADD_BANK_ACCOUNT_URL, REGISTER, ADD_BANK_ACCOUNT, FEE, TRANSACTION, EUR, USD, EGP, process_cur, Currency, unwrap_cur
from core.queries.database import database
import base64

seed=int.from_bytes(os.urandom(3), 'big')
random.seed(seed)
faker=Faker(seed)
db_configs="dbname='demo'  user='tahweela' password='tahweela'"
logging.basicConfig(filename="core.log", \
                    format='%(asctime)s %(message)s', \
                    filemode='w')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)

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
def get_amount():
    return 3333*random.random()

class Client(object):
    def __init__(self, app):
        seed=int.from_bytes(os.urandom(2), 'big')
        self.faker = Faker()
        random.seed(seed)
        Faker.seed(seed)
        #
        self.app=app
        #
        self.name=get_name()
        self.passcode=get_rand_pass()
        self.email=get_email()
        self.bank_name=get_bank_name()
        self.branch_number=get_branch_number()
        self.account_number=get_account_number()
        self.name_reference=get_name_reference()
        self.currency_pref=EUR
        #
        self.db = database(db_configs)
        self.my_contacts = []
        # register
        self.register()
        self.register_bank_account()
        logger.info("client initialized")

    '''
    def auth(self):
        logger.info("auth ("+str(self.email)+":"+str(self.passcode)+")")
        return HTTPBasicAuth(self.email, self.passcode)
    '''
    def basic_auth(self):
        #using the emails doesn't succeed! i will try the byname instead
        valid_cred = base64.b64encode(bytes("{}:{}".format(self.email, self.passcode), 'utf-8')).decode("utf-8")
        #valid_cred = base64.b64encode(bytes("{}:{}".format(self.name, self.passcode), 'utf-8')).decode("utf-8")
        return valid_cred
    def headers(self):
        return {"Authorization": "Basic "+self.basic_auth()}
    def register(self):
        """ check if this client has credentials, if not register

        """
        payload={'name':self.name, \
                 'email': self.email, \
                 'passcode': self.passcode,\
                 'cur_pref':self.currency_pref}
        print('payload: ', payload)
        res=self.app.post(REGISTER_URL, data=json.dumps(payload))
        print('----------> register res: ', res)
        #response = json.loads(res.text)
        response = res.json#json.loads(res.data)
        print(response)

        assert res.status_code==201, "status code is error {} ".format(res.status_code)
        credid=response['cred_id']
        self.credid=credid
        logger.debug("user registered with credentials username: {}, email: {}, passcode: {}".format(self.name, self.email, self.passcode))

    def register_bank_account(self):
        """ check if this client has credentials, if not register

        """
        #check if user have credentials
        payload={'bank_name':self.bank_name, \
                 'branch_number':self.branch_number, \
                 'account_number':self.account_number,\
                 'name_reference':self.name_reference}
        res=self.app.post(ADD_BANK_ACCOUNT_URL, \
                          data=json.dumps(payload), \
                          headers=self.headers())
        #response = json.loads(res.text)
        response = res.json#json.loads(res.data)
        print('response', response)
        assert res.status_code == 201, 'registering bank account failed!'
        self.balance=response['balance']

    def add_contact(self, email, name):
        """Fetch the client with given email/name

        @param email: contact email
        @param name: contact name
        """
        #get client credential id
        cred={'email': email}
        ret=self.app.post(CONTACTS_URL, \
                          data=json.dumps(cred), \
                          headers=self.headers())
        assert ret.status_code==201, 'adding contact failed!'
        response=ret.json#json.loads(ret.data)
        print('add contact response: ', response)
        return response['credid']
    def get_balance(self):
        logger.info('verifying balance for {}/{} + {} with balance {}'.format(self.name, self.email, self.passcode, self.balance))
        res=self.app.get(BALANCE,headers=self.headers())
        print('------------> balance res: ', res)
        assert res.status_code== 201
        balance = res.json['balance']
        base = res.json['base']
        return balance, base
    #TODO update currency preference
    def make_transaction(self, email, name, amount):
        credid=self.add_contact(email, name)
        payload={'credid':credid,\
                 'amount': amount}
        res=self.app.post(TRANSACTION,\
                          data=json.dumps(payload),\
                          headers=self.headers())
        response=res.json
        print('|||--------> make transaction res: ', res)
        assert res.status_code==201
        print('make transaction response: {}'.format(response))
        balance_eq=response['balance']
        trxs=response['transactions']
        return (balance_eq, trxs)

class RestfulTest(unittest.TestCase):
    def setUp(self):
        self.app=app.test_client()
        self.uname=None
        self.pas=None
        logger.info("client initialized")
    #TODO cant work with adding client first!!
    '''
    def test_register(self):
        """ check if this client has credentials, if not register

        """
        name = get_name()
        email = get_email()
        passcode = get_rand_pass()
        payload={'name':name,\
                 'email': email,\
                 'passcode': passcode}
        #before register you need to add the client
        res=self.app.post(REGISTER, data=json.dumps(payload))
        response = res.json #json.loads(res.json)
        print('|______>register test respones: ', response)
        self.assertEqual(res.status_code, 201)
        credid=response['cred_id']
        #cid set to 0, since it never matters in the client side
        #self.db.inserts.register(0, passcode, credid)
        logger.debug("user registered with credentials username: {}, email: {}, passcode: {}".format(name, email, passcode))
        self.assertTrue(type(credid)==int)
        self.uname=email
        self.pas=passcode
    '''
    #
    def __auth(self):
        self.assertFalse(self.uname==None)
        self.assertFalse(self.pas==None)
        valid_cred = \
            base64.b64encode(bytes("{}:{}".format(self.uname, \
                                                  self.pas), \
                                   'utf-8')).decode("utf-8")
        return  valid_cred

    def test_get_balance(self):
        src = Client(self.app)
        balance=src.get_balance()
        print('|------------>balance: ', balance)
        self.assertEqual(balance[0], src.balance)
        self.assertEqual(unwrap_cur(balance[1]), unwrap_cur(src.currency_pref))

    def test_add_contact(self):
        src = Client(self.app)
        dest = Client(self.app)
        credid=src.add_contact(dest.email, dest.name)
        self.assertEqual(credid, dest.credid)
    def test_udapte_ledger(self):
        pass
    def test_make_transaction(self):
        src = Client(self.app)
        dest = Client(self.app)
        assert not src.email==dest.email or not src.passcode==dest.passcode
        amount=get_amount()
        old_balance=src.balance
        new_balance, trxs = src.make_transaction(dest.email, dest.name, amount)
        print("transaction made: ", trxs)
        self.assertEqual(new_balance, old_balance-(amount+FEE))

    '''
    def test_add_contact(self):
        ##############
        # first client
        ##############
        name_1 = get_name()
        email_1 = get_email()
        passcode_1 = get_rand_pass()
        bank_name_1=get_bank_name()
        branch_number_1=get_branch_number()
        account_number_1=get_account_number()
        name_reference_1=get_name_reference()
        register_payload_1={'name':name_1,\
                            'email': email_1,\
                            'passcode': passcode_1}
        bank_payload_1={'bank_name': bank_name_1,\
                        'branch_number': branch_number_1,\
                        'account_number': account_number_1,
                        'name_reference': name_reference_1}
        ##########################################
        # register first user and add bank account
        ##########################################
        res=self.app.post(REGISTER, data=json.dumps(register_payload_1))
        self.assertEqual(res.status_code, 201)
        print('res: ', res)
        response = res.json #json.loads(res.json)
        print('response: ', response)
        credid=response['cred_id']
        self.uname=email_1
        self.pas=passcode_1
        print('auth: ', str(self.__auth()))
        ###############################
        # register bank account
        ###############################
        res=self.app.post(ADD_BANK_ACCOUNT, \
                          data=json.dumps(bank_payload_1), \
                          headers={"Authorization": "Basic "+\
                                   self.__auth()})
        # second client (the destination, or recipient)
        name_2 = get_name()
        email_2 = get_email()
        passcode_2 = get_rand_pass()
        bank_name_2=get_bank_name()
        branch_number_2=get_branch_number()
        account_number_2=get_account_number()
        name_reference_2=get_name_reference()
        register_payload_2={'name':name_1,\
                            'email': email_1,\
                            'passcode': passcode_1}
        bank_payload_2={'bank_name': bank_name_1,\
                        'branch_number': branch_number_1,\
                        'account_number': account_number_1,\
                        'name_reference': name_reference_1}
        ##########################################
        # register first user and add bank account
        ##########################################
        res=self.app.post(REGISTER, data=json.dumps(register_payload_2))
        self.assertEqual(res.status_code, 201)
        print('res: ', res)
        response = res.json #json.loads(res.json)
        print('response: ', response)
        credid=response['cred_id']
        self.uname=email_2
        self.pas=passcode_2
        print('auth: ', str(self.__auth()))
        ###############################
        # register bank account
        ###############################
        res=self.app.post(ADD_BANK_ACCOUNT, \
                          data=json.dumps(bank_payload_2), \
                          headers={"Authorization": "Basic "+\
                                   self.__auth()})
        response=res.json
        print('response: ', response)
        self.assertEqual(res.status_code, 201)
        self.assertTrue(type(response['balance'])==float)
        ##############################
        ##############################
        # now add contact1 to contact2
        ##############################
        add_contact={'email':email_1}
        res=self.app.post(CONTACTS,\
                          data=json.dumps(add_contact),\
                          headers={"Authorization": "Basic "+\
                                   self.__auth()})
        response=res.json
        print('response: ', response)
        self.assertEqual(res.status_code, 201)
        credid=response['credid']
        self.assertTrue(type(credid)==int)
        print("credid: ", credid)
    '''
    def __get_dict(self, ret):
        res=ret.decode('utf8')#.replace('"', "'")
        return json.loads(res)
    def __rand_alphanum(self, L=9):
        passcode=''.join(rand.choice(string.ascii_uppercase+\
                                     string.ascii_lowercase+\
                                     string.digits)\
                         for _ in range(L))

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
            name_reference= self.faker.name() if name_reference==None else anem_reference
            payload={'bank_name':bank_name,
                     'branch_number':branch_number,
                     'account_number':account_number,
                     'name_reference':name_reference}
            res=requests.post(ADD_BANK_ACCOUNT_URL, \
                              data=json.dumps(payload))
            response = json.loads(res.text)
            scode=res.status_code
            #TODO support multiple accounts
            #create local client table for banking,
            #to insert balance, or each account.
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
        respose=ret.text#.decode('utf8')#.replace('"', "'")
        res = json.laods(response)
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
    def autotract(self):
        """Stochastic fake auto-tracting

        trade with randomly with maintained contacts with 0.5 probability for each, and 0.1 probability for all contacts goods, update balance, and goods for each contact
        """
        #update balance, and add new transactions
        MAX_TRACT_BALANCE=100000
        self.__update_ledger()
        contacts_df=db.gets.get_all_contacts()
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

if __name__=='__main__':
    unittest.main()
