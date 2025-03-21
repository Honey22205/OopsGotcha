
# from flask import Flask, request, jsonify
# from flask_mysqldb import MySQL
# import numpy as np
# import pickle
# from sklearn.preprocessing import LabelEncoder

# app = Flask(__name__)


# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'hp222005'
# app.config['MYSQL_DB'] = 'fraud_detection'
# mysql = MySQL(app)

# try:
#     with open('fraud_model.pkl', 'rb') as f:
#         model = pickle.load(f)
# except FileNotFoundError:
#     print("❌ Model file not found! Ensure 'fraud_model.pkl' exists in your project directory.")
#     model = None  


# label_encoders = {
#     "transaction_channel": LabelEncoder().fit(["Online", "Offline"]),
#     "transaction_payment_mode_anonymous": LabelEncoder().fit(["Credit Card", "Debit Card", "UPI", "Net Banking"]),
#     "payment_gateway_bank_anonymous": LabelEncoder().fit(["BankXYZ", "BankABC", "BankDEF"]),
#     "payer_browser_anonymous": LabelEncoder().fit(["Chrome", "Firefox", "Safari", "Edge"]),
# }

# def encode_feature(feature, value):
#     """Convert categorical features into numerical labels or hashed values."""
#     if feature in label_encoders:
#         try:
#             return label_encoders[feature].transform([value])[0]
#         except ValueError:
#             return 0  
#     elif isinstance(value, str):
#         return hash(value) % 10**8  
#     return value  
# def rule_based_detection(transaction):
#     if transaction['transaction_amount'] > 5000:
#         return True, "High Transaction Amount"
#     return False, ""


# @app.route('/fraud-report', methods=['POST'])
# def report_fraud():
#     print("✅ fraud-report API was called") 

#     data = request.get_json()

#     if not data:
#         return jsonify({"error": "No data received"}), 400

#     transaction_id = data.get('transaction_id')
#     reporting_entity_id = data.get('reporting_entity_id')
#     fraud_details = data.get('fraud_details')

#     if not all([transaction_id, reporting_entity_id, fraud_details]):
#         return jsonify({"error": "Missing required fields"}), 400

#     try:
#         cursor = mysql.connection.cursor()
#         cursor.execute("INSERT INTO fraud_reports (transaction_id, reporting_entity_id, fraud_details) VALUES (%s, %s, %s)", 
#                        (transaction_id, reporting_entity_id, fraud_details))
#         cursor.execute("UPDATE transactions SET is_fraud_reported = TRUE WHERE transaction_id = %s", (transaction_id,))
#         mysql.connection.commit()
#         cursor.close()
#     except Exception as e:
#         return jsonify({"error": f"Database error: {str(e)}"}), 500

#     return jsonify({
#         "transaction_id": transaction_id,
#         "reporting_acknowledged": True,
#         "failure_code": 0
#     })

# @app.route('/fraud-detection', methods=['POST'])
# def detect_fraud():
#     data = request.get_json()

 
#     rule_fraud, reason = rule_based_detection(data)
    
#     if rule_fraud:
#         fraud_source = "rule"
#         fraud_score = 1.0  
#     else:
#         if model is None:
#             return jsonify({"error": "AI model is missing. Train and save 'fraud_model.pkl' first."}), 500

#         required_features = [
#             'transaction_amount', 'transaction_channel', 'transaction_payment_mode_anonymous',
#             'payment_gateway_bank_anonymous', 'payer_browser_anonymous', 'payer_email_anonymous',
#             'payee_ip_anonymous', 'payer_mobile_anonymous'
#         ]

#         try:
#             input_data = np.array([[encode_feature(feature, data[feature]) for feature in required_features]], dtype=float)
#         except KeyError as e:
#             return jsonify({"error": f"Missing field in request: {str(e)}"}), 400
#         except ValueError as e:
#             return jsonify({"error": f"Data conversion error: {str(e)}"}), 400

#         fraud_score = model.predict_proba(input_data)[0][1]
#         fraud_source = "model"
#         rule_fraud = fraud_score > 0.5  

#     try:
#         cursor = mysql.connection.cursor()
#         cursor.execute("""
#             INSERT INTO transactions (transaction_id, payer_id, payee_id, amount, fraud_score, is_fraud_predicted) 
#             VALUES (%s, %s, %s, %s, %s, %s)
#         """, (
#             data["transaction_id_anonymous"], 
#             data["payer_email_anonymous"], 
#             data["payee_id_anonymous"], 
#             data["transaction_amount"], 
#             fraud_score, 
#             int(rule_fraud)  
#         ))
#         mysql.connection.commit()
#         cursor.close()
#     except Exception as e:
#         return jsonify({"error": f"Database error: {str(e)}"}), 500

