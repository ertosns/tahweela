import logging
import requests
import os
import random
from time import sleep
import hashlib
import base64
import datetime
from faker import Faker
import string

seed=int.from_bytes(os.urandom(2), "big")
random.seed(seed)
faker=Faker(seed)

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
FEE = 0.01 #this is fixed transaction fee in euros
QUALITY_REDUCTION = 0.1 # this is the reduction in the quality of good per transaction
MAX_COST=1000000
MAX_GOODS=100

REGISTER="/api/v0.1/register"
LEDGER="/api/v0.1/ledger"
CONTACTS="/api/v0.1/contacts"
PURCHASE="/api/v0.1/purchase"

GOODS="/api/v0.1/goods"
GOODS_URL="http://localhost:5000/api/v0.1/goods"

BALANCE_URL="http://localhost:5000/api/v0.1/balance"
BALANCE="/api/v0.1/balance"

TOTAL_BALANCE_URL="http://localhost:5000/api/v0.1/totalbalance"
TOTAL_BALANCE="/api/v0.1/totalbalance"

CURRENCY_URL="http://localhost:5000/api/v0.1/currency"
CURRENCY="/api/v0.1/currency"

CONTACTS_URL="http://localhost:5000/api/v0.1/contacts"
REGISTER_URL="http://localhost:5000/api/v0.1/register"
LEDGER_URL="http://localhost:5000/api/v0.1/ledger"
PURCHASE_URL="http://localhost:5000/api/v0.1/purchase"

ADD_BANK_ACCOUNT_URL="http://localhost:5000/api/v0.1/addbank"
ADD_BANK_ACCOUNT="/api/v0.1/addbank"
TRANSACTION_URL="http://localhost:5000/api/v0.1/transaction"
TRANSACTION="/api/v0.1/transaction"

MAX_CRED_ID=9223372036854775807 #8bytes postgresql bigint max
MAX_BALANCE=MAX_COST*10
STOCHASTIC_TRADE_THRESHOLD=0.9
DAILY_LIMIT_EGP=10000
WEEKLY_LIMIT_EGP=50000

EUR='EUR'
EGP='EGP'
USD='USD'

db_configs="dbname='demo'  user='tahweela' password='tahweela'"

logging.basicConfig(filename="general.log", \
                    format='%(asctime)s %(message)s',\
                    filemode='w')
log=logging.getLogger()
log.setLevel(logging.DEBUG)

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
def get_rand_pass(L=9):
    passcode=''.join(random.choice(string.ascii_uppercase+\
                                 string.ascii_lowercase+\
                                 string.digits)\
                     for _ in range(L))
    return passcode


def daily_limit(pref=EUR):
    """ daily transaction limits

    """
    currency = Currency(pref, EGP)
    return currency.exchange(DAILY_LIMIT_EGP)

def weekly_limit(pref=EUR):
    """ daily transaction limits

    """
    currency = Currency(pref, EGP)
    return currency.exchange(WEEKLY_LIMIT_EGP)

def process_cur(cur):
    cur.strip("'")
    cur.replace("'", '')
    return '\'{}\''.format(cur)
def unwrap_cur(cur):
    return cur.replace("'", '')

def get_amount():
    return 3333*random.random()

#TODO HOW TO MAKE SURE THAT CREDID IS UNIQUE?
# brute force, keep trying new values that does exist,
# is the simplest, otherwise use conguential generator
def get_credid(word):
    #return int(3333333333333*random.random())
    return hash(word)

#TODO (fix) it seams that is_email isn't strong enough, it fails for some emails, need more robust regex
def is_email(email):
  return bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", email))

def hash(word):
    hf=hashlib.sha256()
    hf.update(bytes(word, 'utf-8'))
    return base64.b64encode(hf.digest()).decode('utf-8')

