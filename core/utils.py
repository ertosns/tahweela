#import logging

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
FEE = 0.01 #this is the transaction fee in dollar
QUALITY_REDUCTION = 0.1 # this is the reduction in the quality of good per transaction
MAX_COST=1000000
MAX_GOODS=100

REGISTER="/api/v0.1/register"
LEDGER="/api/v0.1/ledger"
CONTACTS="/api/v0.1/contacts"
PURCHASE="/api/v0.1/purchase"
BALANCE="/api/v0.1/balance"

GOODS="/api/v0.1/goods"
GOODS_URL="http://localhost:5000/api/v0.1/goods"

CONTACTS_URL="http://localhost:5000/api/v0.1/contacts"
REGISTER_URL="http://localhost:5000/api/v0.1/register"
LEDGER_URL="http://localhost:5000/api/v0.1/ledger"
PURCHASE_URL="http://localhost:5000/api/v0.1/purchase"
BALANCE_URL="http://localhost:5000/api/v0.1/balance"
MAX_CRED_ID=9223372036854775807 #8bytes postgresql bigint max
MAX_BALANCE=MAX_COST*10
STOCHASTIC_TRADE_THRESHOLD=0.9
db_configs="dbname='demo'  user='tahweela' password='tahweela'"

#logging.basicConfig(filename="db.log", \
                    #format='%(asctime)s %(message)s', \
                    #filemode='w')
#db_log=logging.getLogger()
#db_log.setLevel(logging.DEBUG)
