import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import Transactions from "./Transactions";
import FraudStats from "./FraudStats";

const App = () => {
  return (
    <Router>
      <div>
        <h1>Fraud Detection Dashboard</h1>
        <nav>
          <ul>
            <li><Link to="/">Transactions</Link></li>
            <li><Link to="/stats">Fraud Stats</Link></li>
          </ul>
        </nav>
        
        <Routes>
          <Route path="/" element={<Transactions />} />
          <Route path="/stats" element={<FraudStats />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
