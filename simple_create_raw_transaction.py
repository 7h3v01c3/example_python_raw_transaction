import sys
import os
import requests

'''
URGENT DISCLAIMER:
This script and the accompanying guide are intended strictly for educational and learning purposes only.
Utilizing this script improperly or without a full understanding can lead to the irreversible loss of funds.
Always exercise extreme caution and if you're unsure or inexperienced, it's imperative to start with a testnet.
Use entirely at your own risk.
'''

class Config:
    # This class is used to define configurations that the script might need.
    # It currently specifies paths to the cryptocurrency daemon configuration file on various platforms
    # and expected keys in that configuration.

    # Define configuration file paths based on the operating system.
    CONFIG_PATHS = {
        "win": os.path.join(os.getenv('APPDATA'), 'CRYPTO', 'crypto.conf'),
        "darwin": os.path.join(os.path.expanduser("~"), 'Library', 'Application Support', 'CRYPTO', 'crypto.conf'),
        "linux": os.path.join(os.path.expanduser("~"), '.crypto', 'crypto.conf')
    }
    
    # Define the keys we expect to find in the configuration file.
    RPC_KEYS = ["rpcuser", "rpcpassword", "rpcport"]

class FeeEstimator:
    # This class is used to calculate transaction fees based on a given fee-per-UTXO rate.
    
    def __init__(self, per_utxo_fee=0.00001):
        # Initialize with a default fee per UTXO
        self.per_utxo_fee = per_utxo_fee

    def estimate_fee(self, utxo_count):
        # Estimate the total fee based on the number of UTXOs
        return utxo_count * self.per_utxo_fee

def daemon_estimate_fee(blocks=2):
    """Retrieve estimated fee from the daemon for the next 2 blocks."""
    try:
        return rpc_request("estimatefee", [blocks])
    except (OSError, FileNotFoundError, ValueError, ConnectionError) as e:
        # Handle errors gracefully by printing a message and returning None
        print(f"Error retrieving estimated fee from daemon: {e}")
        return None

def format_value(value):
    # This function rounds a value to 8 decimal places, typically used for cryptocurrency amounts
    return round(value, 8)

def get_conf_path():
    # This function determines the appropriate configuration file path based on the operating system.
    for platform, path in Config.CONFIG_PATHS.items():
        if sys.platform.startswith(platform):
            if os.path.exists(path):
                return path
    # If we don't find a configuration path, we raise an error.
    raise FileNotFoundError(f"No configuration file found for platform: {sys.platform}")

def get_rpc_config():
    # This function reads the cryptocurrency daemon configuration file
    # and extracts necessary RPC (Remote Procedure Call) details.
    path = get_conf_path()
    config = {}

    with open(path) as f:
        for line in f:
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            value = value.strip()

            if key in Config.RPC_KEYS:
                if key == "rpcport":
                    # Convert port number to integer
                    config[key] = int(value)
                else:
                    config[key] = value

    return config

def rpc_request(method, params=None):
    # This function sends a request to the cryptocurrency daemon using its RPC interface.
    config = get_rpc_config()
    url = f"http://127.0.0.1:{config['rpcport']}"  # Default localhost for RPC
    headers = {"content-type": "application/json"}

    # Construct the JSON-RPC payload
    payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": method,
        "params": params or []
    }

    # Send the request
    response = requests.post(url, headers=headers, json=payload, auth=(config['rpcuser'], config['rpcpassword']))
    
    if response.status_code != 200:
        # Print server response if it's not a successful one
        print(f"RPC server response: {response.text}")
        raise ConnectionError(f"Failed to connect to the RPC server. Status code: {response.status_code}")

    data = response.json()
    # Check if the RPC response contains an error
    if 'error' in data and data['error'] is not None:
        raise ValueError(f"RPC Error: {data['error']['message']}")

    return data['result']

CHANGE_ADDRESSES = ["ADDRESS"]  # Replace "ADDRESS" with the desired change address(es)

def ask_for_fee():
    # This function asks the user to choose a fee estimation method
    # and then retrieves or calculates the appropriate fee based on the choice.
    print("Select a method for fee estimation:")
    print("1. Use hard-set fee value")
    print("2. Estimate fee using daemon")
    print("3. Manually enter fee")

    while True:
        choice = input("Enter your choice (1/2/3): ")
        if choice == "1":
            estimator = FeeEstimator()
            return estimator.estimate_fee(utxo_count)
        elif choice == "2":
            fee = daemon_estimate_fee()
            if fee:
                return fee
            else:
                print("Error getting fee from daemon. Please choose another method.")
        elif choice == "3":
            while True:
                try:
                    fee = float(input("Enter your desired fee: "))
                    return fee
                except ValueError:
                    print("Please enter a valid fee amount.")
        else:
            print("Invalid choice. Please select 1, 2, or 3.")
