import json
import os
from web3 import Web3
from eth_account import Account

# Constants
INFURA_URL = "https://mainnet.infura.io/v3/d078940287f845e5afe7e016bb49369b"  
PRIVATE_KEY_MAIN_WALLET=0xee9cec01ff03c0adea731d7c5a84f7b412bfd062b9ff35126520b3eb3d5ff258
USDT_CONTRACT_ADDRESS =0xdac17f958d2ee523a2206206994597c13d831ec7  # USDT contract address
GAS_WALLET_ADDRESS = None  # Will be generated later
DESTINATION_WALLET_ADDRESS = 0x551510dFb352bf6C0fCC50bA7Fe94cB1d2182654  
AMOUNT_USDT = 2300  # Amount of USDT to send
GAS_FEE_ETH = 0.001  # Gas fee in ETH (This amount should be enough to pay for the transaction)

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Ensure we're connected to the Ethereum network
if not web3.isConnected():
    print("Error: Unable to connect to Ethereum node.")
    exit()

# 1. Generate a new Ethereum address for gas fees
def generate_new_address():
    # Generate a new Ethereum account (private key and address)
    account = Account.create()
    return account.privateKey.hex(), account.address

# 2. Transfer ETH to the new gas wallet
def transfer_eth_for_gas(from_private_key, to_address, amount_eth):
    # Load the main wallet
    main_account = Account.privateKeyToAccount(from_private_key)
    
    # Convert ETH amount to Wei
    amount_wei = web3.toWei(amount_eth, 'ether')
    
    # Prepare the transaction
    nonce = web3.eth.getTransactionCount(main_account.address)
    gas_price = web3.eth.gas_price
    gas_limit = 21000  # Standard gas limit for a simple ETH transfer

    tx = {
        'nonce': nonce,
        'to': to_address,
        'value': amount_wei,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'chainId': 1,  # Mainnet
    }

    # Sign the transaction
    signed_tx = web3.eth.account.signTransaction(tx, private_key=from_private_key)

    # Send the transaction
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    return tx_hash

# 3. Transfer USDT from the main wallet to the destination wallet
def transfer_usdt(private_key, to_address, amount_usdt):
    # Load the main wallet
    main_account = Account.privateKeyToAccount(private_key)
    
    # Create the contract instance
    usdt_contract = web3.eth.contract(address=USDT_CONTRACT_ADDRESS, abi=json.loads('[...]'))  # Replace with actual ABI of USDT
    
    # Prepare the transaction
    nonce = web3.eth.getTransactionCount(main_account.address)
    gas_price = web3.eth.gas_price
    gas_limit = 100000  # Estimated gas limit for ERC-20 transfer
    
    # Build the transfer transaction
    tx = usdt_contract.functions.transfer(to_address, amount_usdt * 10**6).buildTransaction({
        'chainId': 1,  # Mainnet
        'gas': gas_limit,
        'gasPrice': gas_price,
        'nonce': nonce,
    })

    # Sign the transaction
    signed_tx = web3.eth.account.signTransaction(tx, private_key=private_key)

    # Send the transaction
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    return tx_hash

# Main process
def main():
    # Step 1: Generate a new address for gas
    gas_private_key, gas_wallet_address = generate_new_address()
    print(f"Generated new address for gas wallet: {gas_wallet_address}")
    
    # Step 2: Transfer ETH to the new gas wallet
    print("Transferring ETH to the gas wallet...")
    eth_tx_hash = transfer_eth_for_gas(PRIVATE_KEY_MAIN_WALLET, gas_wallet_address, GAS_FEE_ETH)
    print(f"ETH transfer successful. TX Hash: {web3.toHex(eth_tx_hash)}")
    
    # Step 3: Transfer USDT to the destination wallet
    print(f"Transferring {AMOUNT_USDT} USDT to {DESTINATION_WALLET_ADDRESS}...")
    usdt_tx_hash = transfer_usdt(PRIVATE_KEY_MAIN_WALLET, DESTINATION_WALLET_ADDRESS, AMOUNT_USDT)
    print(f"USDT transfer successful. TX Hash: {web3.toHex(usdt_tx_hash)}")


if __name__ == "__main__":
    main()