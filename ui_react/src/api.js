export async function fetchScan(edge = 0.05, minBooks = 1, top = 10) {
  const res = await fetch(`/api/scan?edge=${edge}&min_books=${minBooks}&top=${top}`);
  if (!res.ok) throw new Error('Failed to fetch scan');
  return res.json();
}

export async function fetchHistory() {
  const res = await fetch('/api/history');
  if (!res.ok) throw new Error('Failed to fetch history');
  return res.json();
}

export async function evaluateEntry(legs, payoutMultiplier = 1.0) {
  const res = await fetch('/api/entry/evaluate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ legs, payout_multiplier: payoutMultiplier })
  });
  if (!res.ok) throw new Error('Failed to evaluate entry');
  return res.json();
}
