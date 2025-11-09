from flask import Flask, request, jsonify
import tenseal as ts
import numpy as np

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Homomorphic encryption API active",
        "status": "Server running successfully ✅"
    })

@app.route("/process_encrypted", methods=["POST"])
def process_encrypted():
    try:
        data = request.get_json()
        numbers = data.get("numbers", [])

        # Basic validation
        if not numbers:
            return jsonify({"error": "No numbers provided"}), 400

        # Create encryption context
        context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
        )
        context.generate_galois_keys()

        # Encrypt and compute
        enc_vector = ts.ckks_vector(context, numbers)
        result_vector = enc_vector + enc_vector  # simple operation
        encrypted_result = result_vector.serialize()

        return jsonify({
            "message": "Encrypted computation successful ✅",
            "encrypted_result": encrypted_result.decode("ISO-8859-1")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
