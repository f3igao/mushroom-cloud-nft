import os

from algosdk.future import transaction
from algosdk.v2client import algod
from dotenv import load_dotenv

CID = "bafybeidhxawiaatauhvxa5l32m4fdaavyztqdrnlz63po2aq5wwerbpmoe"
IPFS_URL = "ipfs://" + CID
print(f'ipfs url: {IPFS_URL}')

json_metadata_raw = open('assets/mock_metadata.json')
json_metadata = json_metadata_raw.read()


def create_algod_client():
    # TODO: update to mainnet
    endpoint = "https://testnet-algorand.api.purestake.io/ps2"
    token = ""
    headers = {
        "X-API-Key": os.getenv("PURESTAKE_KEY"),
    }
    return algod.AlgodClient(token, endpoint, headers)


def create_asa():
    private_key = os.getenv("SECRET_A")
    address = os.getenv("ADDRESS_A")

    # create purestake client to send requests
    client = create_algod_client()

    txn = transaction.AssetConfigTxn(
        sender=address,
        sp=client.suggested_params(),
        total=1,
        default_frozen=False,
        manager="",
        reserve="",
        freeze=False,
        clawback="",
        url=IPFS_URL,
        # metadata_hash="",
        strict_empty_address_check=False,
        decimals=0,
        # TODO: add ARC69 metadata
        # note=json_metadata.encode(),
    )

    # sign transaction with our private key to confirm authorization
    signed_txn = txn.sign(private_key=private_key)
    print('signing transaction...')

    try:
        # send transaction to the network using purestake
        txid = client.send_transaction(signed_txn)
        resp = transaction.wait_for_confirmation(client, txid, 5)
        print(f"successfully sent transaction with id: {txid}")
        print(f"response: {resp}")
        print(f"asset ID: {resp['asset-index']}")
        print(f"ipfs url: https://ipfs.io/ipfs/{CID}")
        print(f"algoexplorer: https://testnet.algoexplorer.io/asset/{resp['asset-index']}")
    except Exception as err:
        print(err)


if __name__ == "__main__":
    load_dotenv()
    create_asa()
