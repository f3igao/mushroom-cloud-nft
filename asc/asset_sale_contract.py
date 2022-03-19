from pyteal import *

import random


def asset_sale_contract(seller: str, asset_id: int, price: int):
    RANDOM = random.randrange(2 ** 24)

    put_on_sale = And(
        Global.group_size() == Int(3),
        # fund escrow
        Gtxn[0].type_enum() == TxnType.Payment,
        Gtxn[0].amount() == Int(int(0.5 * 1e6)),
        Gtxn[0].sender() == Addr(seller),
        Gtxn[0].close_remainder_to() == Global.zero_address(),
        # opt in nft
        Gtxn[1].type_enum() == TxnType.AssetTransfer,
        Gtxn[1].asset_amount() == Int(0),
        Gtxn[1].sender() == Gtxn[0].receiver(),
        Gtxn[1].sender() == Gtxn[1].asset_receiver(),
        Gtxn[1].asset_close_to() == Global.zero_address(),
        Gtxn[1].xfer_asset == Int(asset_id),
        # transfer to escrow
        Gtxn[2].type_enum() == TxnType.AssetTransfer,
        Gtxn[2].asset_amount() == Int(1),
        Gtxn[2].sender() == Addr(seller),
        Gtxn[2].asset_receiver() == Gtxn[1].sender(),
        Gtxn[2].asset_close_to() == Global.zero_address(),
        Gtxn[2].xfer_asset == Int(asset_id),
    )

    buy_asset = And(
        Global.group_size() == Int(4),
        # pay seller for asset
        Gtxn[0].type_enum() == TxnType.Payment,
        Gtxn[0].amount() == Int(price * 1e6),
        Gtxn[0].receiver() == Addr(seller),
        Gtxn[0].close_remainder_to() == Global.zero_address(),
        # opt buyer into nft
        Gtxn[1].type_enum() == TxnType.AssetTransfer,
        Gtxn[1].asset_amount() == Int(0),
        Gtxn[1].sender() == Gtxn[0].sender(),
        Gtxn[1].sender() == Gtxn[1].asset_receiver(),
        Gtxn[1].asset_close_to() == Global.zero_address(),
        Gtxn[1].xfer_asset == Int(asset_id),
        # transfer asset to buyer
        Gtxn[2].type_enum() == TxnType.AssetTransfer,
        Gtxn[2].asset_amount() == Int(1),
        Gtxn[2].asset_receiver() == Gtxn[1].sender(),
        Gtxn[2].asset_close_to() == Gtxn[1].sender(),
        Gtxn[2].xfer_asset == Int(asset_id),
        # close escrow remainder to seller
        Gtxn[3].type_enum() == TxnType.Payment,
        Gtxn[3].amount == Int(0),
        Gtxn[3].receiver == Addr(seller),
        Gtxn[3].close_remainder_to() == Addr(seller),
        Gtxn[3].sender == Gtxn[2].sender(),
    )

    cancel = And(
        Global.group_size() == Int(3),
        # opt in seller
        Gtxn[0].type_enum() == TxnType.AssetTransfer,
        Gtxn[0].asset_amount() == Int(0),
        Gtxn[0].sender() == Gtxn[0].asset_receiver(),
        Gtxn[0].asset_close_to() == Global.zero_address(),
        Gtxn[0].xfer_asset == Int(asset_id),
        Gtxn[0].asset_receiver() == Addr(seller),
        # close asset to seller
        Gtxn[1].type_enum() == TxnType.AssetTransfer,
        Gtxn[1].asset_amount() == Int(1),
        Gtxn[1].xfer_asset() == Int(asset_id),
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
            [Global.group_size() == Int(4), buy_asset],
        ),
    )

    contract_teal = compileTeal(contract_py, Mode.Signature, version=6)
    return contract_teal
