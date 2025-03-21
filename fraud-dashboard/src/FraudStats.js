// import React, { useEffect, useState } from "react";
// import axios from "axios";
// import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from "recharts";

// const FraudStats = () => {
//   const [transactions, setTransactions] = useState([]);

//   useEffect(() => {
//     axios.get("http://127.0.0.1:5000/transactions")
//       .then(response => setTransactions(response.data))
//       .catch(error => console.error("Error fetching transactions:", error));
//   }, []);

//   const fraudData = [
//     { name: "Safe", value: transactions.filter(t => !t.is_fraud_predicted).length },
//     { name: "Fraud", value: transactions.filter(t => t.is_fraud_predicted).length }
//   ];

//   return (
//     <div>
//       <h2>Fraud Stats</h2>
//       <BarChart width={500} height={300} data={fraudData}>
//         <XAxis dataKey="name" />
//         <YAxis />
//         <Tooltip />
//         <Legend />
//         <Bar dataKey="value" fill="#8884d8" />
//       </BarChart>
//     </div>
//   );
// };

// export default FraudStats;

import React, { useEffect, useState } from "react";
import io from "socket.io-client";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from "recharts";

const socket = io("http://localhost:5000");

const FraudStats = () => {
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/transactions")
      .then(response => setTransactions(response.data))
      .catch(error => console.error("Error fetching transactions:", error));

    socket.on("fraud_update", (newTransaction) => {
      setTransactions((prev) => [newTransaction, ...prev]);
    });

    return () => socket.off("fraud_update");
  }, []);

  const fraudData = [
    { name: "Safe", value: transactions.filter(t => !t.is_fraud_predicted).length },
    { name: "Fraud", value: transactions.filter(t => t.is_fraud_predicted).length }
  ];

  return (
    <div>
      <h2>Fraud Stats</h2>
      <BarChart width={500} height={300} data={fraudData}>
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="value" fill="#8884d8" />
      </BarChart>
    </div>
  );
};

export default FraudStats;

