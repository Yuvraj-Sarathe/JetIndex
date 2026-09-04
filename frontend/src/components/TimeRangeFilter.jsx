import { useState } from 'react';

/**
 * TimeRangeFilter — presets 7/30/90d + custom date range.
 */
function TimeRangeFilter({ onChange }) {
  const [active, setActive] = useState('90d');
  const [customFrom, setCustomFrom] = useState('');
  const [customTo, setCustomTo] = useState('');

  const presets = {
    '7d': 7,
    '30d': 30,
    '90d': 90,
  };

  function handlePreset(days) {
    setActive(days + 'd');
    const to = new Date().toISOString().split('T')[0];
    const from = new Date(Date.now() - days * 86400000).toISOString().split('T')[0];
    onChange({ from, to });
  }

  function handleCustom() {
    setActive('custom');
    onChange({ from: customFrom || null, to: customTo || null });
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-slate-600 mr-1">Range:</span>
      {Object.keys(presets).map((preset) => (
        <button
          key={preset}
          onClick={() => handlePreset(presets[preset])}
          className={`px-3 py-1 text-xs rounded ${
            active === preset
              ? 'bg-indigo-500 text-white'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
          }`}
        >
          {preset}
        </button>
      ))}
      <input
        type="date"
        value={customFrom}
        onChange={(e) => setCustomFrom(e.target.value)}
        className="px-2 py-1 text-xs border border-slate-200 rounded"
      />
      <span className="text-slate-400">—</span>
      <input
        type="date"
        value={customTo}
        onChange={(e) => setCustomTo(e.target.value)}
        className="px-2 py-1 text-xs border border-slate-200 rounded"
      />
      <button
        onClick={handleCustom}
        className="px-3 py-1 text-xs rounded bg-slate-100 text-slate-600 hover:bg-slate-200"
      >
        Apply
      </button>
    </div>
  );
}

export default TimeRangeFilter;
