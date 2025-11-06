from flask import Flask, request, jsonify
import tenseal as ts
import base64

app = Flask(__name__)

@app.route("/process_encrypted", methods=["POST"])
def process_encrypted():
    try:
        # Parse incoming JSON
        data = request.json
        context_bytes = base64.b64decode(data["context"])
        encrypted_list = [base64.b64decode(x) for x in data["encrypted"]]

        # Load TenSEAL context (public)
        ctx = ts.context_from(context_bytes)

        # Deserialize ciphertexts
        encrypted_vectors = [ts.ckks_vector_from(ctx, e) for e in encrypted_list]

        # Compute encrypted sum
        enc_sum = encrypted_vectors[0]
        for e in encrypted_vectors[1:]:
            enc_sum += e

        # Serialize and return result
        result_bytes = enc_sum.serialize()
        result_b64 = base64.b64encode(result_bytes).decode()

        return jsonify({"encrypted_result": result_b64})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # run locally for testing
    app.run(host="0.0.0.0", port=5000)
