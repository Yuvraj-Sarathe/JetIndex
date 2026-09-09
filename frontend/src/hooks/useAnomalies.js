import { useState, useEffect } from 'react';

/**
 * Custom hook for fetching anomaly data.
 */
export function useAnomalies() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    
    const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1';
    const API_TOKEN = import.meta.env.VITE_API_TOKEN || 'change-me-dev-token';
    
    fetch(`${API_BASE}/anomalies`, {
      headers: {
        'Authorization': `Bearer ${API_TOKEN}`,
        'Content-Type': 'application/json',
      },
    })
      .then(res => {
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        return res.json();
      })
      .then(data => {
        if (!cancelled) {
          setData(data);
          setLoading(false);
        }
      })
      .catch(err => {
        if (!cancelled) {
          setError(err.message);
          setLoading(false);
        }
      });
    
    return () => { cancelled = true; };
  }, []);

  return { data, loading, error };
}
