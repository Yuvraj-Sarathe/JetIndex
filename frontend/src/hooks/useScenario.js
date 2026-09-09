import { useState } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1';
const API_TOKEN = import.meta.env.VITE_API_TOKEN || 'change-me-dev-token';

export function useScenario() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runSimulation = async (params) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/scenario/simulate`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${API_TOKEN}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      setResult(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return { result, loading, error, runSimulation };
}
