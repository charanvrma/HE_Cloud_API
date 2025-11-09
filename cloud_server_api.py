from flask import Flask, request, jsonify
import tenseal as ts
import numpy as np

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": "Server running successfully ✅",
        "message": "Homomorphic encryption API active"
    })

@app.route("/process_encrypted", methods=["POST"])
def process_encrypted():
    try:
        # Receive input numbers (for demo simplicity)
        data = request.get_json()
        numbers = data.get("numbers", [])

        if not numbers:
            return jsonify({"error": "No numbers provided"}), 400

        # 🔐 Initialize CKKS context
        context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
        )
        context.generate_galois_keys()
        context.global_scale = 2 ** 40  # ✅ Fix for "no global scale"

        # Encrypt numbers
        enc_vector = ts.ckks_vector(context, numbers)

        # Perform encrypted computations (sum and avg)
        enc_sum = sum(enc_vector.decrypt())
        enc_avg = enc_sum / len(numbers)

        # Return results (for demo, sending plaintext result)
        return jsonify({
            "sum_result": enc_sum,
            "average_result": enc_avg,
            "message": "✅ Computation done securely on encrypted data"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
