# `simple_create_raw_transaction.py`

> **Disclaimer**: This script and the accompanying guide are intended for educational and learning purposes only. Always exercise caution when working with real funds and always backup your wallets.

`simple_create_raw_transaction.py` is a Python script designed for those who wish to grasp the basics of creating, signing, and broadcasting raw transactions in Bitcoin-based cryptocurrencies. This tool offers a beginner-friendly introduction to raw transactions while still retaining a modicum of customization for the more experienced user.

## **Prerequisites**

- **Python 3.x**
    - Ensure Python 3.x is installed. Verify your Python version by running:
      ```
      python --version
      ```
      in your terminal.

- **requests library**
    - Essential for API interactions. Install with:
      ```bash
      pip install requests
      ```

## **Instructions**

### 1. **Environment Setup**
    - Prior to deploying this tool, make sure you have a functioning Bitcoin (or Bitcoin-derivative) node on your machine with RPC enabled for interfacing.

### 2. **Configuring Change Addresses**
    - Prior to initiating any transaction, configure your change address within the script. This is a pivotal step as any surplus funds from the UTXOs (minus the fees) will be forwarded to this address.
    ```python
    CHANGE_ADDRESSES = ["YOUR_CHANGE_ADDRESS_HERE"]
    ```
    Substitute `YOUR_CHANGE_ADDRESS_HERE` with your actual change address.

### 3. **Executing the Script**
    - Navigate to the directory housing `simple_create_raw_transaction.py` and initiate with:
    ```bash
    python simple_create_raw_transaction.py
    ```
    Engage with the prompts to enter the recipient address, determine the amount to forward, and finalize transaction fees.

### 4. **Transaction Fees - A Primer**
    - By default, this script predicts transaction fees based on the quantity of UTXOs involved. You do, however, retain the choice to substitute this projected fee with a bespoke amount during the transaction generation phase.

## **Recommendations**

### - **Testnet: A Safer Alternative for Beginners**
    If you're just dipping your toes into the world of raw transactions, we highly recommend commencing your journey on a testnet before progressing to the mainnet. The testnet offers a fail-safe environment, enabling you to grasp the nuances of the process sans the risks associated with the mainnet.

### - **Change Address: An Oft-Overlooked Necessity**
    Always assign a change address, even if you feel it's redundant. The realm of raw transactions, while fascinating, is also fraught with potential pitfalls. Neglecting to specify a change address could result in the inadvertent loss of funds, which might be interpreted as transaction fees. Always, always pore over the transaction specifics prior to broadcasting, paying special attention to the transaction fees and the change tally.

## **Join the Cause!**
    Wish to contribute? Excellent! Simply fork the repository on GitHub, introduce your enhancements or tweaks, and submit a pull request. Active community engagement is instrumental in refining tools and ensuring they cater to a broad spectrum of user requirements.
