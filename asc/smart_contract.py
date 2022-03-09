from services.consts import AppVariables
from subroutines import *


def approval_program():
    service_cost = Int(2) * Global.min_txn_fee()  # cost of 2 inner transactions
    # [step 1] initialize smart contract; called only at creation
    royalty_fee = Btoi(Txn.application_args[2])
    asset_decimals = AssetParam.decimals(Btoi(Txn.application_args[1]))
    asset_frozen = AssetParam.defaultFrozen(Btoi(Txn.application_args[1]))
    initialize = Seq([
        Assert(Txn.type_enum() == TxnType.ApplicationCall),  # ensure type is an application call
        Assert(Txn.application_args.length() == Int(4)),  # check for 4 args: creator, assetId, royaltyFee, roundWait
        Assert(Int(0) < royalty_fee <= Int(1000)),  # verify royalty_fee is between 0 and 1000
        default_transaction_checks(Int(0)),  # call default transaction checks
        asset_decimals,  # load the asset decimals
        Assert(asset_decimals.hasValue()),
        Assert(asset_decimals.value() == Int(0)),  # verify that there are no decimal
        # asset_frozen,  # load the frozen parameter of the asset
        # Assert(asset_frozen.hasValue()),
        # Assert(asset_frozen.value() == Global.current_application_address()),  # verify the freeze address is contract
        # Assert(asset_frozen.value() == Int(0)),  # verify that the asset is not frozen
        App.globalPut(AppVariables.Creator, Txn.application_args[0]),  # save the initial creator
        App.globalPut(AppVariables.AssetId, Btoi(Txn.application_args[1])),  # save the asset ID
        App.globalPut(AppVariables.royaltyFee, royalty_fee),  # save the royalty fee
        App.globalPut(AppVariables.waitingTime, Btoi(Txn.application_args[3])),  # save waitingTime in number of rounds
        Approve()
    ])

    # [step 2] set up NFT sale with two arguments:
    #   1. the command to execute, in this case "setup_sale"
    #   2. payment amount
    # first verify the seller owns the NFT, then locally save the arguments
    price = Btoi(Txn.application_args[1])
    # asset_clawback = AssetParam.clawback(App.globalGet(AppVariables.AssetId))
    # asset_freeze = AssetParam.freeze(App.globalGet(AppVariables.AssetId))
    setup_sale = Seq([
        # Assert(Txn.application_args.length() == Int(2)),  # check that there are 2 arguments
        # Assert(Global.group_size() == Int(1)),  # verify that it is only 1 transaction
        default_transaction_checks(Int(0)),  # perform default transaction checks
        Assert(price > Int(0)),  # check that the price is greater than 0
        # asset_clawback,  # verify that the clawback address is the contract
        # Assert(asset_clawback.hasValue()),
        # Assert(asset_clawback.value() == Global.current_application_address()),
        # asset_freeze,  # verify that the freeze address is the contract
        # Assert(asset_freeze.hasValue()),
        # Assert(asset_freeze.value() == Global.current_application_address()),
        check_nft_balance(Txn.sender(), App.globalGet(AppVariables.AssetId)),  # verify that the seller owns the NFT
        Assert(price > service_cost),  # check that the price is greater than the service cost
        App.localPut(Txn.sender(), AppVariables.amountPayment, price),  # save the price
        App.localPut(Txn.sender(), AppVariables.approveTransfer, Int(0)),  # reject transfer until payment is done
        Approve()
    ])

    # [step 3] approve the payment with two transactions:
    # first transaction is a NoOp App call transaction requiring 2 arguments:
    #   1. command to execute, in this case "buy"
    #   2. asset id
    # also pass the seller's address into first transaction
    # second transaction is a payment (the receiver is the app)
    seller = Gtxn[0].accounts[1]  # get seller's address
    amt_to_pay = App.localGet(seller, AppVariables.amountPayment)  # get amount to be paid
    approval = App.localGet(seller, AppVariables.approveTransfer)  # check if the transfer has alraedy been approved
    buyer = Gtxn[0].sender()
    buy = Seq([
        # Assert(Gtxn[0].application_args.length() == Int(2)),  # check that there are 2 arguments
        # Assert(Global.group_size() == Int(2)),  # check that there are 2 transactions
        # Assert(Gtxn[1].type_enum() == TxnType.Payment),  # check that the second transaction is a payment
        Assert(App.globalGet(AppVariables.AssetId) == Btoi(Gtxn[0].application_args[1])),  # ensure correct assetId
        Assert(approval == Int(0)),  # check that the transfer has not been issued yet
        Assert(amt_to_pay == Gtxn[1].amount()),  # check that the amount to be paid is correct
        Assert(Global.current_application_address() == Gtxn[1].receiver()),  # ensure payment receiver is current app
        # default_transaction_checks(Int(0)),  # perform default transaction checks
        # default_transaction_checks(Int(1)),  # perform default transaction checks
        check_nft_balance(seller, App.globalGet(AppVariables.AssetId)),  # check that the seller owns the NFT
        Assert(buyer != seller),  # make sure the seller is not the buyer
        App.localPut(seller, AppVariables.approveTransfer, Int(1)),  # approve the transfer from seller' side
        App.localPut(buyer, AppVariables.approveTransfer, Int(1)),  # approve the transfer from buyer' side
        App.localPut(seller, AppVariables.roundSaleBegan, Global.round()),  # save the round number
        Approve()
    ])

    # [step 4] transfer the NFT: pay the seller and send royalty fees to the creator(s),
    # requires a NoOp App call transaction, with 1 argument:
    #   1. command to execute, in this case "execute_transfer"
    # also account for the service_cost to pay the inner transaction
    royalty_fee = App.globalGet(AppVariables.royaltyFee)
    collected_fees = App.globalGet(AppVariables.collectedFees)
    fees_to_pay = ScratchVar(TealType.uint64)
    execute_transfer = Seq([
        Assert(Gtxn[0].application_args.length() == Int(1)),  # check that there is only 1 argument
        Assert(Global.group_size() == Int(1)),  # check that is only 1 transaction
        default_transaction_checks(Int(0)),  # perform default transaction checks
        Assert(App.localGet(seller, AppVariables.approveTransfer) == Int(1)),  # approval is set to 1 on seller side
        # check approval from buyer' side, alternatively, seller can force transaction if enough time has passed
        Assert(Or(And(seller != buyer, App.localGet(buyer, AppVariables.approveTransfer) == Int(1)),
                  Global.round() > App.globalGet(AppVariables.waitingTime) + App.localGet(seller,
                                                                                          AppVariables.roundSaleBegan))),
        Assert(service_cost < amt_to_pay),  # check underflow
        check_nft_balance(seller, App.globalGet(AppVariables.AssetId)),  # check that the seller owns the NFT
        # reduce number of subroutine calls by saving the variable inside a `temp` variable
        fees_to_pay.store(If(seller == App.globalGet(AppVariables.Creator)).Then(Int(1)).Else(
            compute_royalty_fee(amt_to_pay - service_cost, royalty_fee))),
        # compute royalty fees: if the seller is the creator, the fees are 0
        Assert(Int(2 ** 64 - 1) - fees_to_pay.load() >= amt_to_pay - service_cost),  # check overflow on payment
        Assert(Int(2 ** 64 - 1) - collected_fees >= fees_to_pay.load()),  # check overflow on collected fees
        Assert(amt_to_pay - service_cost > fees_to_pay.load()),
        transfer_asset(seller, Gtxn[0].sender(), App.globalGet(AppVariables.AssetId)),  # transfer asset
        send_payment(seller, amt_to_pay - service_cost - fees_to_pay.load()),  # pay seller
        App.globalPut(AppVariables.collectedFees, collected_fees + fees_to_pay.load()),  # collect fees
        App.localDel(seller, AppVariables.amountPayment),  # delete local variables
        App.localDel(seller, AppVariables.approveTransfer),
        App.localDel(buyer, AppVariables.approveTransfer),
        Approve()
    ])

    # [refund sequence]
    # buyer can get a refund if the payment has already been done but the NFT has not been transferred yet
    refund = Seq([
        Assert(Global.group_size() == Int(1)),  # verify that it is only 1 transaction
        Assert(Txn.application_args.length() == Int(1)),  # check that there is only 1 argument
        default_transaction_checks(Int(0)),  # perform default transaction checks
        Assert(buyer != seller),  # assert that the buyer is not the seller
        Assert(App.localGet(seller, AppVariables.approveTransfer) == Int(1)),  # assert payment has already been done
        Assert(App.localGet(buyer, AppVariables.approveTransfer) == Int(1)),
        Assert(amt_to_pay > Global.min_txn_fee()),
        # underflow check: verify that the amount is greater than the transaction fee
        send_payment(buyer, amt_to_pay - Global.min_txn_fee()),  # refund buyer
        App.localPut(seller, AppVariables.approveTransfer, Int(0)),  # reset local variables
        App.localDel(buyer, AppVariables.approveTransfer),
        Approve()
    ])

    # [claim fees sequence]
    # sequence can be called only by the creator, used to claim all the royalty fees
    # may fail if the contract does not have enough algo to pay the inner transaction
    # (the creator should take care of funding the contract in this case)
    claim_fees = Seq([
        Assert(Global.group_size() == Int(1)),  # Verify that it is only 1 transaction
        Assert(Txn.application_args.length() == Int(1)),  # Check that there is only 1 argument
        default_transaction_checks(Int(0)),  # Perform default transaction checks
        Assert(Txn.sender() == App.globalGet(AppVariables.Creator)),  # Verify that the sender is the creator
        Assert(App.globalGet(AppVariables.collectedFees) > Int(0)),  # Check that there are enough fees to collect
        send_payment(App.globalGet(AppVariables.Creator), App.globalGet(AppVariables.collectedFees)),  # Pay creator
        App.globalPut(AppVariables.collectedFees, Int(0)),  # Reset collected fees
        Approve()
    ])

    # [call sequence]
    # checks that the first transaction is an Application call, and that there is at least 1 argument
    # then checks the first argument of the call, the first argument must be a valid value between
    # "setup_sale", "buy", "execute_transfer", "refund" and "claimFees"
    on_call = If(Or(Txn.type_enum() != TxnType.ApplicationCall, Txn.application_args.length() == Int(0))).Then(
        Reject()).ElseIf(Txn.application_args[0] == AppVariables.setupSale).Then(setup_sale).ElseIf(
        Txn.application_args[0] == AppVariables.buy).Then(buy).ElseIf(
        Txn.application_args[0] == AppVariables.executeTransfer).Then(execute_transfer).ElseIf(
        Txn.application_args[0] == AppVariables.refund).Then(refund).ElseIf(
        Txn.application_args[0] == AppVariables.claimFees).Then(claim_fees).Else(Reject())

    # check the transaction type and execute the corresponding code
    #   1. if application_id() is 0 then the program has just been created, so initialize it
    #   2. if on_completion() is 0, execute the on_call code
    return If(Txn.application_id() == Int(0)).Then(initialize).ElseIf(Txn.on_completion() == OnComplete.CloseOut).Then(
        Approve()).ElseIf(Txn.on_completion() == OnComplete.OptIn).Then(Approve()).ElseIf(
        Txn.on_completion() == Int(0)).Then(on_call).Else(Reject())


def clear_program():
    return Approve()

# if __name__ == "__main__":
#     # Compiles the approval program
#     with open(sys.argv[1], "w+") as f:
#         compiled = compileTeal(approval_program(), mode=Mode.Application, version=5)
#         f.write(compiled)
#
#     # Compiles the clear program
#     with open(sys.argv[2], "w+") as f:
#         compiled = compileTeal(clear_program(), mode=Mode.Application, version=5)
#         f.write(compiled)
