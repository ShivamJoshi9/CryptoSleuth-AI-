from etherscan import Etherscan
import pandas as pd
import re

class DataPipeline:
    def __init__(self, api_key):
        self.eth = Etherscan(api_key)

    def is_valid_wallet(self, wallet):
        """
        Validate Ethereum wallet address.
        - Must start with 0x
        - Must be 42 characters long
        - Must contain only hex digits after 0x
        """
        if not isinstance(wallet, str):
            return False
        if not wallet.startswith("0x"):
            return False
        if len(wallet) != 42:
            return False
        if not re.fullmatch(r"0x[0-9a-fA-F]{40}", wallet):
            return False
        return True

    def fetch_transactions(self, wallet, start_block=0, end_block=99999999):
        """
        Fetch normal transactions for a given wallet.
        """
        if not self.is_valid_wallet(wallet):
            raise ValueError(f"Invalid Ethereum wallet address: {wallet}")

        txs = self.eth.get_normal_txs_by_address(
            wallet,
            startblock=start_block,
            endblock=end_block,
            sort="asc"
        )

        if not txs:
            raise ValueError(f"No transactions found for wallet: {wallet}")

        df = pd.DataFrame(txs)
        return df


if __name__ == "__main__":
    API_KEY = "X741C9XNHGG57BZ1A1S91EYBKRAP689WTD"
    dp = DataPipeline(API_KEY)

    # ✅ Valid Binance hot wallet
    wallet = "0x7edC34a8aC87232c743F46b013795233E911C0B3"

    try:
        df = dp.fetch_transactions(wallet)
        print(df.head())
        df.to_csv("data/raw/sample_wallet.csv", index=False)
    except Exception as e:
        print("Error:", e)


# from etherscan import Etherscan
# import pandas as pd

# class DataPipeline:
#     def __init__(self, api_key):
#         self.eth = Etherscan(api_key)



#     def fetch_transactions(self, wallet, start_block=0, end_block=99999999):
#         txs = self.eth.get_normal_txs_by_address(wallet, startblock=start_block, endblock=end_block, sort="asc")
#         df = pd.DataFrame(txs)
#         return df

# if __name__ == "__main__":
#     API_KEY = "X741C9XNHGG57BZ1A1S91EYBKRAP689WTD"
#     dp = DataPipeline(API_KEY)
#     df = dp.fetch_transactions("0x5a4dd746c1f77cc62933e269c466b4b8d90c85ee4f92a76676df15de9ae2d1f1")  # Example: Bitfinex wallet
#     print(df.head())
#     df.to_csv("data/raw/sample_wallet.csv", index=False)

# Initialize with your API key

# user wallet : 0xde7adbb368c2616df8c5c0e986933bee8f660add
# sample wallet : 0x742d35Cc6634C0532925a3b844Bc454e4438f44e

# YOUR_ETHERSCAN_API_KEY = 'X741C9XNHGG57BZ1A1S91EYBKRAP689WTD'
# eth = Etherscan(YOUR_ETHERSCAN_API_KEY)

# Example: Get the balance of an address
# balance = eth.get_eth_balance("0x7b93790994eb1ce7c27ee893c3b513da9ea2c9fa238b0ef2ae606fd1e587fadd")
# print(balance)
