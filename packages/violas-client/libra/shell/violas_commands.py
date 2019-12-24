from libra.cli.command import *
from canoser import Uint64
from libra import AccountState

class ViolasCommand(Command):
    def get_aliases(self):
        return ["violas", "v"]

    def get_description(self):
        return "Violas operations"

    def execute(self, client, params):
        commands = [
            ViolasCommandPublishModule(),
            ViolasCommandInit(),
            ViolasCommandMint(),
            ViolasCommandTransfer(),
            ViolasCommandGetBalance(),
            ViolasCommandMakeOrder(),
            ViolasCommandPickOrder(),
            ViolasCommandWithdrawOrder()
        ]
        self.subcommand_execute(params[0], commands, client, params[1:])

class ViolasCommandGetBalance(Command):
    def get_aliases(self):
        return ["balance", "b"]

    def get_params_help(self):
        return "<account_ref_id>|<account_address> <module_ref_id>|<module_address>"

    def get_description(self):
        return "Get the current violas balance of an account"

    def execute(self, client, params):
        balance = client.get_violas_balance(params[1],params[2])
        print(f"Balance is: {balance}")


class ViolasCommandPublishModule(Command):
    def get_aliases(self):
        return ["publish", "publishb", "p", "pb"]

    def get_params_help(self):
        return "<account_ref_id>|<account_address>"

    def get_description(self):
        return "Publish violas module on-chain"

    def execute(self, client, params):
        print(">> Publishing module")
        is_blocking = blocking_cmd(params[0])
        client.violas_publish(params[1], is_blocking)
        if is_blocking:
            print("Finished publishing!")
        else:
            print("Publish request submitted")

class ViolasCommandInit(Command):
    def get_aliases(self):
        return ["init", "initb", "i", "ib"]

    def get_params_help(self):
        return "<account_ref_id>|<account_address> <module_ref_id>|<module_address>"

    def get_description(self):
        return "Init violas module on-chain"

    def execute(self, client, params):
        print(">> Initing module")
        is_blocking = blocking_cmd(params[0])
        client.violas_init(params[1], params[2], is_blocking)
        if is_blocking:
            print("Finished initing!")
        else:
            print("init request submitted")

class ViolasCommandMint(Command):
    def get_aliases(self):
        return ["mint", "mintb", "m", "mb"]

    def get_params_help(self):
        return "<receiver_account_ref_id>|<receiver_account_address> <number_of_coins> <module_account_ref_id>|<module_account_address>"

    def get_description(self):
        return "Mint violas coins to the account. Suffix 'b' is for blocking"

    def execute(self, client, params):
        print(">> Minting coins")
        is_blocking = blocking_cmd(params[0])
        client.violas_mint_coin(params[1], params[2], params[3], is_blocking)
        if is_blocking:
            print("Finished minting!")
        else:
            print("Mint request submitted")

class ViolasCommandTransfer(Command):
    def get_aliases(self):
        return ["transfer", "transferb", "t", "tb"]

    def get_params_help(self):
        return ("<sender_account_address>|<sender_account_ref_id>"
         " <receiver_account_address>|<receiver_account_ref_id> <number_of_coins> <module_account_address>|<module_account_ref_id>"
         " [gas_unit_price_in_micro_libras (default=0)] [max_gas_amount_in_micro_libras (default 140000)]")

    def get_description(self):
        return "Transfer coins (in violas) from account to another. Suffix 'b' is for blocking"

    def execute(self, client, params):
        if len(params) == 6:
            gas_unit_price_in_micro_libras = Uint64.int_safe(params[5])
        else:
            gas_unit_price_in_micro_libras = 0
        if len(params) == 7:
            max_gas_amount_in_micro_libras = Uint64.int_safe(params[6])
        else:
            max_gas_amount_in_micro_libras = 140_000
        print(">> Transferring")
        is_blocking = blocking_cmd(params[0])
        sequence_number = client.violas_transfer_coin(params[1], params[2], params[3], params[4],
            max_gas_amount_in_micro_libras, gas_unit_price_in_micro_libras, is_blocking)
        if is_blocking:
            print("Finished transaction!")
        else:
            print("Transaction submitted to validator")
        print(
            "To query for transaction status, run: query txn_acc_seq {} {} \
            <fetch_events=true|false>".format(
            params[1], sequence_number
            )
        )

class ViolasCommandMakeOrder(Command):
    def get_aliases(self):
        return ["order", "orderb", "r", "rb"]

    def get_params_help(self):
        return ("<sender_account_address>|<sender_account_ref_id>  <module_account_address>|<module_account_ref_id> <amount> <price>")

    def get_description(self):
        return "Submit an order for a module.  Suffix 'b' is for blocking."

    def execute(self, client, params):
        print(">> Transferring")
        is_blocking = blocking_cmd(params[0])
        sequence_number = client.violas_make_order(params[1], params[2], params[3], params[4], is_blocking=is_blocking)
        if is_blocking:
            print("Finished transaction!")
        else:
            print("Transaction submitted to validator")
        print(
            "To query for transaction status, run: query txn_acc_seq {} {} \
            <fetch_events=true|false>".format(
            params[1], sequence_number
            )
        )

class ViolasCommandPickOrder(Command):
    def get_aliases(self):
        return ["pick", "pickb", "pi", "pib"]

    def get_params_help(self):
        return ("<sender_account_address>|<sender_account_ref_id> <order_account_address>|<order_account_ref_id>"
                " <module_account_address>|<module_account_ref_id> ")

    def get_description(self):
        return "Pick a module order from an account.  Suffix 'b' is for blocking."

    def execute(self, client, params):
        print(">> Transferring")
        is_blocking = blocking_cmd(params[0])
        sequence_number = client.violas_pick_order(params[1], params[2], params[3], is_blocking=is_blocking)
        if is_blocking:
            print("Finished transaction!")
        else:
            print("Transaction submitted to validator")
        print(
            "To query for transaction status, run: query txn_acc_seq {} {} \
            <fetch_events=true|false>".format(
            params[1], sequence_number
            )
        )

class ViolasCommandWithdrawOrder(Command):
    def get_aliases(self):
        return ["withdraw", "withdrawb", "w", "wb"]

    def get_params_help(self):
        return ("<sender_account_address>|<sender_account_ref_id> <module_account_address>|<module_account_ref_id> ")

    def get_description(self):
        return "Withdraw a module order from an account.  Suffix 'b' is for blocking."

    def execute(self, client, params):
        print(">> Transferring")
        is_blocking = blocking_cmd(params[0])
        sequence_number = client.violas_withdraw_order(params[1], params[2], is_blocking=is_blocking)
        if is_blocking:
            print("Finished transaction!")
        else:
            print("Transaction submitted to validator")
        print(
            "To query for transaction status, run: query txn_acc_seq {} {} \
            <fetch_events=true|false>".format(
            params[1], sequence_number
            )
        )


# class ViolasCommandGetLatestAccountState(Command):
#     def get_aliases(self):
#         return ["account_state", "as"]
#
#     def get_params_help(self):
#         return "<account_ref_id>|<account_address> <moudule_ref_id>|<module_address>"
#
#     def get_description(self):
#         return "Get the latest violas state for an account"
#
#     def execute(self, client, params):
#         print(">> Getting latest violas account state")
#         (acc, addr, version) = client.get_latest_account_state(params[1])
#         module_address = client.parse_address_or_refid(params[2])
#         amp = acc.to_violas_json_serializable(bytes.fromhex(module_address))
#         print(json_print(amp, sort_keys= True))