#     return jsonify({
#         "transaction_id": data["transaction_id_anonymous"],
#         "is_fraud": int(rule_fraud),  
#         "fraud_source": fraud_source,
#         "fraud_reason": reason if rule_fraud else "AI Prediction",
#         "fraud_score": fraud_score
#     })

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_socketio import SocketIO
from flask_cors import CORS
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Enable CORS for WebSocket
socketio = SocketIO(app, cors_allowed_origins="*")

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'hp222005'
app.config['MYSQL_DB'] = 'fraud_detection'
mysql = MySQL(app)

# Load AI Model
try:
    with open('fraud_model.pkl', 'rb') as f:
        model = pickle.load(f)
except FileNotFoundError:
    print("❌ Model file not found! Ensure 'fraud_model.pkl' exists in your project directory.")
    model = None  

# Label Encoding for Categorical Features
label_encoders = {
    "transaction_channel": LabelEncoder().fit(["Online", "Offline"]),
    "transaction_payment_mode_anonymous": LabelEncoder().fit(["Credit Card", "Debit Card", "UPI", "Net Banking"]),
    "payment_gateway_bank_anonymous": LabelEncoder().fit(["BankXYZ", "BankABC", "BankDEF"]),
    "payer_browser_anonymous": LabelEncoder().fit(["Chrome", "Firefox", "Safari", "Edge"]),
}

def encode_feature(feature, value):
    """Convert categorical features into numerical labels or hashed values."""
    if feature in label_encoders:
        try:
            return label_encoders[feature].transform([value])[0]
        except ValueError:
            return 0  
    elif isinstance(value, str):
        return hash(value) % 10**8  
    return value  

def rule_based_detection(transaction):
    if transaction['transaction_amount'] > 5000:
        return True, "High Transaction Amount"
    return False, ""

# 📡 WebSocket Events
@socketio.on("connect")
def handle_connect():
    print("✅ Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("❌ Client disconnected")

@app.route('/fraud-report', methods=['POST'])
def report_fraud():
    print("✅ fraud-report API was called") 

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    transaction_id = data.get('transaction_id')
    reporting_entity_id = data.get('reporting_entity_id')
    fraud_details = data.get('fraud_details')

    if not all([transaction_id, reporting_entity_id, fraud_details]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO fraud_reports (transaction_id, reporting_entity_id, fraud_details) VALUES (%s, %s, %s)", 
                       (transaction_id, reporting_entity_id, fraud_details))
        cursor.execute("UPDATE transactions SET is_fraud_reported = TRUE WHERE transaction_id = %s", (transaction_id,))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    return jsonify({
        "transaction_id": transaction_id,
        "reporting_acknowledged": True,
        "failure_code": 0
    })


@app.route('/transactions', methods=['GET'])
def get_transactions():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT transaction_id, amount, fraud_score, is_fraud_predicted FROM transactions")
        transactions = cursor.fetchall()
        cursor.close()

        transactions_list = [
            {
                "transaction_id": txn[0],
                "amount": txn[1],
                "fraud_score": float(txn[2]),
                "is_fraud_predicted": bool(txn[3])
            }
            for txn in transactions
        ]

        return jsonify(transactions_list)
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@app.route('/fraud-detection', methods=['POST'])
def detect_fraud():
    data = request.get_json()

    rule_fraud, reason = rule_based_detection(data)
    
    if rule_fraud:
        fraud_source = "rule"
        fraud_score = 1.0  
    else:
        if model is None:
            return jsonify({"error": "AI model is missing. Train and save 'fraud_model.pkl' first."}), 500

        required_features = [
            'transaction_amount', 'transaction_channel', 'transaction_payment_mode_anonymous',
            'payment_gateway_bank_anonymous', 'payer_browser_anonymous', 'payer_email_anonymous',
            'payee_ip_anonymous', 'payer_mobile_anonymous'
        ]

        try:
            input_data = np.array([[encode_feature(feature, data[feature]) for feature in required_features]], dtype=float)
        except KeyError as e:
            return jsonify({"error": f"Missing field in request: {str(e)}"}), 400
        except ValueError as e:
            return jsonify({"error": f"Data conversion error: {str(e)}"}), 400

        fraud_score = model.predict_proba(input_data)[0][1]
        fraud_source = "model"
        rule_fraud = fraud_score > 0.5  

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO transactions (transaction_id, payer_id, payee_id, amount, fraud_score, is_fraud_predicted) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data["transaction_id_anonymous"], 
            data["payer_email_anonymous"], 
            data["payee_id_anonymous"], 
            data["transaction_amount"], 
            fraud_score, 
            int(rule_fraud)  
        ))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    # 🔥 Broadcast fraud detection result to WebSocket clients
    socketio.emit("fraud_detection_result", {
        "transaction_id": data["transaction_id_anonymous"],
        "is_fraud": int(rule_fraud),  
        "fraud_source": fraud_source,
        "fraud_reason": reason if rule_fraud else "AI Prediction",
        "fraud_score": fraud_score
    })

    return jsonify({
        "transaction_id": data["transaction_id_anonymous"],
        "is_fraud": int(rule_fraud),  
        "fraud_source": fraud_source,
        "fraud_reason": reason if rule_fraud else "AI Prediction",
        "fraud_score": fraud_score
    })

if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
