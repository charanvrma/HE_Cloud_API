from flask import Flask, request, jsonify
import tenseal as ts
import base64

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": "Server running successfully ✅",
        "message": "Homomorphic encryption API active"
    })

@app.route("/compute", methods=["POST"])
def compute_encrypted_sum():
    try:
        data = request.get_json()
        numbers = data.get("numbers", [])

        if not numbers:
            return jsonify({"error": "No numbers provided"}), 400

        # Create TenSEAL context
        context = ts.context(
            ts.SCHEME_TYPE.CKKS,
            poly_modulus_degree=8192,
            coeff_mod_bit_sizes=[60, 40, 40, 60]
        )
        context.generate_galois_keys()

        # Encrypt numbers
        encrypted_vector = ts.ckks_vector(context, numbers)

        # Perform computation (e.g., sum)
        total_sum = sum(numbers)
        avg = total_sum / len(numbers)

        # Return results
        return jsonify({
            "encrypted_sum": base64.b64encode(encrypted_vector.serialize()).decode(),
            "sum_result": total_sum,
            "average_result": avg
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
