import unittest
from core.queries.database import  database
import random
import os
import string
import datetime
from core.utils import TIMESTAMP_FORMAT, Currency, process_cur, EUR, USD, EGP, hash, get_credid, get_bank_name, get_branch_number, get_account_number, get_name_reference, get_name, get_email, get_balance, get_rand_pass, get_amount, PaymentGate, Client
from core.configs import db_configs

seed=int.from_bytes(os.urandom(2), "big")
random.seed(seed)
#
#db_configs="dbname='demo'  user='tahweela' password='tahweela'"
db=database(db_configs)
#
bank_name=get_bank_name()
branch_number=get_branch_number()
account_number=get_account_number()
name_reference=get_name_reference()
email=get_email()
name=get_name()
credid=get_credid(email)
balance=get_balance()
ADD_CURRENCY_LOCK=1
lock=ADD_CURRENCY_LOCK

class ServerDatabaseTest(unittest.TestCase):
    def test_currency(self):
        #db.init()
        #db.repeatable_read()
        #db.lock_advisory(lock)
        exchange=Currency(EUR)
        rate=exchange.rate
        if not db.exists.currency(EUR):
            db.inserts.add_currency(EUR, rate)
        self.assertEqual(rate, 1)
        #db.rollback(lock)

    def test_banking_byemail(self):
        #db.init()
        #db.repeatable_read()
        #db.lock_advisory(lock)
        exchange=Currency(EUR)
        rate=exchange.rate
        if not db.exists.currency(EUR):
            db.inserts.add_currency(EUR, rate)
        curr_id=db.gets.get_currency_id(EUR)
        db.inserts.add_client(name, email, curr_id)
        self.assertTrue(db.exists.account_byemail(email))
        cid=db.gets.get_client_id_byemail(email)
        self.assertTrue(db.exists.client_exists(cid))
        #db.rollback(lock)

    def test_banking_byname(self):
        exchange=Currency(EUR)
        rate=exchange.rate
        if not db.exists.currency(EUR):
            db.inserts.add_currency(EUR, rate)
        curr_id=db.gets.get_currency_id(EUR)
        passcode=get_rand_pass()
        email=get_email()
        name=get_name()
        db.inserts.add_client(name, email, curr_id)
        cid=db.gets.get_client_id_byemail(email)
        db.inserts.register(cid, passcode, credid)
        self.assertTrue(db.exists.account_byname(name, passcode))
        cid=db.gets.get_client_id_byname(name, passcode)
        self.assertTrue(db.exists.client_exists(cid))

    def test_bank_account_exist_by_cid(self):
        exchange=Currency(EUR)
        rate=exchange.rate
        if not db.exists.currency(EUR):
            db.inserts.add_currency(EUR, rate)
        curr_id=db.gets.get_currency_id(EUR)
        name=get_name()
        email=get_email()
        db.inserts.add_client(name, email, curr_id)
        cid=db.gets.get_client_id_byemail(email)
        self.assertFalse(db.exists.bank_account_bycid(cid))

    def test_client_exists(self):
        exchange=Currency(EUR)
        rate=exchange.rate
        if not db.exists.currency(EUR):
            db.inserts.add_currency(EUR, rate)
        curr_id=db.gets.get_currency_id(EUR)
        name=get_name()
        email=get_email()
        db.inserts.add_client(name, email, curr_id)
        cid=db.gets.get_client_id_byemail(email)
        self.assertTrue(db.exists.client_exists(cid))
    def test_credential_exists(self):
        exchange=Currency(EUR)
        rate=exchange.rate
        if not db.exists.currency(EUR):
            db.inserts.add_currency(EUR, rate)
        curr_id=db.gets.get_currency_id(EUR)
        name=get_name()
        email=get_email()
        passcode=get_rand_pass()
        credid=get_credid(email)
        db.inserts.add_client(name, email, curr_id)
        db.commit()
        cid=db.gets.get_client_id_byemail(email)
        db.commit()
        self.assertFalse(db.exists.credential_exists(0))
        db.inserts.register(cid, passcode, credid)
        cid=db.gets.get_client_id_byname(name, passcode)
        db.commit()
        self.assertTrue(db.exists.credential_exists(cid))

    def test_add_bank_account(self):
        exchange=Currency(EUR)
        rate=exchange.rate
        if not db.exists.currency(EUR):
            db.inserts.add_currency(EUR, rate)
        curr_id=db.gets.get_currency_id(EUR)
        passcode=get_rand_pass()
        email=get_email()
        credid=get_credid(email)
        banalce=get_balance()
        email=get_email()
        name=get_name()
        db.inserts.add_client(name, email, curr_id)
        cid=db.gets.get_client_id_byemail(email)
        db.inserts.register(cid, passcode, credid)
        #add_bank_addount
        bid=db.inserts.add_bank_account(cid, balance, bank_name, branch_number, account_number, name_reference, curr_id)
        self.assertTrue(db.exists.bank_account_bycid(cid))
    def test_bid_cid_conversion(self):
        """ bid_cid conversion testing

        convert, and cross-reference from client id, to bank id
        """
        exchange=Currency(EUR)
        rate=exchange.rate
        if not db.exists.currency(EUR):
            db.inserts.add_currency(EUR, rate)
        curr_id=db.gets.get_currency_id(EUR)
        passcode=get_rand_pass()
        email=get_email()
        credid=get_credid(email)
        banalce=get_balance()
        email=get_email()
        name=get_name()
        db.inserts.add_client(name, email, curr_id)
        cid=db.gets.get_client_id_byemail(email)
        db.inserts.register(cid, passcode, credid)
        #add_bank_addount
        bid=db.inserts.add_bank_account(cid, balance, bank_name, branch_number, account_number, name_reference, curr_id)
        cid_eq=db.gets.get_client_id(bid)
        bid_eq=db.gets.get_banking_id(cid_eq)
        self.assertEqual(cid_eq, cid)
        self.assertEqual(bid_eq, bid)

    def test_balance(self):
        exchange=Currency(EUR)
        rate=exchange.rate
        if not db.exists.currency(EUR):
            db.inserts.add_currency(EUR, rate)
        curr_id=db.gets.get_currency_id(EUR)
        passcode=get_rand_pass()
        email=get_email()
        credid=get_credid(email)
        banalce=get_balance()
        email=get_email()
        name=get_name()
        db.inserts.add_client(name, email, curr_id)
        cid=db.gets.get_client_id_byemail(email)
        db.inserts.register(cid, passcode, credid)
        #add_bank_addount
        bid=db.inserts.add_bank_account(cid, balance, bank_name, branch_number, account_number, name_reference, curr_id)
        bank_exists=db.exists.bank_account_bycid(cid)
        self.assertTrue(bank_exists)
        print('cid: ', cid)
        balance_cur=db.gets.get_balance_by_cid(cid)['balance']
        self.assertEqual(balance_cur, balance)
    def test_total_balance(self):
        c1 = Client(db)
        bank_name=get_bank_name()
        branch_number=get_branch_number()
        account_number=get_account_number()
        name_reference=get_name_reference()
        pg1=PaymentGate(bank_name,branch_number,account_number, name_reference)
        c1.add_pg(pg1)
        c1.add_bank_account(c1.cid, pg1.balance, bank_name, branch_number, account_number, name_reference, c1.curr_id)
        bank_name=get_bank_name()
        branch_number=get_branch_number()
        account_number=get_account_number()
        name_reference=get_name_reference()
        pg2=PaymentGate(bank_name,branch_number,account_number, name_reference)
        c1.add_pg(pg2)
        c1.add_bank_account(c1.cid, pg2.balance, bank_name, branch_number, account_number, name_reference, c1.curr_id)
        #
        bank_exists=db.exists.bank_account_bycid(c1.cid)
        self.assertTrue(bank_exists)
        #TODO get number of bank accounts associated with cid
        credid=db.gets.cid2credid(c1.cid)
        total_balance=db.gets.get_total_balance_by_credid(credid)['balance']
        self.assertEqual(total_balance, c1.total_currency())
    def test_banking_ids(self):
        c1 = Client(db)
        bank_name=get_bank_name()
        branch_number=get_branch_number()
        account_number=get_account_number()
        name_reference=get_name_reference()
        pg1=PaymentGate(bank_name,branch_number,account_number, name_reference)
        c1.add_pg(pg1)
        c1.add_bank_account(c1.cid, pg1.balance, bank_name, branch_number, account_number, name_reference, c1.curr_id)
        bid1=db.gets.get_banking_id(c1.cid)
        bank_name=get_bank_name()
        branch_number=get_branch_number()
        account_number=get_account_number()
        name_reference=get_name_reference()
        pg2=PaymentGate(bank_name,branch_number,account_number, name_reference)
        c1.add_pg(pg2)
        c1.add_bank_account(c1.cid, pg2.balance, bank_name, branch_number, account_number, name_reference, c1.curr_id)
        bid2=db.gets.get_banking_id(c1.cid)
        #
        bids=db.gets.get_banking_ids(c1.cid)
        print('bids: ', bids)
        self.assertEqual(bid1, bids[0])
        #note this will fail since bid1=bid2, because get_banking_id is limited by 1
        #self.assertEqual(bid2, bids[1])
    def test_update_balance(self):
        exchange=Currency(EUR)
        rate=exchange.rate
        if not db.exists.currency(EUR):
            db.inserts.add_currency(EUR, rate)
        curr_id=db.gets.get_currency_id(EUR)
        passcode=get_rand_pass()
        email=get_email()
        credid=get_credid(email)
        balance=get_balance()
        email=get_email()
        name=get_name()
        db.inserts.add_client(name, email, curr_id)
        db.commit()
        cid=db.gets.get_client_id_byemail(email)
        db.inserts.register(cid, passcode, credid)
        db.commit()
        #add_bank_addount
        bid=db.inserts.add_bank_account(cid, balance, bank_name, branch_number, account_number, name_reference, curr_id)
        db.commit()
        db.updates.update_account(cid, 0)
        balance_cur=db.gets.get_balance_by_cid(cid)['balance']
        self.assertEqual(balance_cur, 0)
    #TODO (fix) fails
    def test_credid2cid(self):
        exchange=Currency(EUR)
        rate=exchange.rate
        if not db.exists.currency(EUR):
            db.inserts.add_currency(EUR, rate)
        curr_id=db.gets.get_currency_id(EUR)
        passcode=get_rand_pass()
        email=get_email()
        credid=get_credid(email)
        # add new client
        db.inserts.add_client(name, email, curr_id)
        cid=db.gets.get_client_id_byemail(email)
        # register client's credentials
        db.inserts.register(cid, passcode, credid)
        # credid2cid conversion
        cid_eq=db.gets.credid2cid(credid)
        self.assertEqual(cid, cid_eq)
        credid_eq=db.gets.cid2credid(cid)
        self.assertEqual(credid, credid_eq)

    def test_password(self):
        exchange=Currency(EUR)
        rate=exchange.rate
        if not db.exists.currency(EUR):
            db.inserts.add_currency(EUR, rate)
        curr_id=db.gets.get_currency_id(EUR)
        passcode=get_rand_pass()
        email=get_email()
        credid=get_credid(email)
        banalce=get_balance()
        email=get_email()
        name=get_name()
        db.inserts.add_client(name, email, curr_id)
        cid=db.gets.get_client_id_byemail(email)
        db.inserts.register(cid, passcode, credid)
        #add_bank_addount
        bid=db.inserts.add_bank_account(cid, balance, bank_name, branch_number, account_number, name_reference, curr_id)
        passcode_eq=db.gets.get_password(credid)
        self.assertEqual(hash(passcode), passcode_eq)

    def test_transaction(self):
        """ create two clients, client_1, client_2

        procedure:
        - client_1 sends 10k to client_2
        - client_1 sends 20k to client_2
        - client_2 sends 5k to client_1
        - transaction sum 35k sent/received
        """
        exchange=Currency(EUR)
        rate=exchange.rate
        if not db.exists.currency(EUR):
            db.inserts.add_currency(EUR, rate)
        curr_id=db.gets.get_currency_id(EUR)
        c1_name=get_name()
        c1_email=get_email()
        c1_passcode=get_rand_pass()
        c1_credid=get_credid(c1_email)
        c1_bank_name=get_bank_name()
        c1_branch_number=get_branch_number()
        c1_account_number=get_account_number()
        c1_name_reference=get_name_reference()
        c1_balance=get_balance()
        db.inserts.add_client(c1_name, c1_email, curr_id)
        db.commit()
        c1_cid=db.gets.get_client_id_byemail(c1_email)
        db.inserts.register(c1_cid, c1_passcode, c1_credid)
        db.commit()
        db.inserts.add_bank_account(c1_cid, c1_balance, c1_bank_name, c1_branch_number, c1_account_number, c1_name_reference, curr_id)
        db.commit()
        #
        c2_name=get_name()
        c2_email=get_email()
        c2_passcode=get_rand_pass()
        c2_credid=get_credid(c2_email)
        c2_bank_name=get_bank_name()
        c2_branch_number=get_branch_number()
        c2_account_number=get_account_number()
        c2_name_reference=get_name_reference()
        c2_balance=get_balance()
        db.inserts.add_client(c2_name, c2_email, curr_id)
        db.commit()
        c2_cid=db.gets.get_client_id_byemail(c2_email)
        db.inserts.register(c2_cid, c2_passcode, c2_credid)
        db.commit()
        db.inserts.add_bank_account(c2_cid, c2_balance, c2_bank_name, c2_branch_number, c2_account_number, c2_name_reference, curr_id)
        db.commit()
        #
        ################
        # transactions
        ################
        costs=[10000, 20000, 5000]
        trx_st_0=datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
        db.inserts.insert_trx(c2_credid, c1_credid, costs[0], curr_id, 'transaction1')
        db.commit()
        trx_st_1=datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
        db.inserts.insert_trx(c2_credid, c1_credid, costs[1], curr_id, 'transaction2')
        db.commit()
        trx_st_2=datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
        db.inserts.insert_trx(c1_credid, c2_credid, costs[2], curr_id, 'transaction3')
        db.commit()
        trx_st_3=datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
        ##################
        # validation test
        ##################
        #epoch 1
        c1_trx_sum_0=db.gets.get_transactions_sum(c1_credid, trx_st_0)
        db.commit()
        self.assertEqual(sum(costs), c1_trx_sum_0)
        #epoch 2
        c1_trx_sum_1=db.gets.get_transactions_sum(c1_credid, trx_st_1)
        db.commit()
        self.assertEqual(sum(costs[1:]), c1_trx_sum_1)
        #epoch 3
        c1_trx_sum_2=db.gets.get_transactions_sum(c1_credid, trx_st_2)
        db.commit()
        self.assertEqual(sum(costs[2:]), c1_trx_sum_2)
        #######################
        # viola tahweela database works!
        #######################
if __name__=='__main__':
    unittest.main()
