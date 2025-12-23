# src/nlp_interface.py

"""
NLP → Graph Query Translator
This module maps simple natural language queries to GraphBuilder functions.
"""

import sys
import os
import pandas as pd

# Ensure src/ is in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graph_builder import GraphBuilder

def parse_query(query: str, gb: GraphBuilder, exchanges: list):
    """
    Parse a natural language query and call the corresponding graph function.
    """
    query = query.lower().strip()

    # Trace all transactions from a wallet until any exchange
    if "trace all transactions from" in query and "until exchange" in query:
        try:
            wallet = query.split("from")[1].split("until")[0].strip()
            if wallet not in gb.G.nodes:
                return f"Wallet {wallet} not found in graph."
            paths = gb.trace_to_all_exchanges(wallet, exchanges)
            return paths if paths else f"No paths found from {wallet} to any exchange."
        except IndexError:
            return "Could not extract wallet address from query."

    # Expand a wallet (all outgoing transactions)
    if "expand wallet" in query:
        try:
            wallet = query.split("expand wallet")[1].strip()
            if wallet not in gb.G.nodes:
                return f"Wallet {wallet} not found in graph."
            return gb.expand_wallet(wallet)
        except IndexError:
            return "Could not extract wallet address from query."

    # Trace path from one wallet to another
    if "trace path from" in query and "to" in query:
        try:
            wallet_from = query.split("from")[1].split("to")[0].strip()
            wallet_to = query.split("to")[1].strip()
            if wallet_from not in gb.G.nodes or wallet_to not in gb.G.nodes:
                return "One or both wallets not found in graph."
            path = gb.trace_path(wallet_from, wallet_to)
            return path if path else f"No path found from {wallet_from} to {wallet_to}"
        except IndexError:
            return "Could not extract wallet addresses from query."

    # Placeholder for filtering by days
    if "transactions in last" in query and "days" in query:
        try:
            days_str = query.split("last")[1].split("days")[0].strip()
            days = int(days_str)
            if hasattr(gb, "filter_by_days"):
                return gb.filter_by_days(days)
            else:
                return f"Filtering by days not implemented. Days requested: {days}"
        except ValueError:
            return "Could not extract number of days from query."

    # Default fallback
    return "Query not recognized. Please use a supported format."


if __name__ == "__main__":
    # Load CSV and build graph
    df = pd.read_csv("data/raw/sample_wallet.csv")
    gb = GraphBuilder()
    gb.build_graph(df)

    # Example exchanges
    exchanges = [
        "0xF977814e90dA44bFA03b6295A0616a897441aceC",
        "0x61EDCDf5eF8F8F8F8F8F8F8F8F8F8F8F8F8F8F8F",
    ]

    # Example queries
    queries = [
        "Trace all transactions from 0xc5824c79b7470fab1ffbec0d190fffac6ca7cb39 until exchange",
        f"Expand wallet {df.iloc[0]['from']}",
        f"Trace path from {df.iloc[0]['from']} to {df.iloc[0]['to']}",
        "Show transactions in last 30 days"
    ]

    for q in queries:
        print(f"Query: {q}")
        result = parse_query(q, gb, exchanges)
        print("Result:", result)
        print("-" * 40)
