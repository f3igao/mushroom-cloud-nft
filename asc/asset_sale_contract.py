import random

from pyteal import *

from helpers.consts import AppVariables


def asset_sale_contract(seller: str, asset_index: int, price: int):
    RANDOM = random.randrange(2 ** 24)

    # ARTIST_SOUND = 'OBVRRZENURKIN7QSSCGXAQ3Y642BLMGXZWJUQTHW7WWKY5DINHE3GYRBTU'
    ARTIST_SOUND = 'E6U45JTJJQKGIQXECBTUAEARHU7PKCSRVLR5Q4PWT2EDG5XSOVOMK77LUA'

    put_on_sale = And(
        Global.group_size() == Int(3),
        # fund escrow
        Gtxn[0].type_enum() == TxnType.Payment,
        Gtxn[0].amount() == Int(int(0.5 * 1e6)),
        Gtxn[0].sender() == Addr(seller),
        Gtxn[0].close_remainder_to() == Global.zero_address(),
        # opt in escrow
        Gtxn[1].type_enum() == TxnType.AssetTransfer,
        Gtxn[1].asset_amount() == Int(0),
        Gtxn[1].sender() == Gtxn[0].receiver(),
        Gtxn[1].sender() == Gtxn[1].asset_receiver(),
        Gtxn[1].asset_close_to() == Global.zero_address(),
        Gtxn[1].xfer_asset() == Int(asset_index),
        # transfer asset to escrow
        Gtxn[2].type_enum() == TxnType.AssetTransfer,
        Gtxn[2].asset_amount() == Int(1),
        Gtxn[2].sender() == Addr(seller),
        Gtxn[2].asset_receiver() == Gtxn[1].sender(),
        Gtxn[2].asset_close_to() == Global.zero_address(),
        Gtxn[2].xfer_asset() == Int(asset_index),
    )

    buy_asset = And(
        Global.group_size() == Int(4),
        # pay seller 90% of the sale
        Gtxn[0].type_enum() == TxnType.Payment,
        Gtxn[0].amount() == Int(int(price * 1e6 * 0.9)),
        Gtxn[0].receiver() == Addr(seller),
        Gtxn[0].close_remainder_to() == Global.zero_address(),
        # opt in buyer to nft
        Gtxn[1].type_enum() == TxnType.AssetTransfer,
        Gtxn[1].asset_amount() == Int(0),
        Gtxn[1].sender() == Gtxn[0].sender(),
        Gtxn[1].sender() == Gtxn[1].asset_receiver(),
        Gtxn[1].asset_close_to() == Global.zero_address(),
        Gtxn[1].xfer_asset() == Int(asset_index),
        # transfer asset to buyer
        Gtxn[2].type_enum() == TxnType.AssetTransfer,
        Gtxn[2].asset_amount() == Int(1),
        Gtxn[2].asset_receiver() == Gtxn[1].sender(),
        Gtxn[2].asset_close_to() == Gtxn[1].sender(),
        Gtxn[2].xfer_asset() == Int(asset_index),
        # close escrow remainder to seller
        Gtxn[3].type_enum() == TxnType.Payment,
        Gtxn[3].amount() == Int(0),
        Gtxn[3].receiver() == Addr(seller),
        Gtxn[3].close_remainder_to() == Addr(seller),
        Gtxn[3].sender() == Gtxn[2].sender(),
        # pay collaborator 10% of the sale
        Gtxn[4].type_enum() == TxnType.Payment,
        Gtxn[4].amount() == Int(int(price * 1e6 * 0.1)),
        Gtxn[4].receiver() == Addr(ARTIST_SOUND),
        Gtxn[4].close_remainder_to() == Global.zero_address(),
    )

    cancel = And(
        Global.group_size() == Int(3),
        # opt in seller
        Gtxn[0].type_enum() == TxnType.AssetTransfer,
        Gtxn[0].asset_amount() == Int(0),
        Gtxn[0].sender() == Gtxn[0].asset_receiver(),
        Gtxn[0].asset_close_to() == Global.zero_address(),
        Gtxn[0].xfer_asset() == Int(asset_index),
        Gtxn[0].asset_receiver() == Addr(seller),
        # close asset to seller
        Gtxn[1].type_enum() == TxnType.AssetTransfer,
        Gtxn[1].asset_amount() == Int(1),
        Gtxn[1].xfer_asset() == Int(asset_index),
        Gtxn[1].asset_receiver() == Addr(seller),
        Gtxn[1].asset_close_to() == Addr(seller),
        # close escrow remainder to seller
        Gtxn[2].type_enum() == TxnType.Payment,
        Gtxn[2].amount() == Int(0),
        Gtxn[2].sender() == Gtxn[1].sender(),
        Gtxn[2].receiver() == Addr(seller),
        Gtxn[2].close_remainder_to() == Addr(seller),
    )

    security = And(
        Txn.fee() <= Global.min_txn_fee(),
        Txn.lease() == Global.zero_address(),
        Txn.rekey_to() == Global.zero_address(),
        Int(RANDOM) == Int(RANDOM),
    )

    contract_py = And(
        security,
        Cond(
            [Global.group_size() == Int(3), Or(put_on_sale, cancel)],
            [Global.group_size() == Int(5), buy_asset],
        ),
    )

    contract_teal = compileTeal(contract_py, Mode.Signature, version=6)
    return contract_teal


ARTIST_MAIN_ADDRESS = "PIQVKPN4EAHMS74DK5CSCIZCJ6CM7OSIUZYQ5Y6MYFP26XZHBPRNJHAPDA"
ASSET_ID = 78961298
PRICE = 100

contract_teal = asset_sale_contract(ARTIST_MAIN_ADDRESS, ASSET_ID, PRICE)
with open('../teal/asset_sale_contract.teal', 'w+') as f:
    f.write(str(contract_teal))
