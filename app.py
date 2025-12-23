from flask import Flask, request, jsonify
from src.data_pipeline import DataPipeline
from src.graph_builder import GraphBuilder

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Server Running ✅ Use POST /trace with a wallet address."})


@app.route("/trace", methods=["POST"])
def trace_wallet():
    wallet = request.json.get("wallet")
    if not wallet:
        return jsonify({"error": "No wallet address provided"}), 400

    try:
        API_KEY = "X741C9XNHGG57BZ1A1S91EYBKRAP689WTD"
        dp = DataPipeline(API_KEY)
        df = dp.fetch_transactions(wallet)

        gb = GraphBuilder()
        G = gb.build_graph(df)

        return jsonify({
            "wallet": wallet,
            "nodes": len(G.nodes()),
            "edges": len(G.edges())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)


# from flask import Flask, request, jsonify
# from src.data_pipeline import DataPipeline
# from src.graph_builder import GraphBuilder

# app = Flask(__name__)

# @app.route("/", methods=["GET"])
# def home():
#     return jsonify({"message": "Server Running ✅ Use POST /trace with a wallet address."})

# @app.route("/trace", methods=["POST"])
# def trace_wallet():
#     wallet = request.json.get("wallet")
#     if not wallet:
#         return jsonify({"error": "No wallet address provided"}), 400

#     try:
#         dp = DataPipeline("YOUR_API_KEY_HERE")
#         df = dp.fetch_transactions(wallet)

#         gb = GraphBuilder()
#         G = gb.build_graph(df)

#         return jsonify({
#             "wallet": wallet,
#             "nodes": len(G.nodes()),
#             "edges": len(G.edges())
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True)




