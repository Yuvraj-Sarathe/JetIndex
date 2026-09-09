import { useState, useEffect } from 'react';

export function useTemporal() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1';
    const API_TOKEN = import.meta.env.VITE_API_TOKEN || 'change-me-dev-token';

    fetch(`${API_BASE}/temporal/temporal`, {
      headers: { 'Authorization': `Bearer ${API_TOKEN}`, 'Content-Type': 'application/json' },
    })
      .then(r => r.json())
      .then(d => { if (!cancelled) { setData(d); setLoading(false); } })
      .catch(err => { if (!cancelled) { setError(err.message); setLoading(false); } });

    return () => { cancelled = true; };
  }, []);

  return { data, loading, error };
}
