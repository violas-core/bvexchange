from grpc import insecure_channel
import requests
import time
from canoser import Uint64
from canoser.util import  bytes_to_hex
import os
import json

from libra.account import Account
from libra.account_address import Address
from libra.account_config import AccountConfig
from libra.transaction import Transaction, RawTransaction, SignedTransaction, Script, TransactionPayload, Module
from libra.trusted_peers import ConsensusPeersConfig
from libra.transaction import (
    Transaction, RawTransaction, SignedTransaction, Script, TransactionPayload, TransactionInfo)
from libra.trusted_peers import ConsensusPeersConfig
from libra.ledger_info import LedgerInfo
from libra.get_with_proof import verify
from libra.event import ContractEvent

from libra.proto.admission_control_pb2 import SubmitTransactionRequest, AdmissionControlStatusCode
from libra.proto.admission_control_pb2_grpc import AdmissionControlStub
from libra.proto.get_with_proof_pb2 import UpdateToLatestLedgerRequest
from libra.event import ContractEvent
from libra.transaction.transaction_info import TransactionInfo

from libra.violas_transaction import ViolasAccountBlob, ViolasAccountResource, ViolasAccountState, ViolasSignedTransaction,ViolasContractEvent, ViolasTransactionInfo

NETWORKS = {
    'testnet':{
        'host': "ac.testnet.libra.org",
        'port': 8000,
        'faucet_host': "faucet.testnet.libra.org"
    }
}

class LibraError(Exception):
    pass

class AccountError(LibraError):
    pass

class TransactionNotExistError(LibraError):
    pass

class TransactionIllegalError(LibraError):
    pass

class TransactionTimeoutError(LibraError):
    pass

class LibraNetError(LibraError):
    pass

