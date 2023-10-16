# `simple_create_raw_transaction.py`

`simple_create_raw_transaction.py` is a Python script that facilitates the creation, signing, and broadcasting of raw transactions for Bitcoin-based cryptocurrencies. This tool offers a simplified approach to working with raw transactions while still allowing some customizations.

## **Prerequisites**

- **Python 3.x**
    - You need to have Python 3 installed on your machine. You can verify the version using `python --version` in your terminal.
- **requests library**
    - Required for making API requests. Install using:
      ```bash
      pip install requests
      ```

## **Instructions**

### 1. **Setting up your environment**
    Before using this tool, ensure you have a running Bitcoin-based cryptocurrency node on your system. The node should have RPC enabled for interaction.

### 2. **Configuring your change address**
    Before initiating a transaction, set your change address in the script. This is crucial as any excess funds (excluding the fees) from the UTXOs used will be sent to this address.
    ```python
    CHANGE_ADDRESSES = ["YOUR_CHANGE_ADDRESS"]
    ```
    Replace `YOUR_CHANGE_ADDRESS` with your actual change address.

### 3. **Running the script**
    Navigate to the directory where you saved the `simple_create_raw_transaction.py` and run:
    ```bash
    python simple_create_raw_transaction.py
    ```
    Follow the interactive prompts to enter the destination address, the amount you want to send, and decide on transaction fees.

### 4. **Understanding fees**
    By default, the script estimates fees based on the number of UTXOs utilized. However, you have the option to override this estimated fee with a custom amount during the transaction creation process.

## **Recommendations**

### - **Using Testnet for Learning**
    If you're unfamiliar with raw transactions or just getting started, it's strongly recommended to practice on a testnet before using mainnet. This allows for a risk-free environment to understand the process and ensure you're confident in using the tool.

### - **Understanding the Importance of a Change Address**
    Always set a change address, even if you don't anticipate using it. When creating transactions, especially raw transactions, it's easy to make mistakes. If you don't specify a change address, you risk losing excess funds as they could be consumed as fees. Always review the transaction details before broadcasting, especially the transaction fees and the change amount.

## **Contribution**
    Feel free to fork the repository on GitHub, make improvements or adjustments, and submit a pull request. Community contributions help in refining tools and ensuring they cater to various user requirements.

