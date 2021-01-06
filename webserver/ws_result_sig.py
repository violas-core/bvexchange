import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
from lbsafemsg import *
from multiprocessing import Lock
input_lock = Lock()
#*********************************************init sign************************************************
def __get_ids():
    client_id = "80f16cbd-e549-4c93-9e7b-22a91c8615d4"
    tenant_id = "d99eee11-8587-4c34-9201-38d5247df9c9"
    secret = "sUN0g~V9o81.M5UP1tJHKRMgxS_ru7g~O~"

    return (client_id, tenant_id, secret)

def __input_ids(client):
    input_lock.acquire()
    client_id = client.get_azure_client_id()
    if not client_id:
        client_id = input("input AZURE_CLIENT_ID: ")

    tenant_id = client.get_azure_tenant_id()
    if not tenant_id:
        tenant_id = input("input AZURE_TENANT_ID: ")

    secret = client.get_azure_client_secret()
    if not secret:
        secret = input("input client secret: ")

    client.set_azure_secret_ids( client_id, tenant_id, secret)
    input_lock.release()

def pri_pub():
    return smc_client().create_keys()

client = smc_client(smc_key_source.KEY_VAULT, use_mempool = True)

#__input_ids(client)

client_id , tenant_id, secret = __get_ids()
client.set_azure_secret_ids( client_id, tenant_id, secret)
vault_name = "vault-test02"
#pri_key, pub_key = pri_pub()
sign_name = "bvweb-sign-key"
verify_name = "bvweb-verify-key"

#client.set_azure_secret(vault_name, sign_name, pri_key)
#client.set_azure_secret(vault_name, verify_name, pub_key)

client.set_azure_key_path(smc_azure_names.SIGN_KEY, vault_name, sign_name)
client.set_azure_key_path(smc_azure_names.VERIFY_KEY, vault_name, verify_name)
print("*****import ws_result_sig")

def get_sign_key_id(client):
    return client.make_md5(client.get_azure_secret_value(vault_name, verify_name))

def sign_message(client, message):
    return client.generate_sign(None, message, None, azure_name = smc_azure_names.SIGN_KEY)

