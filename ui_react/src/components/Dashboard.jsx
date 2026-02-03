import React, { useState } from 'react';
import { fetchScan } from '../api.js';

export default function Dashboard() {
  const [edge, setEdge] = useState(0.05);
  const [top, setTop] = useState(10);
  const [candidates, setCandidates] = useState([]);

  const handleScan = async () => {
    const data = await fetchScan(edge, 1, top);
    setCandidates(data);
  };

  return (
    <div>
      <h2>Dashboard</h2>
      <label>Min Edge:
        <input type="number" step="0.01" min="0" max="0.2" value={edge} onChange={(e) => setEdge(parseFloat(e.target.value))}/>
      </label>
      <label style={{ marginLeft: '1rem' }}>Top N:
        <input type="number" min="1" max="50" value={top} onChange={(e) => setTop(parseInt(e.target.value))}/>
      </label>
      <button style={{ marginLeft: '1rem' }} onClick={handleScan}>Scan</button>
      <ul>
        {candidates.map((c, idx) => (
          <li key={idx}>
            {c.player} {c.market} {c.side} {c.line} —
            Model: {c.model_prob.toFixed(2)} | Market: {c.market_prob.toFixed(2)} | Edge: {c.edge.toFixed(2)}
          </li>
        ))}
      </ul>
    </div>
  );
}
