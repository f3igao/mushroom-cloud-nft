import base64
import json
import os

from algosdk import encoding, mnemonic
from algosdk.v2client import algod


def create_algod_client():
    # TODO: update to mainnet
    endpoint = 'https://testnet-algorand.api.purestake.io/ps2'
    token = ''
    headers = {
        'X-API-Key': os.getenv('PURESTAKE_KEY'),
    }
    return algod.AlgodClient(token, endpoint, headers)


# wait until the transaction is confirmed before proceeding
def wait_for_confirmation(client, txn_id):
    last_round = client.status().get('last-round')
    txn_info = client.pending_transaction_info(txn_id)
    while not (txn_info.get('confirmed-round') and txn_info.get('confirmed-round') > 0):
        print('waiting for transaction confirmation')
        last_round += 1
        client.status_after_block(last_round)
        txn_info = client.pending_transaction_info(txn_id)
    print(f'transaction {txn_id} confirmed in round {txn_info.get("confirmed-round")}.')
    return txn_info


#   utility function used to print created asset for account and asset_id
def print_created_asset(algod_client, account, asset_id):
    # note: if you have an indexer instance available it is easier to just use this
    # response = myindexer.accounts(asset_id = asset_id)
    # then use 'account_info['created-assets'][0] to get info on the created asset
    account_info = algod_client.account_info(account)
    idx = 0
    for my_account_info in account_info['created-assets']:
        scrutinized_asset = account_info['created-assets'][idx]
        idx = idx + 1
        if scrutinized_asset['index'] == asset_id:
            print(f'asset ID: {scrutinized_asset["index"]}')
            print(json.dumps(my_account_info['params'], indent=4))
            break


#   Utility function used to print asset holding for account and asset_id
def print_asset_holding(algod_client, account, asset_id):
    # note: if you have an indexer instance available it is easier to just use this
    # response = myindexer.accounts(asset_id = asset_id)
    # then loop thru the accounts returned and match the account you are looking for
    account_info = algod_client.account_info(account)
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1
        if scrutinized_asset['asset-id'] == asset_id:
            print(f'account: {account}, asset ID: {scrutinized_asset["asset-id"]}')
            print(json.dumps(scrutinized_asset, indent=4))
            break


# Utility function to create ASA metadata
def metadata_template(description, standard, external_url, attributes):
    metadata = {'description': description, 'standard': standard, 'external_url': external_url,
                'attributes': attributes}
    metadata_note = json.dumps(metadata).encode()
    return metadata_note


# helper function to compile program source
def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response['result'])


# helper function to convert a mnemonic passphrase into a private signing key
def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    return private_key


# helper function to convert a mnemonic passphrase into a public key
def get_public_key_from_mnemonic(mn):
    public_key = mnemonic.to_public_key(mn)
    return public_key


# convert 64 bit integer i to byte string
def int_to_bytes(i):
    return i.to_bytes(8, 'big')


# convert string s to byte string
def address_to_bytes(a):
    return encoding.decode_address(a)
