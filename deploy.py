from dotenv import load_dotenv

load_dotenv()
# import solcx
from solcx import compile_standard
import json
from web3 import Web3
import os

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    # print(simple_storage_file)

# install_solc('0.8.0')
compile_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.0",
)


with open("compiled_code.json", "w") as file:
    json.dump(compile_sol, file)

bytecode = compile_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]
abi = compile_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecting to ganache
# w3 = Web3
w3 = Web3(Web3.HTTPProvider(os.getenv("INFURA_RINKEBY_ENDPOINT")))
chain_id = int(os.getenv("RINKEBY_CHAIN_ID"))
my_address = os.getenv("RINKEBY_DEPLOYER_ADDRESS")
private_key = os.getenv("RINKEBY_PRIVATE_KEY")


"""
DEPLOY CONTRACT
"""
print("--------Deploying Contract ----------")
# # # Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# # print(SimpleStorage)
nonce = w3.eth.getTransactionCount(my_address)
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# print(signed_txn)
# send the signed transaction

tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("--------Deployed Contract ----------")

# print(tx_receipt)
"""
DEPLOY CONTRACT
"""
# simple_storage = w3.eth.contract(address=os.getenv("CONTRACT_ADDRESS"), abi=abi)
simple_storage = w3.eth.contract(tx_receipt.contractAddress, abi=abi)

store_transaction = simple_storage.functions.store(15).buildTransaction({
    'chainId':chain_id,
    'from':my_address,
    'nonce':nonce + 1,
})
signed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

print(simple_storage.functions.retrieve().call())
# print(simple_storage.functions.store(15).call())
# print(simple_storage.functions.retrieve().call())
