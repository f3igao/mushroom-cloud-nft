from pyteal import *


@Subroutine(TealType.none)
def default_transaction_checks(txn_id: Int) -> TealType.none:
    # verifies the rekeyTo, closeRemainderTo, and the assetCloseTo attributes are set equal to the zero address
    return Seq(
        [
            Assert(txn_id < Global.group_size()),
            Assert(Gtxn[txn_id].rekey_to() == Global.zero_address()),
            Assert(Gtxn[txn_id].close_remainder_to() == Global.zero_address()),
            Assert(Gtxn[txn_id].asset_close_to() == Global.zero_address()),
        ]
    )


@Subroutine(TealType.none)
def send_payment(receiver: Addr, amount: Int) -> TealType.none:
    # sends payments from asc to other accts in microalgos using inner transactions
    return Seq([
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.Payment,
            TxnField.amount: amount,
            TxnField.receiver: receiver,
            TxnField.fee: Global.min_txn_fee()
        }),
        InnerTxnBuilder.Submit(),
    ])


@Subroutine(TealType.none)
def transfer_asset(sender: Addr, receiver: Addr, asset_id: Int) -> TealType.none:
    # transfers an asset from one acct to another
    # can be used to opt in an asset if 'amount' is 0 and `sender` is equal to `receiver`
    # asset_id must also be passed in the `foreign_assets` field in the outer transaction (otherwise reference error)
    return Seq([
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields({
            TxnField.type_enum: TxnType.AssetTransfer,
            TxnField.asset_amount: Int(1),
            TxnField.asset_receiver: receiver,
            TxnField.asset_sender: sender,
            TxnField.xfer_asset: asset_id,
            TxnField.fee: Global.min_txn_fee()
        }),
        InnerTxnBuilder.Submit(),
    ])


@Subroutine(TealType.none)
def check_nft_balance(account: Addr, asset_id: Int) -> TealType.none:
    # checks acct owns nft
    # note: asset id must also be passed in the `foreignAssets` field in the outer transaction
    # otherwise get a reference error
    asset_acct_balance = AssetHolding.balance(account, asset_id)
    return Seq([
        asset_acct_balance,
        Assert(asset_acct_balance.hasValue() == Int(1)),
        Assert(asset_acct_balance.value() == Int(1))
    ])


@Subroutine(TealType.uint64)
def compute_royalty_fee(amount: Int, royalty_fee: Int) -> TealType.uint64:
    # computes the fee given a specific `amount` and predefined `royalty_fee`
    # `royalty_fee` must be expressed in thousands
    # note: must call check_royalty_fee_computation() before calling this function
    # the safety of computing `remainder` and `division` is given by calling check_royalty_fee_computation()
    remainder = ScratchVar(TealType.uint64)
    division = ScratchVar(TealType.uint64)

    # if the fee is equal to 0, or the amount is very small, the fee will be 0
    # if the royalty fee is larger or equal to 1000, then return the original amount
    # if the remainder of royalty_fee * amount / 1000 is larger than 500 round up the
    # result and return  1 + royalty_fee * amount / 1000
    # otherwise  just return royalty_fee * amount / 1000

    return Seq([
        check_royalty_fee_computation(amount, royalty_fee),
        remainder.store(Mod(Mul(amount, royalty_fee), Int(1000))),
        division.store(Div(Mul(amount, royalty_fee), Int(1000))),
        Return(If(Or(royalty_fee == Int(0), division.load() == Int(0))).Then(Int(0)) \
               .ElseIf(royalty_fee >= Int(1000)).Then(amount) \
               .ElseIf(remainder.load() > Int(500)).Then(division.load() + Int(1)) \
               .Else(division.load()))
    ])


@Subroutine(TealType.none)
def check_royalty_fee_computation(amount: Int, royalty_fee: Int) -> TealType.none:
    # checks that there are no problems computing the royalty fee given a specific `amount` and `royalty_fee`
    # `royalty_fee` must be expressed in thousands

    return Seq([
        Assert(amount > Int(0)),
        Assert(royalty_fee <= Div(Int(2 ** 64 - 1), amount)),
    ])
