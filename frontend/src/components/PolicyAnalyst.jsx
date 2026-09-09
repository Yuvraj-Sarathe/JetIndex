import { useState } from 'react';
import { useAIAnalyst } from '../hooks/useAIAnalyst';

const EXAMPLE_QUESTIONS = [
  'Why did airfares increase this week?',
  'How much does airfare contribute to CPI?',
  'What is the current market pressure score?',
  'Compare DEL-BOM vs DEL-BLR routes',
  'What happens if fuel prices rise 20%?',
  'How reliable is the current data quality?',
];

export default function PolicyAnalyst() {
  const { result, loading, error, askQuestion } = useAIAnalyst();
  const [question, setQuestion] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim()) askQuestion(question);
  };

  return (
    <div className="space-y-6">
      {/* Query Input */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">AI Policy Analyst</h3>
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input value={question} onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a macroeconomic question..."
            className="flex-1 px-4 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500" />
          <button type="submit" disabled={loading || !question.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm font-medium">
            {loading ? 'Thinking...' : 'Ask'}
          </button>
        </form>
        <div className="flex flex-wrap gap-2 mt-3">
          {EXAMPLE_QUESTIONS.map((q) => (
            <button key={q} onClick={() => { setQuestion(q); askQuestion(q); }}
              className="px-3 py-1 text-xs bg-slate-100 hover:bg-slate-200 rounded-full transition-colors">
              {q}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="bg-rose-50 border border-rose-200 rounded-lg p-4 text-rose-700">{error}</div>}

      {/* Response */}
      {result && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center gap-2 mb-3">
            <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded font-mono">{result.detected_intent}</span>
          </div>
          <p className="text-slate-900 font-medium leading-relaxed mb-3">{result.answer_summary}</p>
          {result.detailed_explanation && (
            <p className="text-sm text-slate-600 leading-relaxed mb-4">{result.detailed_explanation}</p>
          )}
          {result.numerical_evidence && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
              {Object.entries(result.numerical_evidence).map(([k, v]) => (
                <div key={k} className="p-2 bg-slate-50 rounded text-center">
                  <p className="text-xs text-slate-500 font-mono">{k.replace(/_/g, ' ')}</p>
                  <p className="text-sm font-bold text-slate-900">{typeof v === 'number' ? v.toFixed?.(2) || v : String(v)}</p>
                </div>
              ))}
            </div>
          )}
          {result.affected_routes?.length > 0 && (
            <div className="flex gap-1 mb-3">
              {result.affected_routes.map((r) => (
                <span key={r} className="px-2 py-0.5 text-xs bg-slate-100 rounded font-mono">{r}</span>
              ))}
            </div>
          )}
          {result.statutory_citations?.length > 0 && (
            <div className="text-xs text-slate-400">
              Citations: {result.statutory_citations.join(' · ')}
            </div>
          )}
          <p className="text-xs text-slate-400 mt-2">Data Tag: {result.data_tag}</p>
        </div>
      )}
    </div>
  );
}