class Client:
    def __init__(self, network="testnet", validator_set_file=None, faucet_file=None):
        if network == "mainnet":
            raise LibraNetError("Mainnet is not supported currently")
        if network != "testnet":
            raise LibraNetError(f"Unknown network: {network}")
        self.host = NETWORKS[network]['host']
        self.port = NETWORKS[network]['port']
        try:
            tests = os.environ['TESTNET_LOCAL'].split(";")
            self.host = tests[0]
            self.port = int(tests[1])
            validator_set_file = tests[2]
        except KeyError:
            pass
        self.do_init(validator_set_file, faucet_file)

    def do_init(self, validator_set_file=None, faucet_file=None):
        self.init_validators(validator_set_file)
        self.init_grpc()
        self.init_faucet_account(faucet_file)
        self.client_known_version = 0
        self.verbose = True

    def init_grpc(self):
        #TODO: should check under ipv6, add [] around ipv6 host
        self.channel = insecure_channel(f"{self.host}:{self.port}")
        self.stub = AdmissionControlStub(self.channel)

    def init_faucet_account(self, faucet_file):
        if self.is_testnet():
            self.faucet_host = NETWORKS['testnet']['faucet_host']
            self.faucet_account = None
        else:
            self.faucet_account = Account.gen_faucet_account(faucet_file)

    def is_testnet(self):
        return self.host == NETWORKS['testnet']['host']

    def init_validators(self, validator_set_file):
        # if self.is_testnet() and validator_set_file is None:
        #     validator_set_file = ConsensusPeersConfig.testnet_file_path()
        if validator_set_file is None:
            validator_set_file = ConsensusPeersConfig.testnet_file_path()
        self.validator_verifier = ConsensusPeersConfig.parse(validator_set_file)

    @classmethod
    def new(cls, host, port, validator_set_file, faucet_file=None):
        if port == 0:
            try:
                tests = os.environ['TESTNET_LOCAL'].split(";")
                host = tests[0]
                port = int(tests[1])
                validator_set_file = tests[2]
            except KeyError:
                port = 8000
        ret = cls.__new__(cls)
        ret.host = host
        if isinstance(port, str):
            port = int(port)
        if port <=0 or port > 65535:
            raise LibraNetError("port must be between 1 and 65535")
        ret.port = port
        ret.do_init(validator_set_file, faucet_file)
        return ret

    #Not exist raise AccountError
    def get_account_blob(self, address) -> ViolasAccountBlob:
        address = Address.normalize_to_bytes(address)
        request = UpdateToLatestLedgerRequest()
        item = request.requested_items.add()
        item.get_account_state_request.address = address
        resp = self.update_to_latest_ledger(request)
        blob = resp.response_items[0].get_account_state_response.account_state_with_proof.blob
        version = resp.ledger_info_with_sigs.ledger_info.version
        try:
            return ViolasAccountBlob(blob, version)
        except OSError:
            raise AccountError

    #Not exist raise AccountError
    def get_account_state(self, address) -> ViolasAccountState:
        blob = self.get_account_blob(address)
        return blob.blob
        # if len(blob.__str__()) == 0:
        #     #TODO: bad smell
        #     raise AccountError("Account state blob is empty.")
        # return AccountState.deserialize(blob.blob)

    #Not exist raise AccountError
    def get_account_resource(self, address) -> ViolasAccountResource:
            state = self.get_account_state(address)
            return state.account_resource

    def get_sequence_number(self, address):
        state = self.get_account_resource(address)
        return state.sequence_number

    def get_balance(self, address):
        try:
            state = self.get_account_resource(address)
            return state.balance
        except:
            return 0

    def update_to_latest_ledger(self, request):
        request.client_known_version = self.client_known_version
        resp = self.stub.UpdateToLatestLedger(request)
        #verify(self.validator_verifier, request, resp)
        #TODO:need update to latest proof, bitmap is removed.
        self.client_known_version = resp.ledger_info_with_sigs.ledger_info.version
        self.latest_time = resp.ledger_info_with_sigs.ledger_info.timestamp_usecs
        return resp

    def get_latest_ledger_info(self):
        request = UpdateToLatestLedgerRequest()
        resp = self.update_to_latest_ledger(request)
        return resp.ledger_info_with_sigs.ledger_info

    def _get_time_diff(self):
        from datetime import datetime
        info = self.get_latest_ledger_info()
        localtime = datetime.now().timestamp()
        return localtime - info.timestamp_usecs / 1000_000

    def get_latest_transaction_version(self):
        return self.get_latest_ledger_info().version

    def _get_txs(self, start_version, limit=1, fetch_events=False):
        start_version = Uint64.int_safe(start_version)
        limit = Uint64.int_safe(limit)
        if limit == 0:
            raise ValueError(f"limit:{limit} is invalid.")
        request = UpdateToLatestLedgerRequest()
        item = request.requested_items.add()
        item.get_transactions_request.start_version = start_version
        item.get_transactions_request.limit = limit
        item.get_transactions_request.fetch_events = fetch_events
        return (request, self.update_to_latest_ledger(request))

    #Not exist raise TransactionError
    def get_transactions_proto(self, start_version, limit=1, fetch_events=False):
        request, resp = self._get_txs(start_version, limit, fetch_events)
        txnp = resp.response_items[0].get_transactions_response.txn_list_with_proof
        if txnp.first_transaction_version.value == 0 and start_version:
            raise TransactionNotExistError
        assert txnp.first_transaction_version.value == start_version
        return (txnp.transactions, txnp.events_for_versions, txnp.proof.transaction_infos)

    def get_transactions(self, start_version, limit=1, fetch_event=False):
        try:
            transactions, events, infos = self.get_transactions_proto(start_version, limit, True)
        except TransactionNotExistError:
            return []
        txs = [Transaction.deserialize(x.transaction).value for x in transactions]
        infos = [TransactionInfo.from_proto(info) for info in infos ]
        if fetch_event:
            return [ ViolasSignedTransaction(tx, start_version+n, info, [ContractEvent.from_proto(e) for e in event_list.events]) for n, (tx, info, event_list) in enumerate(zip(txs, infos, events.events_for_version))]
        return [ ViolasSignedTransaction(tx, start_version+n, info) for n, (tx, info) in enumerate(zip(txs, infos))]

    def get_transaction(self, start_version, fetch_event=False):
        txs =  self.get_transactions(start_version, 1, fetch_event)
        if not len(txs):
            raise TransactionNotExistError
        return txs[0]

    def get_transaction_type(self, start_version):
        return self.get_transaction(start_version).raw_txn.type

    def get_account_transaction_type(self, address, sequence_number):
        return self.get_account_transaction(address, sequence_number).raw_txn.type

    def get_account_transaction_proto(self, address, sequence_number, fetch_event=False):
        address = Address.normalize_to_bytes(address)
        request = UpdateToLatestLedgerRequest()
        item = request.requested_items.add()
        itemreq = item.get_account_transaction_by_sequence_number_request
        itemreq.account = address
        itemreq.sequence_number = sequence_number
        itemreq.fetch_events = fetch_event
        resp = self.update_to_latest_ledger(request)
        usecs = resp.ledger_info_with_sigs.ledger_info.timestamp_usecs
        transaction = resp.response_items[0].get_account_transaction_by_sequence_number_response
        return (transaction.transaction_with_proof, usecs)

    #Not exist raise AcccountError
    def get_account_transaction(self, address, sequence_number, fetch_event=False):
        if fetch_event:
            version = self.get_transaction_version(address, sequence_number)
            return self.get_transaction(version, True)
        signed_transaction_with_proof, _ = self.get_account_transaction_proto(address, sequence_number, True)
        if len(signed_transaction_with_proof.transaction.transaction) == 0:
            raise TransactionNotExistError
        info = TransactionInfo.from_proto(signed_transaction_with_proof.proof.transaction_info)
        return ViolasSignedTransaction(Transaction.deserialize(signed_transaction_with_proof.transaction.transaction).value, signed_transaction_with_proof.version, info)

    #Not exist raise TransactionError
    def get_transaction_info(self, start_version):
        return self.get_transaction(start_version).get_info()

    #Not exist raise AcccountError
    def get_account_transaction_info(self, address, sequence_number):
        return  self.get_account_transaction(address, sequence_number).get_info()

    #Not exist raise AcccountError
    def get_transaction_version(self, address, sequence_number):
        return self.get_account_transaction(address, sequence_number).version

    def mint_coins(self, address, micro_libra, is_blocking=False):
        if self.faucet_account:
            tx = self.mint_coins_with_faucet_account(address, micro_libra, is_blocking)
            return tx.raw_txn.sequence_number
        else:
            return self.mint_coins_with_faucet_service(address, micro_libra, is_blocking)

    def mint_coins_with_faucet_account(self, receiver_address, micro_libra, is_blocking=False):
        script = Script.gen_mint_script(receiver_address, micro_libra)
        payload = TransactionPayload('Script', script)
        return self.submit_payload(self.faucet_account, payload, is_blocking=is_blocking)

    def mint_coins_with_faucet_service(self, receiver, micro_libra, is_blocking=False):
        url = "http://{}?amount={}&address={}".format(self.faucet_host, micro_libra, receiver)
        resp = requests.post(url)
        if resp.status_code != 200:
            raise IOError(
                "Failed to send request to faucet service: {}".format(self.faucet_host)
            )
        sequence_number = Uint64.int_safe(resp.text) - 1
        if is_blocking:
            self.wait_for_transaction(AccountConfig.association_address(), sequence_number)
        return sequence_number

    #Not wait raise TransactionTimeoutError
    def wait_for_transaction(self, address, sequence_number):
        max_iterations = 50
        if self.verbose:
            print("waiting", flush=True)
        version = None
        while max_iterations > 0:
            time.sleep(0.1)
            max_iterations -= 1
            if version is None:
                try:
                    version = self.get_transaction_version(address, sequence_number)
                except TransactionNotExistError:
                    if self.verbose:
                        print(".", end='', flush=True)
                    continue
            try:
                tx = self.get_transaction(version, True)
                if len(tx.events):
                    if self.verbose:
                        print("transaction is stored!")
                    return True
                else:
                    if self.verbose:
                        print("no events emitted")
                    return False
            except TransactionNotExistError:
                if self.verbose:
                    print(".", end='', flush=True)
                continue
        raise TransactionTimeoutError("wait_for_transaction timeout.")

    def transfer_coin(self, sender_account, receiver_address, micro_libra,
        max_gas=140_000, unit_price=0, is_blocking=False, txn_expiration=100):
        script = Script.gen_transfer_script(receiver_address,micro_libra)
        payload = TransactionPayload('Script', script)
        return self.submit_payload(sender_account, payload, max_gas, unit_price,
            is_blocking, txn_expiration)

    def create_account(self, sender_account, fresh_address, is_blocking=True):
        script = Script.gen_create_account_script(fresh_address)
        payload = TransactionPayload('Script', script)
        return self.submit_payload(sender_account, payload, is_blocking=is_blocking)

    def rotate_authentication_key(self, sender_account, public_key, is_blocking=True):
        script = Script.gen_rotate_auth_key_script(public_key)
        payload = TransactionPayload('Script', script)
        return self.submit_payload(sender_account, payload, is_blocking=is_blocking)

    def gen_raw_signed_transaction(self, sender_account, receiver_address, micro_libra,
                                   max_gas=140_000, unit_price=0, txn_expiration=100):
        script = Script.gen_transfer_script(receiver_address, micro_libra)
        payload = TransactionPayload('Script', script)

        sequence_number = self.get_sequence_number(sender_account.address)
        raw_tx = RawTransaction.new_tx(sender_account.address, sequence_number,
                                       payload, max_gas, unit_price, txn_expiration)
        signed_txn = SignedTransaction.gen_from_raw_txn(raw_tx, sender_account)
        return signed_txn.serialize().hex()

    #not valid raise TransactionError
    def submit_signed_txn(self,signed_txn, is_blocking=False):
        request = SubmitTransactionRequest()
        request.transaction.txn_bytes = bytes.fromhex(signed_txn)
        if is_blocking:
            return self.submit_transaction(request, SignedTransaction.deserialize(bytes.fromhex(signed_txn)), is_blocking=True)
        return self.submit_transaction(request, None, is_blocking)

    #not valid raise TransactionError
    def submit_payload(self, sender_account, payload,
        max_gas=140_000, unit_price=0, is_blocking=False, txn_expiration=100):
        sequence_number = self.get_sequence_number(sender_account.address)
        #TODO: cache sequence_number
        raw_tx = RawTransaction.new_tx(sender_account.address, sequence_number,
            payload, max_gas, unit_price, txn_expiration)
        signed_txn = SignedTransaction.gen_from_raw_txn(raw_tx, sender_account)
        request = SubmitTransactionRequest()
        request.transaction.txn_bytes = signed_txn.serialize()
        self.submit_transaction(request, raw_tx, is_blocking)
        return signed_txn

    def submit_transaction(self, request, raw_tx, is_blocking=False):
        resp = self.submit_transaction_non_block(request)
        if is_blocking:
            address = bytes(raw_tx.sender)
            sequence_number = raw_tx.sequence_number
            self.wait_for_transaction(address, sequence_number)
        return resp

    #not valid raise TransactionError or
    def submit_transaction_non_block(self, request):
        resp = self.stub.SubmitTransaction(request)
        status = resp.WhichOneof('status')
        if status == 'ac_status':
            if resp.ac_status.code == AdmissionControlStatusCode.Accepted:
                return resp
            else:
                raise TransactionIllegalError(f"Status code: {resp.ac_status.code}")
        elif status == 'vm_status':
            raise TransactionIllegalError(resp.vm_status.__str__())
        elif status == 'mempool_status':
            raise TransactionIllegalError(resp.mempool_status.__str__())
        else:
            raise TransactionIllegalError(f"Unknown Error: {resp}")
        raise LibraNetError("unreacheable")

    # Returns events specified by `access_path` with sequence number in range designated by
    # `start_seq_num`, `ascending` and `limit`. If ascending is true this query will return up to
    # `limit` events that were emitted after `start_event_seq_num`. Otherwise it will return up to
    # `limit` events in the reverse order. Both cases are inclusive.
    def get_events(self, address, path, start_sequence_number, ascending=True, limit=1):
        address = Address.normalize_to_bytes(address)
        request = UpdateToLatestLedgerRequest()
        item = request.requested_items.add()
        item.get_events_by_event_access_path_request.access_path.address = address
        item.get_events_by_event_access_path_request.access_path.path = path
        item.get_events_by_event_access_path_request.start_event_seq_num = start_sequence_number
        item.get_events_by_event_access_path_request.ascending = ascending
        item.get_events_by_event_access_path_request.limit = limit
        resp = self.update_to_latest_ledger(request)
        return resp.response_items[0].get_events_by_event_access_path_response.events_with_proof

    def get_events_sent(self, address, start_sequence_number, ascending=True, limit=1):
        path = AccountConfig.account_sent_event_path()
        efs =  self.get_events(address, path, start_sequence_number, ascending, limit)
        return [ContractEvent.from_proto(ef.event) for ef in efs]

    def get_events_received(self, address, start_sequence_number, ascending=True, limit=1):
        path = AccountConfig.account_received_event_path()
        efs =  self.get_events(address, path, start_sequence_number, ascending, limit)
        return [ ContractEvent.from_proto(ef.event) for ef in efs]

    def get_latest_events_sent(self, address, limit=1):
        return self.get_events_sent(address, 2**64-1, False, limit)[0]

    def get_latest_events_received(self, address, limit=1):
        return self.get_events_received(address, 2**64-1, False, limit)[0]

    def get_tx_events(self, tx_version):
        _, events_for_version, _ = self.get_transactions_proto(tx_version, fetch_events=True)
        return [ ViolasContractEvent(ContractEvent.from_proto(e)) for e in events_for_version.events_for_version[0].events]

    def get_account_event(self, address, sequence_number):
        try:
            return self.get_tx_events(self.get_transaction_version(address, sequence_number))
        except TransactionNotExistError:
            raise AccountError

    def violas_publish(self,sender_account, is_blocking = False):
        module = Module.gen_violas_publish_module(sender_account.address)
        payload = TransactionPayload('Module',module)
        return self.submit_payload(sender_account, payload, is_blocking=is_blocking)

    def violas_init(self,sender_account, module_address, is_blocking = False):
        script = Script.gen_violas_init_script(module_address)
        payload = TransactionPayload('Script', script)
        return self.submit_payload(sender_account, payload, is_blocking=is_blocking)

    def violas_owner_init(self, sender_account, data=None, is_blocking=False):
        if data is None:
            data = ""
        else:
            data = bytes(data, encoding="utf8")
        script = Script.gen_violas_owner_init_script(sender_account.address, data)
        payload = TransactionPayload('Script', script)
        return self.submit_payload(sender_account, payload, is_blocking=is_blocking)

    def violas_mint_coin(self, receiver_address, micro_violas, sender_account, is_blocking=False):
        script = Script.gen_violas_mint_script(receiver_address, micro_violas, sender_account.address)
        payload = TransactionPayload('Script', script)
        return self.submit_payload(sender_account, payload, is_blocking=is_blocking)

    def violas_transfer_coin(self, sender_account, receiver_address, micro_libra, module_address, data=None,
        max_gas=140_000, unit_price=0, is_blocking=False, txn_expiration=100):
        if data is None:
            script = Script.gen_violas_transfer_script(receiver_address,micro_libra,module_address)
            payload = TransactionPayload('Script', script)
            return self.submit_payload(sender_account, payload, max_gas, unit_price,
                is_blocking, txn_expiration)
        else:
            data = bytes(data, encoding="utf8")
            script = Script.gen_violas_peer_to_peer_transfer_with_data_script(receiver_address, micro_libra, module_address, data)
            payload = TransactionPayload('Script', script)
            return self.submit_payload(sender_account, payload, max_gas, unit_price,
                is_blocking, txn_expiration)

    # flag 0：提交稳定币换平台币的订单, 1:提交平台币换稳定币的订单
    def violas_make_order(self, sender_account, module_address, order_amount, pick_amount, source_is_vtoken=0,
        max_gas=140_000, unit_price=0, is_blocking=False, txn_expiration=100):
        script = Script.gen_violas_order_script(module_address, order_amount, pick_amount, source_is_vtoken)
        payload = TransactionPayload('Script', script)
        return self.submit_payload(sender_account, payload, max_gas, unit_price, is_blocking, txn_expiration)

    def violas_pick_order(self, sender_account, module_address, order_address, order_amount, pick_amount, source_is_vtoken=0,
        max_gas = 140_000, unit_price = 0, is_blocking = False, txn_expiration = 100):
        script = Script.gen_violas_pick_script(module_address, order_address, order_amount, pick_amount, source_is_vtoken)
        payload = TransactionPayload('Script', script)
        return self.submit_payload(sender_account, payload, max_gas, unit_price,
                                   is_blocking, txn_expiration)

    def violas_withdraw_order(self, sender_account, module_address,
        max_gas=140_000, unit_price=0, is_blocking=False, txn_expiration=100):
        script = Script.gen_violas_withdrawal_script(module_address)
        payload = TransactionPayload('Script', script)
        return self.submit_payload(sender_account, payload, max_gas, unit_price,
                                   is_blocking, txn_expiration)

    def violas_get_balance(self,account_address,module_address):
        account_state = self.get_account_state(account_address)
        return  account_state.violas_get_balance(module_address)

    #Not exist raise AcccountError
    def violas_get_info(self,account_address):
        account_state = self.get_account_state(account_address)
        return account_state.violas_get_info()

    def violas_submit_exchange(self, sender_account, receiver_address, source_amount,
        source_module_address, exchange_amount, exchange_module_address, fee,
        exchange_exexpiration, max_gas=140_000, unit_price=0, is_blocking=False, txn_expiration=100):
        if isinstance(exchange_module_address, bytes):
            exchange_module_address = exchange_module_address.hex()
        data = {
            "type": "sub_ex",
            "addr": exchange_module_address,
            "amount": exchange_amount,
            "fee": fee,
            "exp": exchange_exexpiration
        }
        return self.violas_transfer_coin(sender_account, receiver_address, source_amount, source_module_address, json.dumps(data)
                                         , max_gas, unit_price, is_blocking, txn_expiration)

    def violas_feedback_exchange(self, sender_account, receiver_address, amount, module_address, version, fee, state,
        max_gas=140_000, unit_price=0, is_blocking=False, txn_expiration=100):
        data = {
            "type": "fb_ex",
            "ver": version,
            "fee": fee,
            "state": state
        }
        return self.violas_transfer_coin(sender_account, receiver_address, amount, module_address, json.dumps(data)
                                         , max_gas, unit_price, is_blocking, txn_expiration)

    def violas_withdraw_exchange(self, sender_account, receiver_address, module_address, version,
        max_gas=140_000, unit_price=0, is_blocking=False, txn_expiration=100):
        data = {"type": "wd_ex", "ver": version}
        return self.violas_transfer_coin(sender_account, receiver_address, 0, module_address, json.dumps(data)
                                         ,max_gas, unit_price, is_blocking, txn_expiration)

