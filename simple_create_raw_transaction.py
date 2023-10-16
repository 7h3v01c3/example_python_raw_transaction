import sys
import os
import requests

class Config:
    # Make these configurations based on the target cryptocurrency
    CONFIG_PATHS = {
        "win": os.path.join(os.getenv('APPDATA'), 'CRYPTO', 'crypto.conf'),
        "darwin": os.path.join(os.path.expanduser("~"), 'Library', 'Application Support', 'CRYPTO', 'crypto.conf'),
        "linux": os.path.join(os.path.expanduser("~"), '.crypto', 'crypto.conf')
    }
    
    RPC_KEYS = ["rpcuser", "rpcpassword", "rpcport"]

class FeeEstimator:
    def __init__(self, per_utxo_fee=0.00001):
        self.per_utxo_fee = per_utxo_fee

    def estimate_fee(self, utxo_count):
        return utxo_count * self.per_utxo_fee
		
def daemon_estimate_fee(blocks=2):
    """Retrieve estimated fee from the daemon for the next 2 blocks."""
    try:
        return rpc_request("estimatefee", [blocks])
    except (OSError, FileNotFoundError, ValueError, ConnectionError) as e:
        print(f"Error retrieving estimated fee from daemon: {e}")
        return None


def format_value(value):
    return round(value, 8)  # Format to 8 decimal places

def get_conf_path():
    for platform, path in Config.CONFIG_PATHS.items():
        if sys.platform.startswith(platform):
            if os.path.exists(path):
                return path

    raise FileNotFoundError(f"No configuration file found for platform: {sys.platform}")

def get_rpc_config():
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
                    config[key] = int(value)
                else:
                    config[key] = value

    return config

def rpc_request(method, params=None):
    config = get_rpc_config()
    url = f"http://127.0.0.1:{config['rpcport']}"
    headers = {"content-type": "application/json"}
    payload = {
        "jsonrpc": "1.0",
        "id": "python",
        "method": method,
        "params": params or []
    }
    response = requests.post(url, headers=headers, json=payload, auth=(config['rpcuser'], config['rpcpassword']))
    
    if response.status_code != 200:
        print(f"RPC server response: {response.text}")
        raise ConnectionError(f"Failed to connect to the RPC server. Status code: {response.status_code}")

    data = response.json()
    if 'error' in data and data['error'] is not None:
        raise ValueError(f"RPC Error: {data['error']['message']}")

    return data['result']

CHANGE_ADDRESSES = ["ADDRESS"]


def ask_for_fee():
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
    try:
        return rpc_request("listunspent")
    except (OSError, FileNotFoundError, ValueError, ConnectionError) as e:
        print(f"Error retrieving unspent outputs: {e}")
        return []

def select_utxos_for_transaction(amount):
    utxos = get_unspent_outputs()
    selected_utxos, total = [], 0
    for utxo in utxos:
        if total < amount:
            total += utxo['amount']
            selected_utxos.append(utxo)
        else:
            break
    if total < amount:
        raise ValueError("Insufficient funds.")
    return selected_utxos, total

def create_transaction(destination_address, amount):
    selected_utxos, total_utxo_amount = select_utxos_for_transaction(amount)

    inputs = [{"txid": utxo['txid'], "vout": utxo['vout']} for utxo in selected_utxos]
    estimator = FeeEstimator()
    estimated_fee = format_value(estimator.estimate_fee(len(selected_utxos)))
    fee = ask_for_fee(estimated_fee)

    outputs = {destination_address: amount}
    change_amount = format_value(total_utxo_amount - amount - fee)
    
    if change_amount > 0:
        print("Select a change address from the list:")
        for i, addr in enumerate(CHANGE_ADDRESSES):
            print(f"{i + 1}. {addr}")
        chosen_idx = int(input("Enter the number corresponding to your desired change address: ")) - 1
        change_address = CHANGE_ADDRESSES[chosen_idx]
        outputs[change_address] = format_value(change_amount)

    raw_tx = rpc_request("createrawtransaction", [inputs, outputs])

    print("\nTransaction Details:")
    print(f"Sending To Address: {destination_address}")
    print(f"Sending Amount: {format_value(amount)}")
    print(f"Transaction Fee: {fee}")
    print(f"Change Amount: {change_amount}")
    print(f"Change Address: {change_address if change_amount > 0 else 'No change'}\n")

    return raw_tx

def sign_raw_transaction(raw_tx):
    signed_tx = rpc_request("signrawtransaction", [raw_tx])
    if 'hex' in signed_tx and 'complete' in signed_tx:
        return signed_tx
    else:
        raise ValueError(f"Unexpected RPC response when signing the transaction: {signed_tx}")

def broadcast_transaction(signed_tx):
    txid = rpc_request("sendrawtransaction", [signed_tx['hex']])
    if isinstance(txid, str) and len(txid) == 64:
        return txid
    else:
        raise ValueError(f"Unexpected RPC response: {txid}")

def main():
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
