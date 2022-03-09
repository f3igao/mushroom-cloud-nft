import os

from algosdk.future import transaction
from dotenv import load_dotenv

from asc.utils import create_algod_client

CID = 'bafybeidhxawiaatauhvxa5l32m4fdaavyztqdrnlz63po2aq5wwerbpmoe'
IPFS_URL = 'ipfs://' + CID
print(f'ipfs url: {IPFS_URL}')

json_metadata_raw = open('../assets/mock_metadata.json')
json_metadata = json_metadata_raw.read()


def create_asa():
    private_key = os.getenv('CREATOR_SECRET')
    address = os.getenv('CREATOR_ADDRESS')

    # create purestake algod_client to send requests
    algod_client = create_algod_client()

    txn = transaction.AssetConfigTxn(
        sender=address,
        sp=algod_client.suggested_params(),
        total=1,
        default_frozen=False,
        unit_name="MUSHROOM",
        asset_name="Nancy Baker's Mushroom Cloud",
        manager='',
        reserve='',
        freeze='',
        clawback='',
        url=IPFS_URL,
        # metadata_hash=json_metadata_hash,
        strict_empty_address_check=False,
        decimals=0,
        # TODO: add ARC69 metadata
        # note=json_metadata.encode(),
    )

    # sign transaction with our private key to confirm authorization
    signed_txn = txn.sign(private_key=private_key)
    print('signing transaction to create asa...')

    try:
        # send transaction to the network using purestake
        txn_id = algod_client.send_transaction(signed_txn)
        resp = transaction.wait_for_confirmation(algod_client, txn_id, 5)
        asset_id = resp['asset-index']

        with open('../.env', 'a') as f:
            f.write(f'ASSET_ID={asset_id}\n')
            f.flush()

        print(f'successfully sent transaction with id: {txn_id}')
        print(f'response: {resp}')
        print(f'asset ID: {asset_id}')
        print(f'ipfs url: https://ipfs.io/ipfs/{CID}')
        print(f'algoexplorer: https://testnet.algoexplorer.io/asset/{resp["asset-index"]}')

    except Exception as err:
        print(err)


if __name__ == '__main__':
    load_dotenv()
    create_asa()
