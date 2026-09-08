/**
 * API client — fetch wrapper with bearer token.
 * All API calls go through this client.
 */

const API_BASE = import.meta.env.VITE_API_BASE || '/api/v1';
const API_TOKEN = import.meta.env.VITE_API_TOKEN || 'change-me-dev-token';

async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Authorization': `Bearer ${API_TOKEN}`,
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function getApixDaily({ from, to } = {}) {
  const params = new URLSearchParams();
  if (from) params.append('from_date', from);
  if (to) params.append('to_date', to);
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiFetch(`/apix/daily${query}`);
}

export async function getApixWeekly({ from, to } = {}) {
  const params = new URLSearchParams();
  if (from) params.append('from_date', from);
  if (to) params.append('to_date', to);
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiFetch(`/apix/weekly${query}`);
}

export async function getApixMonthly({ from, to } = {}) {
  const params = new URLSearchParams();
  if (from) params.append('from_date', from);
  if (to) params.append('to_date', to);
  const query = params.toString() ? `?${params.toString()}` : '';
  return apiFetch(`/apix/monthly${query}`);
}

export async function getRoutes() {
  return apiFetch('/routes');
}

export async function getHeatmap(date) {
  const params = date ? `?route_date=${date}` : '';
  return apiFetch(`/routes/heatmap${params}`);
}

export async function getElasticity(routeId) {
  const params = routeId ? `?route_id=${routeId}` : '';
  return apiFetch(`/elasticity${params}`);
}

export async function getQuotes({ routeId, date, leadTime, carrier, limit = 50 } = {}) {
  const params = new URLSearchParams();
  if (routeId) params.append('route_id', routeId);
  if (date) params.append('route_date', date);
  if (leadTime) params.append('lead_time', leadTime);
  if (carrier) params.append('carrier', carrier);
  params.append('limit', limit);
  return apiFetch(`/quotes?${params.toString()}`);
}

export async function getBacktest() {
  return apiFetch('/backtest');
}

export async function triggerSweep() {
  return apiFetch('/admin/trigger-sweep', { method: 'POST' });
}

export async function getScrapedVsDGCA() {
  return apiFetch('/apix/scraped-vs-dgca');
}
