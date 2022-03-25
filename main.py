from algosdk import v2client

from asc.asset_sale_contract import asset_sale_contract

# endpoint = 'https://node.algoexplorerapi.io'
endpoint = 'https://node.testnet.algoexplorerapi.io'
algod_client = v2client.algod.AlgodClient("", endpoint, "")


def main(request):
    headers = {
        "Access-Control-Allow-Origin": "*",
    }
    if request.method == "OPTIONS":
        return "", 204, headers
    seller = request.args.get("seller")
    asset = int(request.args.get("asset"))
    price = int(request.args.get("price"))
    contract_teal = asset_sale_contract(seller, asset, price)
    contract_compiled = algod_client.compile(contract_teal)
    contract_result = contract_compiled["result"]
    return contract_result, 200, headers
