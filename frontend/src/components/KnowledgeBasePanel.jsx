import React, { useState, useEffect } from 'react'
import { api } from '../api.js'

export default function KnowledgeBasePanel() {
  const [stats, setStats] = useState(null)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    api.getKnowledgeStats().then(r => setStats(r.data)).catch(console.error)
  }, [])

  const handleSearch = async () => {
    if (!query.trim()) return
    setSearching(true)
    try {
      const r = await api.querySimilarTests(query)
      setResults(r.data.results || [])
    } catch (e) {
      console.error(e)
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Test Cases', value: stats.test_cases, icon: '🧪', color: 'blue' },
            { label: 'Bug Reports', value: stats.bug_reports, icon: '🐛', color: 'red' },
            { label: 'Baselines', value: stats.run_baselines, icon: '📏', color: 'green' },
          ].map(item => (
            <div key={item.label} className="bg-slate-800 rounded-xl border border-slate-700 p-5 text-center">
              <div className="text-3xl mb-2">{item.icon}</div>
              <div className="text-3xl font-bold text-white">{item.value}</div>
              <div className="text-slate-400 text-sm mt-1">{item.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Search */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-5">
        <h3 className="text-white font-bold mb-3">🔍 Semantic Search</h3>
        <p className="text-slate-400 text-sm mb-3">
          Query the knowledge base with natural language to find similar past tests.
        </p>
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="e.g. 'user adds a todo item' or 'filter by completion'"
            className="flex-1 bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500 placeholder-slate-600"
          />
          <button
            onClick={handleSearch}
            disabled={searching}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white px-5 py-2 rounded-lg text-sm font-semibold transition-colors"
          >
            {searching ? '...' : 'Search'}
          </button>
        </div>

        {results.length > 0 && (
          <div className="mt-4 space-y-3">
            <p className="text-slate-400 text-xs font-medium">{results.length} similar tests found:</p>
            {results.map((r, idx) => (
              <div key={idx} className="bg-slate-900 rounded-lg p-3 border border-slate-700">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-slate-300 text-sm font-medium">
                    {r.metadata?.test_name || 'Unknown test'}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-0.5 rounded font-bold uppercase ${
                      r.metadata?.outcome === 'passed' ? 'bg-green-900/50 text-green-300' : 'bg-red-900/50 text-red-300'
                    }`}>
                      {r.metadata?.outcome || 'unknown'}
                    </span>
                    <span className="text-slate-500 text-xs">
                      sim: {r.distance ? (1 - r.distance).toFixed(2) : 'N/A'}
                    </span>
                  </div>
                </div>
                <p className="text-slate-500 text-xs">{r.document?.slice(0, 150)}...</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
