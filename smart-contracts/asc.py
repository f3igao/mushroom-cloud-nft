from pyteal import *

from consts import AppVariables


def approval_program():
    # [Step 1] Sequence used to initialize the smart contract. Should be called only at creation
    royaltyFeeArg = Btoi(Txn.application_args[2])
    assetDecimals = AssetParam.decimals(Btoi(Txn.application_args[1]))
    assetFrozen = AssetParam.defaultFrozen(Btoi(Txn.application_args[1]))
    initialize = Seq([
        Assert(Txn.type_enum() == TxnType.ApplicationCall),  # Check if it's an application call
        Assert(Txn.application_args.length() == Int(4)),
        # Check that there are 4 arguments, Creator, AssetId and Royalty Fee and Round Wait
        Assert(royaltyFeeArg > Int(0) and royaltyFeeArg <= Int(1000)),
        # verify that the Royalty fee is between 0 and 1000
        defaultTransactionChecks(Int(0)),  # Perform default transaction checks
        assetDecimals,  # Load the asset decimals
        Assert(assetDecimals.hasValue()),
        Assert(assetDecimals.value() == Int(0)),  # Verify that there are no decimals
        assetFrozen,  # Load the frozen parameter of the asset
        Assert(assetFrozen.hasValue()),
        Assert(assetFrozen.value() == Int(1)),  # Verify that the asset is frozen
        App.globalPut(Constants.Creator, Txn.application_args[0]),  # Save the initial creator
        App.globalPut(Constants.AssetId, Btoi(Txn.application_args[1])),  # Save the asset ID
        App.globalPut(Constants.royaltyFee, royaltyFeeArg),  # Save the royalty fee
        App.globalPut(Constants.waitingTime, Btoi(Txn.application_args[3])),
        # Save the waiting time in number of rounds
        Approve()
    ])

    # onCall Sequence
    # Checks that the first transaction is an Application call, and that there is at least 1 argument.
    # Then it checks the first argument of the call. The first argument must be a valid value between
    # "setupSale", "buy", "executeTransfer", "refund" and "claimFees"
    onCall = If(Or(Txn.type_enum() != TxnType.ApplicationCall,Txn.application_args.length() == Int(0))
                ).Then(Reject()) \
        .ElseIf(Txn.application_args[0] == AppVariables.setupSale).Then(setupSale) \
        .ElseIf(Txn.application_args[0] == AppVariables.buy).Then(buy) \
        .ElseIf(Txn.application_args[0] == AppVariables.executeTransfer).Then(executeTransfer) \
        .ElseIf(Txn.application_args[0] == AppVariables.refund).Then(refund) \
        .ElseIf(Txn.application_args[0] == AppVariables.claimFees).Then(claimFees) \
        .Else(Reject())

    # Check the transaction type and execute the corresponding code
    #   1. If application_id() is 0 then the program has just been created, so we initialize it
    #   2. If on_completion() is 0 we execute the onCall code
    return If(Txn.application_id() == Int(0)).Then(initialize) \
        .ElseIf(Txn.on_completion() == OnComplete.CloseOut).Then(Approve()) \
        .ElseIf(Txn.on_completion() == OnComplete.OptIn).Then(Approve()) \
        .ElseIf(Txn.on_completion() == Int(0)).Then(onCall) \
        .Else(Reject())
