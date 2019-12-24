from libra import Client
from libra import WalletLibrary
from libra.json_print import json_print

def test_ret():
    wallet = WalletLibrary.new()
    a1 = wallet.new_account()
    a2 = wallet.new_account()
    client = Client.new('125.39.5.57',46454)
    client.get_account_blob(a1.address)
    client.get_account_state(a1.address)
    client.get_account_resource(a1.address)
    client.get_account_events(a1.address, 0)
    # client.get_account_blob(a1.address)


    # client.mint_coins(a1.address, 100, True)
    # client.mint_coins(a2.address, 100, True)
    # client.violas_publish(a1, True)
    # client.violas_publish(a2, True)
    # client.violas_init(a1, a1.address, True)
    # client.violas_init(a1, a2.address, True)
    # client.violas_init(a2, a1.address, True)
    # client.violas_init(a2, a2.address, True)
    # client.violas_mint_coin(a1.address, 100, a1, is_blocking=True)
    # client.violas_mint_coin(a1.address, 100, a2, is_blocking=True)
    # client.violas_make_order(a1, a1.address, 10, 10, is_blocking=True)
    # client.violas_make_order(a1, a2.address, 10, 10, is_blocking=True)