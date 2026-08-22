'use client';

import { useState } from 'react';

export default function Home() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-24 font-sans">
      <div className="max-w-2xl mx-auto space-y-8">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-indigo-500">
            Misinformation Radar
          </h1>
          <p className="text-slate-400 mt-2">
            GitHub Ready Version: Detect structural anomalies and emotional bait instantly.
          </p>
        </div>

        <div className="space-y-4">
          <textarea
            rows={6}
            className="w-full p-4 bg-slate-900 border border-slate-800 rounded-xl focus:ring-2 focus:ring-cyan-500 focus:outline-none text-slate-200 placeholder-slate-600"
            placeholder="Paste text or social media excerpt here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full py-3 px-6 bg-gradient-to-r from-cyan-500 to-indigo-600 font-semibold rounded-xl hover:opacity-90 transition disabled:opacity-50 shadow-lg shadow-cyan-500/20"
          >
            {loading ? 'Analyzing...' : 'Run Analysis'}
          </button>
        </div>

        {result && (
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-xl space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-slate-400">Threat Index</span>
              <span className={`text-xl font-bold ${result.riskScore > 50 ? 'text-red-400' : 'text-emerald-400'}`}>
                {result.riskScore}% Risk
              </span>
            </div>

            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-500 ${result.riskScore > 50 ? 'bg-red-500' : 'bg-emerald-500'}`}
                style={{ width: `${result.riskScore}%` }}
              />
            </div>

            <div>
              <h3 className="font-semibold text-slate-200">Verdict: {result.rating}</h3>
              <p className="text-sm text-slate-400 mt-1">{result.summary}</p>
            </div>

            {result.triggers?.length > 0 && (
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Flags Triggered:</span>
                <div className="flex flex-wrap gap-2 mt-2">
                  {result.triggers.map((trigger: string, idx: number) => (
                    <span key={idx} className="px-3 py-1 bg-red-950/50 border border-red-900/50 text-red-300 text-xs rounded-full">
                      {trigger}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
      }