def get_unspent_outputs():
    """
    Retrieves a list of all unspent transaction outputs (UTXOs) associated with the user's wallet.

    Returns:
    - A list of UTXOs.

    Note:
    - UTXOs represent spendable funds in a Bitcoin-like cryptocurrency.
    """
    try:
        return rpc_request("listunspent")
    except (OSError, FileNotFoundError, ValueError, ConnectionError) as e:
        print(f"Error retrieving unspent outputs: {e}")
        return []

def select_utxos_for_transaction(amount):
    """
    Selects the required number of UTXOs to cover a specified transaction amount.

    Parameters:
    - amount: Amount of cryptocurrency the user wishes to send.

    Returns:
    - A tuple containing:
      * The selected UTXOs.
      * The total value of the selected UTXOs.
    """
    # Get all available UTXOs
    utxos = get_unspent_outputs()
    selected_utxos, total = [], 0

    # Select UTXOs until we cover the required amount
    for utxo in utxos:
        if total < amount:
            total += utxo['amount']
            selected_utxos.append(utxo)
        else:
            break

    # If the total UTXOs' value is less than the required amount, raise an error.
    if total < amount:
        raise ValueError("Insufficient funds.")
    
    return selected_utxos, total

def create_transaction(destination_address, amount):
    """
    Constructs a raw transaction for a given amount to a specified address.

    Parameters:
    - destination_address: The address where funds should be sent.
    - amount: Amount of cryptocurrency to send.

    Returns:
    - A raw transaction in hexadecimal format.
    """
    # Select UTXOs to fund the transaction
    selected_utxos, total_utxo_amount = select_utxos_for_transaction(amount)

    # Prepare the input structure for the transaction
    inputs = [{"txid": utxo['txid'], "vout": utxo['vout']} for utxo in selected_utxos]

    # Estimate the transaction fee
    estimator = FeeEstimator()
    estimated_fee = format_value(estimator.estimate_fee(len(selected_utxos)))
    fee = ask_for_fee(estimated_fee)

    # Prepare the output structure for the transaction
    outputs = {destination_address: amount}
    change_amount = format_value(total_utxo_amount - amount - fee)

    # If there's a remaining amount after sending and paying the fee, it goes to a change address
    if change_amount > 0:
        print("Select a change address from the list:")
        for i, addr in enumerate(CHANGE_ADDRESSES):
            print(f"{i + 1}. {addr}")
        chosen_idx = int(input("Enter the number corresponding to your desired change address: ")) - 1
        change_address = CHANGE_ADDRESSES[chosen_idx]
        outputs[change_address] = format_value(change_amount)

    # Create the raw transaction
    raw_tx = rpc_request("createrawtransaction", [inputs, outputs])

    # Display transaction details to the user
    print("\nTransaction Details:")
    print(f"Sending To Address: {destination_address}")
    print(f"Sending Amount: {format_value(amount)}")
    print(f"Transaction Fee: {fee}")
    print(f"Change Amount: {change_amount}")
    print(f"Change Address: {change_address if change_amount > 0 else 'No change'}\n")

    return raw_tx

def sign_raw_transaction(raw_tx):
    """
    Signs a raw transaction.

    Parameters:
    - raw_tx: The raw transaction in hexadecimal format.

    Returns:
    - The signed transaction.
    """
    # Use the RPC method to sign the transaction
    signed_tx = rpc_request("signrawtransaction", [raw_tx])
    if 'hex' in signed_tx and 'complete' in signed_tx:
        return signed_tx
    else:
        raise ValueError(f"Unexpected RPC response when signing the transaction: {signed_tx}")

def broadcast_transaction(signed_tx):
    """
    Broadcasts a signed transaction to the network.

    Parameters:
    - signed_tx: The signed transaction.

    Returns:
    - The transaction ID (TXID) if successful.
    """
    txid = rpc_request("sendrawtransaction", [signed_tx['hex']])
    if isinstance(txid, str) and len(txid) == 64:
        return txid
    else:
        raise ValueError(f"Unexpected RPC response: {txid}")

def main():
    """
    Main function for the script. It guides the user through the process of creating,
    signing, and broadcasting a cryptocurrency transaction.
    """
    destination_address = input("Enter the destination address: ")
    amount = float(input("Enter the amount to send (as a float): "))
    raw_tx = create_transaction(destination_address, amount)

    signed_tx = sign_raw_transaction(raw_tx)
    print(f"\nSigned Transaction: {signed_tx['hex']}")

    if signed_tx['complete']:
        user_input = input("Enter 'broadcast' to broadcast the transaction or any other key to exit: ")
        if user_input.lower() == 'broadcast':
            txid = broadcast_transaction(signed_tx)
            print(f"\nTransaction broadcasted. TXID: {txid}")
        else:
            print("Operation cancelled. Exiting.")
    else:
        print("Failed to sign the transaction. Exiting.")

if __name__ == "__main__":
    main()
