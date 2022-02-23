from pyteal import *


class AppVariables:
    Creator = Bytes("Creator")  # Identified the account of the Asset creator, stored globally
    AssetId = Bytes("AssetId")  # ID of the asset, stored globally
    amountPayment = Bytes("amountPayment")  # Amount to be paid for the asset, stored locally on the seller's account
    approveTransfer = Bytes("approveTransfer")  # Approval variable, stored on the seller's and the buyer's accounts
    setupSale = Bytes("setupSale")  # Method call
    buy = Bytes("buy")  # Method call
    executeTransfer = Bytes("executeTransfer")  # Method call
    royaltyFee = Bytes("royaltyFee")  # Royalty fee in thousands
    waitingTime = Bytes("waitingTime")  # Number of rounds to wait before the seller can force the transaction
    claimFees = Bytes("claimFees")  # Method call
    collectedFees = Bytes("collectedFees")  # Amount of collected fees, stored globally
    refund = Bytes("refund")  # Method call
    roundSaleBegan = Bytes("roundSaleBegan")  # Round in which the sale began