def exchangerate_rate(base, pref):
    site='https://api.exchangeratesapi.io/latest?base={}'.format(unwrap_cur(base))
    res=requests.get(site)
    if base==pref:
        return 1
    try:
        response=res.json()
        assert res.status_code<300 , 'exchange currency failed'
        rate=response['rates'][unwrap_cur(pref)]
    except Exception as error:
        print('exchange server failed, error:{} '.format(error))
        log.critical('exchange rate fetch failed base: {}, pref: {}'. format(base, pref))
        rate=0
    return rate

def fixer_rate(base, pref):
    site='http://data.fixer.io/api/latest?access_key=9c87591ccfb9716f0850e500ceceef7a'
    res=requests.get(site)
    if base==pref:
        return 1
    try:
        response=res.json()
        assert res.status_code<300 , 'exchange currency failed'
        base_rate=response['rates'][unwrap_cur(base)]
        pref_rate=response['rates'][unwrap_cur(pref)]
        rate=base_rate/pref_rate
    except Exception as error:
        print('exchange server failed, error:{} '.format(error))
        log.critical('fixer.io rate fetch failed base: {}, pref: {}'. format(base, pref))
        rate=0
    return rate

def exchange(base, pref):
    rate=0
    while rate==0:
        rate=exchangerate_rate(unwrap_cur(base), unwrap_cur(pref))
        if rate==0:
            rate=fixer_rate(unwrap_cur(base), unwrap_cur(pref))
            if rate==0:
                print("make sure there is internet connection exchange server connection fails!")
                sleep(1)
    return rate

class Currency(object):
    def __init__(self, preference, base=EUR):
        self.base=base
        self.pref=preference
        self.rate = exchange(self.base, self.pref)
        log.info("exchange with rate {}".format(self.rate))
        if self.rate==0:
            log.critical("currence base {}, pref {}".format(self.base, self.pref))

    def valid(self):
        """ wither the given preference currency is available
        """
        return not self.rate==0
    def exchange(self, amount=1):
        print("making exchange with rate {}".format(self.rate))

        return amount*self.rate
    def exchange_back(self, amount=1):
        print("making back exchange with rate {}".format(self.rate))
        return amount/self.rate

class Client(object):
    def __init__(self, db, name=None, email=None, passcode=None, base=None):
        self.db = db
        self.name=get_name() if name==None else name
        self.passcode=get_rand_pass() if passcode==None else passcode
        self.email=get_email() if email==None else email
        self.base=EUR if base==None else base
        self.balance=get_amount()
        #get balance self.balance preference self.b
        exchange=Currency(self.base)
        rate=exchange.rate
        if not db.exists.currency(self.base):
            db.inserts.add_currency(EUR, rate)
        self.curr_id=db.gets.get_currency_id(EUR)
        db.inserts.add_client(self.name, self.email, self.curr_id)
        self.cid=db.gets.get_client_id_byemail(self.email)
        db.inserts.register(self.cid, self.passcode, hash(self.email))
        self.pgs=[]
    def add_bank_account(self, cid, balance, bank_name, branch_number, account_number, name_reference, curr_id):
        self.bid=self.db.inserts.add_bank_account(cid, balance, bank_name, branch_number, account_number, name_reference, curr_id)
    def add_pg(self, pg):
        self.pgs.append(pg)
    def total_currency(self):
        sum=0
        for pg in self.pgs:
            sum+=pg.balance
        return sum

class PaymentGate(object):
    def __init__(self, bank_name=None, branch_number=None, account_number=None, name_reference=None):
        self.bank_name=get_bank_name() if bank_name==None else bank_name
        self.branch_number=get_branch_number() if branch_number==None else branch_number
        self.account_number=get_account_number() if account_number==None else account_number
        self.name_reference=name_reference() if name_reference==None else name_reference
        #self.base=faker.currency()
        self.base=EUR
        self.balance=random.random()*MAX_BALANCE

    def authenticated(self):
        ''' contact the corresponding banking infrastructure server for authentication, and retrieve the balance
        '''
        return True

    def get_balance(self):
        return {'balance':self.balance, 'base':self.base}
    def get_daily_limit(self):
        return daily_limit()
    def get_weekly_limit(self):
        return weekly_limit()
