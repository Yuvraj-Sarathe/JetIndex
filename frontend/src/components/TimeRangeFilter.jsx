import { useState } from 'react';

/**
 * TimeRangeFilter — presets 7D/30D/90D/1Y + custom date range.
 */
function TimeRangeFilter({ onChange }) {
  const [active, setActive] = useState('90d');
  const [customFrom, setCustomFrom] = useState('');
  const [customTo, setCustomTo] = useState('');

  // key -> { days, label }. Order here controls display order.
  const presets = {
    '7d': { days: 7, label: '7D' },
    '30d': { days: 30, label: '30D' },
    '90d': { days: 90, label: '90D' },
    '1y': { days: 365, label: '1Y' },
  };

  function handlePreset(key, days) {
    setActive(key);
    const to = new Date().toISOString().split('T')[0];
    const from = new Date(Date.now() - days * 86400000).toISOString().split('T')[0];
    onChange({ from, to });
  }

  function handleCustom() {
    setActive('custom');
    onChange({ from: customFrom || null, to: customTo || null });
  }

  return (
    <div className="flex flex-wrap items-center gap-2 bg-card border border-hairline rounded-xl p-1.5 text-xs">
      <span className="text-ink-muted font-medium px-2 uppercase tracking-wider text-[11px]">Range:</span>
      <div className="flex items-center gap-1 bg-surface-card p-0.5 rounded-lg border border-hairline">
        {Object.entries(presets).map(([key, { days, label }]) => (
          <button
            key={key}
            onClick={() => handlePreset(key, days)}
            className={`px-3 py-1 rounded-md font-medium transition-all ${
              active === key
                ? 'bg-primary text-black font-bold shadow-sm'
                : 'text-ink-muted hover:text-white hover:bg-card-hover'
            }`}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="flex items-center gap-1.5 ml-1">
        <input
          type="date"
          value={customFrom}
          onChange={(e) => setCustomFrom(e.target.value)}
          className="bg-canvas border border-hairline text-ink-muted focus:text-white rounded-md px-2 py-1 text-xs focus:outline-none focus:border-primary transition-colors"
        />
        <span className="text-ink-faint">→</span>
        <input
          type="date"
          value={customTo}
          onChange={(e) => setCustomTo(e.target.value)}
          className="bg-canvas border border-hairline text-ink-muted focus:text-white rounded-md px-2 py-1 text-xs focus:outline-none focus:border-primary transition-colors"
        />
        <button
          onClick={handleCustom}
          className="px-3 py-1 rounded-md font-semibold bg-card-elevated border border-hairline text-white hover:bg-primary hover:text-black hover:border-primary transition-colors"
        >
          Apply
        </button>
      </div>
    </div>
  );
}

export default TimeRangeFilter;