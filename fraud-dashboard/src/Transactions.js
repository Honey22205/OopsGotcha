import React, { useEffect, useState } from "react";
import axios from "axios";

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/transactions")
      .then(response => setTransactions(response.data))
      .catch(error => console.error("Error fetching transactions:", error));
  }, []);

  const reportFraud = (transactionId) => {
    axios.post("http://127.0.0.1:5000/fraud-report", {
      transaction_id: transactionId,
      reporting_entity_id: "user_123",
      fraud_details: "Suspicious activity detected"
    })
    .then(response => alert("Fraud reported successfully!"))
    .catch(error => console.error("Error reporting fraud:", error));
  };

  return (
    <div>
      <h2>Transaction History</h2>
      <table border="1">
        <thead>
          <tr>
            <th>Transaction ID</th>
            <th>Amount</th>
            <th>Fraud Score</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map(txn => (
            <tr key={txn.transaction_id}>
              <td>{txn.transaction_id}</td>
              <td>${txn.amount}</td>
              <td>{txn.fraud_score.toFixed(2)}</td>
              <td>{txn.is_fraud_predicted ? "Fraud" : "Safe"}</td>
              <td>
                {!txn.is_fraud_predicted && (
                  <button onClick={() => reportFraud(txn.transaction_id)}>
                    Report Fraud
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Transactions;
