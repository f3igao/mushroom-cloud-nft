import os

from algosdk.future import transaction
from asc.operations import (opt_in_app, send_funds, set_clawback, setup_sale, buy_asset, buyer_execute_transfer,
                            claim_fees)
from asc.utils import (get_public_key_from_mnemonic, get_private_key_from_mnemonic, int_to_bytes, print_asset_holding,
                       wait_for_confirmation, create_algod_client)

from dotenv import load_dotenv

load_dotenv()
cwd = os.getcwd()

mnemonics = [
    os.getenv('CREATOR_MNEMONIC'),
    os.getenv('BUYER_1_MNEMONIC'),
    os.getenv('BUYER_2_MNEMONIC'),
]

asset_id = int(os.getenv('ASSET_ID'))
app_id = int(os.getenv('APP_ID'))
app_address = os.getenv('APP_ADDRESS')

# for ease of reference, add account public and private keys to an accounts dict
accounts = {}
counter = 1
for m in mnemonics:
    accounts[counter] = {}
    accounts[counter]['pk'] = get_public_key_from_mnemonic(m)
    accounts[counter]['sk'] = get_private_key_from_mnemonic(m)
    counter += 1

# create purestake algod_client
algod_client = create_algod_client()

# get network params for transactions before every transaction.
params = algod_client.suggested_params()
# comment these two lines to use suggested params
# params.fee = 1000
# params.flat_fee = True

creator_private_key = get_private_key_from_mnemonic(mnemonics[0])
buyer_1_private_key = get_private_key_from_mnemonic(mnemonics[1])
buyer_2_private_key = get_private_key_from_mnemonic(mnemonics[2])

creator_public_key = get_public_key_from_mnemonic(mnemonics[0])
buyer_1_public_key = get_public_key_from_mnemonic(mnemonics[1])
buyer_2_public_key = get_public_key_from_mnemonic(mnemonics[2])

# asset opt in
for wallet_num, value in accounts.items():
    # Check if asset_id is in account 2 and 3's asset holdings prior to opt-in
    account_info = algod_client.account_info(accounts[wallet_num]["pk"])
    holding = None
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1
        if scrutinized_asset['asset-id'] == asset_id:
            holding = True
            break

    if holding:
        print(f"confirming asset is already in account for address: {accounts[wallet_num]['pk']}")
    else:
        # use the AssetTransferTxn class to opt-in
        txn = transaction.AssetTransferTxn(
            sender=accounts[wallet_num]['pk'],
            sp=params,
            receiver=accounts[wallet_num]['pk'],
            amt=0,
            index=asset_id,
        )
        stxn = txn.sign(accounts[wallet_num]['sk'])
        txid = algod_client.send_transaction(stxn)
        print(txid)
        # Wait for the transaction to be confirmed
        wait_for_confirmation(algod_client, txid)
        # Now check the asset holding for that account.
        # This should now show a holding with a balance of 0.
        print(f'asset opt-in for address: {accounts[wallet_num]["pk"]}')
        print_asset_holding(algod_client, accounts[wallet_num]['pk'], asset_id)

# fund application
send_funds(algod_client, creator_private_key, app_address)

# setting clawback
set_clawback(algod_client, creator_private_key, asset_id, app_address)
print(f'set clawback address to: {app_address}')

# opt into application
opt_in_app(algod_client, creator_private_key, app_id)
opt_in_app(algod_client, buyer_1_private_key, app_id)
opt_in_app(algod_client, buyer_2_private_key, app_id)

foreign_assets = [asset_id]
asa_price = 1000000

# create list of bytes for sale setup app args
sale_args = [
    'setupSale'.encode(),
    int_to_bytes(asa_price),
]

setup_txn_id = setup_sale(
    algod_client, creator_private_key, app_id, sale_args, foreign_assets
)
print(f'Setup sale transaction ID: {setup_txn_id}')

buy_args = [
    'buy'.encode(),
    int_to_bytes(asset_id),
]

print('buyer 1 is attempting to buy the asset from the creator')
# buyer posting buy transactions
buy_asset(
    algod_client,
    buyer_1_private_key,
    creator_public_key,
    app_id,
    buy_args,
    foreign_assets,
    asa_price,
)

buyer_execute_args = [
    "executeTransfer".encode(),
]

# buyer executing transfer
buyer_execute_transfer(
    algod_client,
    buyer_1_private_key,
    creator_public_key,
    app_id,
    buyer_execute_args,
    foreign_assets,
)

print("---------sale from creator to buyer1 completed---------")
print_asset_holding(algod_client, creator_public_key, asset_id)
print_asset_holding(algod_client, buyer_1_public_key, asset_id)

setup_txn_id_v2 = setup_sale(
    algod_client, buyer_1_private_key, app_id, sale_args, foreign_assets
)
print(f"setup sale transaction ID: {setup_txn_id_v2}")

print("buyer 2 is attempting to buy the asset from buyer 1")
# buyer posting buy transactions
buy_asset(
    algod_client,
    buyer_2_private_key,
    buyer_1_public_key,
    app_id,
    buy_args,
    foreign_assets,
    asa_price,
)

# buyer executing transfer
buyer_execute_transfer(
    algod_client,
    buyer_2_private_key,
    buyer_1_public_key,
    app_id,
    buyer_execute_args,
    foreign_assets,
)

print("---------sale from buyer 1 to buyer 2 completed---------")
print_asset_holding(algod_client, buyer_1_public_key, asset_id)
print_asset_holding(algod_client, buyer_2_public_key, asset_id)

creator_claim_args = [
    "claimFees".encode(),
]

creator_account_before = algod_client.account_info(creator_public_key).get("amount")
print(
    f"Creator account balance before claiming fees: {creator_account_before} microAlgos."
)

claim_fees(algod_client, creator_private_key, app_id, creator_claim_args)

creator_account_after = algod_client.account_info(creator_public_key).get("amount")
print(
    f"Creator account balance after claiming fees: {creator_account_after} microAlgos."
)

print(
    f"Total fees claimed: {creator_account_after - creator_account_before} microAlgos"
)
