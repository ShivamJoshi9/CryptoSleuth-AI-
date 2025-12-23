import networkx as nx
import pandas as pd

class GraphBuilder:
    def __init__(self):
        self.G = nx.DiGraph()

    def build_graph(self, df):
        """
        Build a directed graph from transaction dataframe.
        Required columns: ['from', 'to', 'value', 'timeStamp']
        """
        for _, row in df.iterrows():
            sender = row["from"]
            receiver = row["to"]

            # Add wallets as nodes
            self.G.add_node(sender, type="wallet")
            self.G.add_node(receiver, type="wallet")

            # Add transaction as edge
            self.G.add_edge(
                sender,
                receiver,
                value=float(row["value"]),
                time=row["timeStamp"],
                tx_hash=row.get("hash", None)
            )
        return self.G

    def label_entities(self, scam_list, exchange_list):
        """
        Label nodes as 'scam' or 'exchange' based on provided lists.
        """
        for node in self.G.nodes:
            if node in scam_list:
                self.G.nodes[node]['type'] = 'scam'
            elif node in exchange_list:
                self.G.nodes[node]['type'] = 'exchange'

    def trace_path(self, source, target):
        """
        Find shortest path between two wallets.
        """
        try:
            return nx.shortest_path(self.G, source, target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def expand_wallet(self, wallet, depth=None, outermost_only=False):
        """
        Expand wallet connections.

        Args:
            wallet (str): Starting wallet address.
            depth (int or None): Max depth to explore. If None, explore all reachable nodes.
            outermost_only (bool): If True, return only the wallets at the max depth reached.

        Returns:
            dict or list: 
                - If outermost_only=False -> dict {wallet: distance}
                - If outermost_only=True  -> list of wallets at the max distance
        """
        if wallet not in self.G.nodes:
            return "Wallet not found"
        
        distances = nx.single_source_shortest_path_length(self.G, wallet, cutoff=depth)

        if outermost_only and distances:
            max_dist = max(distances.values())
            return [node for node, dist in distances.items() if dist == max_dist]

        return distances    

     
    def trace_to_all_exchanges(self, start_node, exchange_list, cutoff=5):
        """
        Returns ALL simple paths from start_node to any exchange in exchange_list.
        Includes all intermediate wallets in those paths.

        Args:
            start_node (str): The wallet address to trace from.
            exchange_list (list): List of exchange wallet addresses.
            cutoff (int): Maximum path length to explore (default = 5).
        
        Returns:
            dict: {exchange_wallet: [list_of_paths]}
        """
        if start_node not in self.G:
            return "Start node not found in graph"

        all_paths = {}
        for exchange in exchange_list:
            if exchange in self.G:
                paths = list(nx.all_simple_paths(self.G, start_node, exchange, cutoff=cutoff))
                if paths:
                    all_paths[exchange] = paths

        if not all_paths:
            return "No exchanges found from this start wallet"

        return all_paths



if __name__ == "__main__":
    # Load CSV file
    df = pd.read_csv("data/raw/sample_wallet.csv")

    gb = GraphBuilder()
    G = gb.build_graph(df)

    # Example lists
    scams = ["0xScamWallet1"]
    exchanges = [
        # Binance
        "0xF977814e90dA44bFA03b6295A0616a897441aceC",
        "0x564286362092D8e7936f0549571a803B203aAceD",
        "0x3f5CE5FBFe3E9af3971dD833D26BA9b5C936f0bE",

        # Coinbase
        "0x503828976D22510aad0201ac7EC88293211D23Da",
        "0x71660C4005BA85c37Ccec55d0C4493E66Fe775d3",

        # Kraken
        "0x0A869d79a7052C7f1b55a8EbAbbFcD44cF5fB80f",
        "0x2910543Af39aba0Cd09dBb2D50200b3E800A63D2",

        # Gemini
        "0x61EDCDf5eF8F8F8F8F8F8F8F8F8F8F8F8F8F8F8F",
        "0x183bC6C7ef385038cc39D61c9D8dF4F92F90218d",

        # Bitfinex
        "0xE92d1A43A43A43A43A43A43A43A43A43A43A43A43",
        "0xABAF05A0d6a98b4CcB01fA0F2D70f2A28A444d0F",

        # OKX
        "0x5C985E89De07Deb1fFfB61F276eC8C7aF0E87f5d",
        "0x9A3f5e0bFf5C57B2c4dD3F76811C7Ff1eE3bBa97",

        # Huobi
        "0x1062a747393198f70F71ec65A582423Dba7E5Ab3",
        "0x80C62FE4487E1351b47Ba49809EBD60ED085bf52",

        # KuCoin
        "0x2b5634C42055806a59e9107ED44D43c426E58258",
        "0x689c56aef474Df92D44A1B70850f808488F9769C",

        # Poloniex
        "0x32Be343B94f860124dC4fEe278FDCBD38C102D88",

        # Gate.io
        "0x3e5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9",

        # Bittrex
        "0xFbb1b73C4f0Bda4f67dca266ce6Ef42f520fBB98",

        # Bybit
        "0x1d9F4dF2BffA255dfBEc2a7790a739E8e01Dd5b0",
    ]

    gb.label_entities(scams, exchanges)

    # Choose a wallet that exists in your CSV
    start_wallet = df.iloc[0]["from"]

    print("total_wallets:", len(G.nodes()), "total_transaction:", len(G.edges()))
    print()
    print("Trace Path Example:", gb.trace_path(start_wallet, df.iloc[0]["to"]))
    print()
    print("Expand Wallet Example:", gb.expand_wallet(start_wallet, depth=4))
    print()

    # # Full expansion (all reachable wallets)
    # all_reachable = gb.expand_wallet(start_wallet)
    # print("All Reachable:", all_reachable)
    # print()

    # # Expansion limited to 3 hops
    # limited = gb.expand_wallet(start_wallet, depth=3)
    # print("Up to depth 3:", limited)
    # print()

    # # Only the outermost wallets (farthest ones from start)
    # outermost = gb.expand_wallet(start_wallet, outermost_only=True)
    # print("Outermost wallets:", outermost)
    # print()

    paths = gb.trace_to_all_exchanges(start_wallet, exchanges, cutoff=6)

    if isinstance(paths, dict):
        for ex, p_list in paths.items():
            print(f"\nExchange: {ex}")
            for p in p_list:
                print(" -> ".join(p))
    else:
        print(paths)  # Just print the error message
