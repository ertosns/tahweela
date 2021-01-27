import logging
import requests
import os
import random
from time import sleep

seed=int.from_bytes(os.urandom(2), 'big')
random.seed(seed)

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

logging.basicConfig(filename="utils.log", \
                    format='%(asctime)s %(message)s',\
                    filemode='w')
log=logging.getLogger()
log.setLevel(logging.DEBUG)

def exchangerate_rate(base, pref):
    site='https://api.exchangeratesapi.io/latest?base={}'.format(unwrap_cur(base))
    res=requests.get(site)
    try:
        response=res.json()
        assert res.status_code<300 , 'exchange currency failed'
        rate=response['rates'][unwrap_cur(pref)]
    except:
        log.critical('exchange rate fetch failed base: {}, pref: {}'. format(base, pref))
        rate=0
    return rate

def fixer_rate(base, pref):
    site='http://data.fixer.io/api/latest?access_key=9c87591ccfb9716f0850e500ceceef7a'
    res=requests.get(site)
    try:
        response=res.json()
        assert res.status_code<300 , 'exchange currency failed'
        base_rate=response['rates'][unwrap_cur(base)]
        pref_rate=response['rates'][unwrap_cur(pref)]
        rate=base_rate/pref_rate
    except:
        log.critical('fixer.io rate fetch failed base: {}, pref: {}'. format(base, pref))
        rate=0
    return rate

def exchange(base, pref):
    rate=0
    while rate==0:
        rate=exchangerate_rate(base, pref)
        if rate==0:
            rate=fixer_rate(base, pref)
        sleep(1)
        print("make sure there is internet connection!")
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

class PaymentGate(object):
    def __init__(self, bank_name, branch_number, account_number, name_reference):
        self.bank_name=bank_name
        self.branch_number=branch_number
        self.account_number=account_number
        self.name_reference=name_reference

    def __get_balance(self):
        return random.random()*MAX_BALANCE

    def authenticated(self):
        ''' contact the corresponding banking infrastructure server for authentication, and retrieve the balance
        '''
        self.base=EUR
        self.balance=self.__get_balance()
        return True
    def get_balance(self):
        return {'balance':self.balance, 'base':self.base}

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
