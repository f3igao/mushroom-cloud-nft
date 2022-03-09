from pyteal import *


class AppVariables:
    Creator = Bytes("creator")  # Identified the account of the Asset creator, stored globally
    AssetId = Bytes("assetId")  # ID of the asset, stored globally
    amountPayment = Bytes("amount_payment")  # Amount to be paid for the asset, stored locally on the seller's account
    approveTransfer = Bytes("approve_transfer")  # Approval variable, stored on the seller's and the buyer's accounts
    setupSale = Bytes("setup_sale")  # Method call
    buy = Bytes("buy")  # Method call
    executeTransfer = Bytes("execute_transfer")  # Method call
    royaltyFee = Bytes("royalty_fee")  # Royalty fee in thousands
    waitingTime = Bytes("waiting_time")  # Number of rounds to wait before the seller can force the transaction
    claimFees = Bytes("claim_fees")  # Method call
    collectedFees = Bytes("collected_fees")  # Amount of collected fees, stored globally
    refund = Bytes("refund")  # Method call
    roundSaleBegan = Bytes("round_sale_began")  # Round in which the sale began


class DefaultValues:
    RoyaltyFee = int(50)
    WaitingTime = int(15)
    NFTPrice = int(1000000)  # 1 algo
