import sys
import os
import re
import json
import pandas as pd

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Ensure src/ is in Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graph_builder import GraphBuilder

MODEL_DIR = "models/intent_classifier"

class NLPInterface:
    def __init__(self, gb: GraphBuilder, exchanges: list):
        self.gb = gb
        self.exchanges = exchanges
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
        with open("data/intent_label_mapping.json", "r") as f:
            mapping = json.load(f)
        # keys are string indices, convert to dict[int, str]
        self.id2label = {int(k): v for k, v in mapping.items()}

    def classify_intent(self, query: str) -> str:
        inputs = self.tokenizer(query, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            pred_id = torch.argmax(logits, dim=-1).item()
        return self.id2label[pred_id]

    def extract_wallets(self, text: str):
        # Simple regex for Ethereum addresses
        pattern = r"0x[a-fA-F0-9]{40}"
        return re.findall(pattern, text)

    def extract_days(self, text: str):
        match = re.search(r"(\d+)\s*days?", text)
        if match:
            return int(match.group(1))
        return None

    def handle_query(self, query: str):
        intent = self.classify_intent(query)
        q_lower = query.lower()

        if intent == "TRACE_UNTIL_EXCHANGE":
            wallets = self.extract_wallets(query)
            if not wallets:
                return "Could not find a wallet address in the query."
            wallet = wallets[0]
            if wallet not in self.gb.G.nodes:
                return f"Wallet {wallet} not found in graph."
            paths = self.gb.trace_to_all_exchanges(wallet, self.exchanges)
            return paths if paths else f"No paths found from {wallet} to any exchange."

        elif intent == "EXPAND_WALLET":
            wallets = self.extract_wallets(query)
            if not wallets:
                return "Could not find a wallet address in the query."
            wallet = wallets[0]
            if wallet not in self.gb.G.nodes:
                return f"Wallet {wallet} not found in graph."
            return self.gb.expand_wallet(wallet)

        elif intent == "TRACE_PATH":
            wallets = self.extract_wallets(query)
            if len(wallets) < 2:
                return "Need two wallet addresses (from and to) in the query."
            wallet_from, wallet_to = wallets[0], wallets[1]
            if wallet_from not in self.gb.G.nodes or wallet_to not in self.gb.G.nodes:
                return "One or both wallets not found in graph."
            path = self.gb.trace_path(wallet_from, wallet_to)
            return path if path else f"No path found from {wallet_from} to {wallet_to}"

        elif intent == "FILTER_BY_DAYS":
            days = self.extract_days(query)
            if days is None:
                return "Could not extract number of days from query."
            if hasattr(self.gb, "filter_by_days"):
                return self.gb.filter_by_days(days)
            else:
                return f"Filtering by days not implemented. Days requested: {days}"

        else:
            return "Sorry, I could not understand this query intent."

if __name__ == "__main__":
    # Load CSV and build graph
    df = pd.read_csv("data/raw/sample_wallet.csv")
    gb = GraphBuilder()
    gb.build_graph(df)

    exchanges = [
        "0xF977814e90dA44bFA03b6295A0616a897441aceC",
        "0x61EDCDf5eF8F8F8F8F8F8F8F8F8F8F8F8F8F8F8F",
    ]

    nlp = NLPInterface(gb, exchanges)

    print("CryptoSleuth-AI NLP (Transformer-based)")
    print("Type your query (or 'exit'):")

    while True:
        q = input(">>> ").strip()
        if q.lower() in ("exit", "quit"):
            break
        result = nlp.handle_query(q)
        print("Intent:", nlp.classify_intent(q))
        print("Result:", result)
        print("-" * 60)
