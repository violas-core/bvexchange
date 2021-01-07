import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
from lbsafemsg import *
from multiprocessing import Lock
input_lock = Lock()
client = smc_client(smc_key_source.KEY_VAULT, use_mempool = True)
from webserver.init_keys import (
        get_client,
        vault_name,
        sign_name,
        verify_name
        )

client = get_client()
def get_sign_key_id(client):
    return client.make_md5(client.get_azure_secret_value(vault_name, verify_name))

def sign_message(client, message):
    return client.generate_sign(None, message, None, azure_name = smc_azure_names.SIGN_KEY)

def verify_sign(client, message, sign_msg):
    verify_state = client.verify_sign(None, message, sign_msg, None, azure_name = smc_azure_names.VERIFY_KEY)
    assert verify_state, f"sign/verify failed."
