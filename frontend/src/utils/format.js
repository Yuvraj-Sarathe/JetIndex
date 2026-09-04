/**
 * Formatting utilities for currency, dates, and numbers.
 */

/**
 * Format a number as Indian Rupees.
 * @param {number} amount
 * @returns {string} e.g., "₹4,250"
 */
export function formatINR(amount) {
  if (amount === null || amount === undefined) return '—';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format a date to IST display format.
 * @param {string|Date} date
 * @returns {string} e.g., "15 Jan 2025"
 */
export function formatDateIST(date) {
  if (!date) return '—';
  const d = new Date(date);
  return d.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    timeZone: 'Asia/Kolkata',
  });
}

/**
 * Format a percentage with sign.
 * @param {number} value
 * @returns {string} e.g., "+2.5%" or "-1.2%"
 */
export function formatPercent(value) {
  if (value === null || value === undefined) return '—';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
}

/**
 * Format a number with commas.
 * @param {number} num
 * @returns {string} e.g., "1,234,567"
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return '—';
  return new Intl.NumberFormat('en-IN').format(num);
}
