import sys, os
import json
sys.path.append(os.getcwd())
sys.path.append("..")
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
from lbsafemsg import *
from multiprocessing import Lock
input_lock = Lock()

vault_name = "vault-test02"
sign_name = "bvweb-sign-key"
verify_name = "bvweb-verify-key"
#*********************************************init sign************************************************
def __input_ids(debug = True):
    if debug:
        client_id = "80f16cbd-e549-4c93-9e7b-22a91c8615d4"
        tenant_id = "d99eee11-8587-4c34-9201-38d5247df9c9"
        secret = "sUN0g~V9o81.M5UP1tJHKRMgxS_ru7g~O~"

    else:
        client_id = input(f"input azure_client_id: ")
        tenant_id = input(f"input azure_tenant_id: ")
        secret    = input(f"input azure_client_secret: ")
    return (client_id, tenant_id, secret)

def __get_ids():
    client = smc_client()
    pri_key = load_decrypt_key()
    return client.load_azure_secret_ids_from_file("azure_ids.key", pri_key)

def pri_pub():
    return smc_client().create_keys()

def get_client():
    input_lock.acquire()
    pri_key = load_decrypt_key()
    client = smc_client(smc_key_source.KEY_VAULT, use_mempool = True)
    client.set_azure_key_path(smc_azure_names.SIGN_KEY, vault_name, sign_name)
    client.set_azure_key_path(smc_azure_names.VERIFY_KEY, vault_name, verify_name)
    client.set_azure_secret_ids_with_file("azure_ids.key", pri_key)
    input_lock.release()
    return client
    
#**********************save ids to local and save sign/verify key to local******************

def save_datas(datas, filename):
    with open(filename, 'w') as pf:
        pf.write(datas.encode().hex())
        return True
    return False

def load_datas(filename):
    with open(filename, 'r') as pf:
        datas = pf.read()
    return bytes.fromhex(datas).decode()


def new_crypty_key_to_local(decrypt_filename = "decrypt.key", encrypt_filename = "encrypt_public.key"):
    pri_key, pub_key = pri_pub()
    save_datas(pri_key, decrypt_filename)
    save_datas(pub_key, encrypt_filename)

def load_encrypt_key(filename = "encrypt_public.key"):
    return load_datas(filename)

def load_decrypt_key(filename = "decrypt.key"):
    return load_datas(filename)

def update_azure_ids():
    client = smc_client()
    client_id , tenant_id, secret = __input_ids()
    pub_key = load_encrypt_key()
    client.save_azure_secret_ids_to_file("azure_ids.key", pub_key, client_id, tenant_id, secret)

def test_init_client():
    get_client()

def test_updata_azure_ids():
    update_azure_ids()

def test_get_ids_from_local():
    client_id, tenant_id, secret = __get_ids()
    print(f'''
    azure ids: 
    client id: {client_id} 
    tenant id: {tenant_id} 
    secret: {secret}
    '''
    )

def test_sign_verify():
    client = get_client()
    message = "7b227374617465223a202253554343454544222c20226d657373616765223a2022222c20226461746173223a205b7b2261646472657373223a20223030303030303030303030303030303030303432353234373264343235343433222c202274797065223a20227632626d222c2022636861696e223a202276696f6c6173222c2022636f6465223a2022222c202266726f6d5f746f5f746f6b656e223a205b7b2266726f6d5f636f696e223a202276425443222c2022746f5f636f696e223a2022425443227d5d7d2c207b2261646472657373223a2022324e325961735455644c625873616648486d796f4b5559635252696352506755794e42222c202274797065223a20226232766d222c2022636861696e223a2022627463222c2022636f6465223a2022307833303030222c202266726f6d5f746f5f746f6b656e223a205b7b2266726f6d5f636f696e223a2022425443222c2022746f5f636f696e223a202276425443227d5d7d2c207b2261646472657373223a2022307846466636343538613037624362363964663245614562626639436634363361423038463366333942222c202274797065223a20226532766d222c2022636861696e223a2022657468657265756d222c2022636f6465223a2022222c202266726f6d5f746f5f746f6b656e223a205b7b2266726f6d5f636f696e223a202275736474222c2022746f5f636f696e223a20227655534454227d5d7d2c207b2261646472657373223a20223030303030303030303030303030303030303432353234373535353334343534222c202274797065223a20227632656d222c2022636861696e223a202276696f6c6173222c2022636f6465223a2022222c202266726f6d5f746f5f746f6b656e223a205b7b2266726f6d5f636f696e223a20227655534454222c2022746f5f636f696e223a202275736474227d5d7d5d7d"
    sign_msg = "WqscO4Ybe7cbN98LVa/mifP96k5qr6ZxjgoRte2G0gY2QB5E2zwtnctHj501QZQ1eBhPZb6pPKfJdqWE80e9vvd9QV2U1MBXITZk1vn6J7AG72fPuGhxE/SLAO8GDcWeJKTh8qHvVAb0onJ/brxsRS1BhnI7FNOYZSATpLb38iudWQBJmKAChaTNiNduf5x0CEutp/SAHK1hvARjpTj5fI8AeLt2a7vQsp4+vBpvW5IuvyaEsG4bC/rMlxnZRERZGTje9lVHAHsrb2x4U1vZM4UrCtF1gmIIgY27S3kAdgnO6mf8vvXR8lf0BL29rJPV1mK2nhq5mJkQbppbTuye5Q=="

    sign_key_id     =  client.make_md5(client.get_azure_secret_value(vault_name, verify_name))

    sign_msg        = client.generate_sign(None, message, None, azure_name = smc_azure_names.SIGN_KEY)
    verify_state    = client.verify_sign(None, message, sign_msg, None, azure_name = smc_azure_names.VERIFY_KEY)
    assert verify_state, f"sign/verify failed."
    
    print(f"datas : {json.loads(bytes.fromhex(message))}")

def test_new_crypet_key_to_local():
    new_crypty_key_to_local()

if __name__ == "__main__":
    test_new_crypet_key_to_local()
    test_updata_azure_ids()
    test_get_ids_from_local()
    #test_sign_verify()
    

