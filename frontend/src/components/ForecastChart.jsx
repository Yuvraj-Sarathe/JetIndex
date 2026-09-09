/**
 * ForecastChart — Line chart with 95% confidence interval bands.
 * Renders predicted index values with shaded CI area.
 */
function ForecastChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="text-center py-8 text-slate-500">No forecast data</div>;
  }

  const values = data.map(d => d.predicted_index);
  const lower = data.map(d => d.ci_lower_95);
  const upper = data.map(d => d.ci_upper_95);

  const minVal = Math.min(...lower) - 1;
  const maxVal = Math.max(...upper) + 1;
  const range = maxVal - minVal;

  const width = 800;
  const height = 300;
  const padding = { top: 20, right: 20, bottom: 40, left: 50 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const toX = (i) => padding.left + (i / (data.length - 1)) * chartWidth;
  const toY = (val) => padding.top + chartHeight - ((val - minVal) / range) * chartHeight;

  // Build path strings
  const linePath = data.map((d, i) => `${i === 0 ? 'M' : 'L'}${toX(i)},${toY(d.predicted_index)}`).join(' ');
  const upperPath = data.map((d, i) => `${i === 0 ? 'M' : 'L'}${toX(i)},${toY(d.ci_upper_95)}`).join(' ');
  const lowerPath = data.map((d, i) => `${i === 0 ? 'M' : 'L'}${toX(i)},${toY(d.ci_lower_95)}`).join(' ');
  
  // CI area path (close the polygon)
  const areaPath = upperPath + ' L' + toX(data.length - 1) + ',' + toY(data[data.length - 1].ci_lower_95) +
    data.slice().reverse().map((d, i) => ` L${toX(data.length - 1 - i)},${toY(d.ci_lower_95)}`).join('') + ' Z';

  // Y-axis ticks
  const yTicks = 5;
  const yTickValues = Array.from({ length: yTicks + 1 }, (_, i) => minVal + (range * i) / yTicks);

  // X-axis labels (every 7th day)
  const xLabels = data.filter((_, i) => i % 7 === 0 || i === data.length - 1);

  return (
    <div className="overflow-x-auto">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-64">
        {/* Grid lines */}
        {yTickValues.map((val, i) => (
          <g key={i}>
            <line
              x1={padding.left}
              y1={toY(val)}
              x2={width - padding.right}
              y2={toY(val)}
              stroke="#e2e8f0"
              strokeWidth="1"
            />
            <text
              x={padding.left - 8}
              y={toY(val)}
              textAnchor="end"
              fontSize="10"
              fill="#94a3b8"
            >
              {val.toFixed(1)}
            </text>
          </g>
        ))}

        {/* CI band */}
        <path d={areaPath} fill="#3b82f6" fillOpacity="0.15" />

        {/* Upper/lower bounds */}
        <path d={upperPath} fill="none" stroke="#93c5fd" strokeWidth="1" strokeDasharray="4,4" />
        <path d={lowerPath} fill="none" stroke="#93c5fd" strokeWidth="1" strokeDasharray="4,4" />

        {/* Main forecast line */}
        <path d={linePath} fill="none" stroke="#2563eb" strokeWidth="2" />

        {/* X-axis labels */}
        {xLabels.map((d, i) => (
          <text
            key={i}
            x={toX(data.indexOf(d))}
            y={height - 10}
            textAnchor="middle"
            fontSize="9"
            fill="#94a3b8"
          >
            {d.forecast_date.slice(5)}
          </text>
        ))}

        {/* Legend */}
        <g transform={`translate(${padding.left + 10}, ${padding.top + 10})`}>
          <line x1="0" y1="0" x2="20" y2="0" stroke="#2563eb" strokeWidth="2" />
          <text x="25" y="4" fontSize="10" fill="#64748b">Predicted</text>
          <rect x="0" y="10" width="20" height="8" fill="#3b82f6" fillOpacity="0.15" />
          <text x="25" y="18" fontSize="10" fill="#64748b">95% CI</text>
        </g>
      </svg>
    </div>
  );
}

export default ForecastChart;
