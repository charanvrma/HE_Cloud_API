# Major_Project/HE_Cloud_API/cloud_server_api.py
from flask import Flask, request, jsonify
import tenseal as ts
import base64
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
    return jsonify({"status": "HE Cloud API running"})

@app.route("/process_encrypted", methods=["POST"])
def process_encrypted():
    try:
        payload = request.get_json()
        context_b64 = payload.get("context_public")
        ciphertexts_b64 = payload.get("ciphertexts", [])

        if not context_b64 or not ciphertexts_b64:
            return jsonify({"error": "context_public and ciphertexts required"}), 400

        # reconstruct context (public only, no secret key)
        context_bytes = base64.b64decode(context_b64.encode("utf-8"))
        ctx = ts.context_from(context_bytes)

        app.logger.info("Received ciphertexts (base64/truncated):")
        for i, cb64 in enumerate(ciphertexts_b64):
            app.logger.info(f"  ciphertext[{i}] (trunc): {cb64[:120]}...")
            if i >= 2:
                break

        # deserialize ciphertexts and compute encrypted sum
        enc_vectors = [ts.ckks_vector_from(ctx, base64.b64decode(cb64.encode("utf-8"))) for cb64 in ciphertexts_b64]

        res = enc_vectors[0]
        for e in enc_vectors[1:]:
            res += e

        # serialize result and return base64
        res_bytes = res.serialize()
        res_b64 = base64.b64encode(res_bytes).decode("utf-8")

        return jsonify({"result_ciphertext": res_b64}), 200

    except Exception as e:
        app.logger.exception("Error in processing encrypted request")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
