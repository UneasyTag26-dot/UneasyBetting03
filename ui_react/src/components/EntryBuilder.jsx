import React, { useState, useEffect } from 'react';
import { fetchHistory, evaluateEntry } from '../api.js';

export default function EntryBuilder() {
  const [picks, setPicks] = useState([]);
  const [selected, setSelected] = useState([]);
  const [payout, setPayout] = useState(3.0);
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetchHistory().then(setPicks);
  }, []);

  const togglePick = (id) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const evaluate = async () => {
    if (selected.length < 2 || selected.length > 5) {
      alert('Select between 2 and 5 legs');
      return;
    }
    const data = await evaluateEntry(selected, payout);
    setResult(data);
  };

  return (
    <div>
      <h2>Entry Builder</h2>
      <p>Select 2–5 saved picks to evaluate:</p>
      <ul>
        {picks.map((p) => (
          <li key={p.id}>
            <label>
              <input
                type="checkbox"
                checked={selected.includes(p.id)}
                onChange={() => togglePick(p.id)}
              />
              {p.player} {p.market} {p.side} {p.line} (model {p.model_prob.toFixed(2)})
            </label>
          </li>
        ))}
      </ul>
      <label>Payout multiplier:
        <input type="number" step="0.1" value={payout} onChange={(e) => setPayout(parseFloat(e.target.value))}/>
      </label>
      <button onClick={evaluate}>Evaluate</button>
      {result && (
        <div>
          <p>Combined probability: {result.combined_probability.toFixed(3)}</p>
          {result.fair_odds && <p>Fair odds: {result.fair_odds.toFixed(2)}</p>}
          <p>Expected value: {result.expected_value.toFixed(3)}</p>
        </div>
      )}
    </div>
  );
}
