import React, { useEffect, useState } from 'react';
import { fetchHistory } from '../api.js';

export default function History() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchHistory().then(setHistory);
  }, []);

  return (
    <div>
      <h2>History / Tracking</h2>
      <ul>
        {history.map((p) => (
          <li key={p.id}>
            {new Date(p.timestamp).toLocaleDateString()} —
            {p.player} {p.market} {p.side} {p.line} —
            Model: {p.model_prob.toFixed(2)} | Market: {p.market_prob.toFixed(2)} |
            Edge: {p.edge.toFixed(2)} | Result: {p.result || 'pending'}
          </li>
        ))}
      </ul>
    </div>
  );
}
