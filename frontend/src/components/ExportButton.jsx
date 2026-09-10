import Papa from 'papaparse';

/**
 * ExportButton — CSV + JSON download for current view data.
 */
function ExportButton({ data, filename = 'export' }) {
  function downloadJSON() {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function downloadCSV() {
    if (!data || data.length === 0) return;
    const csv = Papa.unparse(data);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="flex gap-2">
      <button
        onClick={downloadCSV}
        disabled={!data || data.length === 0}
        className="px-3.5 py-1.5 text-xs font-semibold bg-card border border-hairline text-ink-muted hover:text-white hover:border-primary/50 rounded-xl transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5"
      >
        <span>↓</span> CSV
      </button>
      <button
        onClick={downloadJSON}
        disabled={!data || data.length === 0}
        className="px-3.5 py-1.5 text-xs font-semibold bg-card border border-hairline text-ink-muted hover:text-white hover:border-primary/50 rounded-xl transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-1.5"
      >
        <span>↓</span> JSON
      </button>
    </div>
  );
}

export default ExportButton;
