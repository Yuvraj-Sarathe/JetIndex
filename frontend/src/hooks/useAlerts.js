import { useState, useEffect } from 'react';

export function useAlerts() {
  const [rules, setRules] = useState(null);
  const [liveAlerts, setLiveAlerts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1';
    const API_TOKEN = import.meta.env.VITE_API_TOKEN || 'change-me-dev-token';
    const headers = { 'Authorization': `Bearer ${API_TOKEN}`, 'Content-Type': 'application/json' };

    Promise.all([
      fetch(`${API_BASE}/alerts/rules`, { headers }).then(r => r.json()),
      fetch(`${API_BASE}/alerts/live`, { headers }).then(r => r.json()),
    ])
      .then(([rulesData, liveData]) => {
        if (!cancelled) {
          setRules(rulesData);
          setLiveAlerts(liveData);
          setLoading(false);
        }
      })
      .catch(err => {
        if (!cancelled) { setError(err.message); setLoading(false); }
      });

    return () => { cancelled = true; };
  }, []);

  return { rules, liveAlerts, loading, error };
}
