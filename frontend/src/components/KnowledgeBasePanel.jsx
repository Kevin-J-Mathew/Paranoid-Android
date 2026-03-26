import React, { useState } from 'react'
import { api } from '../api'

const SearchIcon = () => (
   <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
)

export default function KnowledgeBasePanel() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setHasSearched(true)
    try {
      const response = await api.querySimilarTests(query, 5)
      // Map RAG response to standard format
      const mapped = (response.data.results || []).map((item, idx) => ({
        id: idx,
        title: item.metadata?.title || item.metadata?.test_name || 'Generic Document',
        text: item.document,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' UTC',
        score: (1 - (item.distance || 0)).toFixed(2)
      }))
      setResults(mapped)
    } catch (err) {
      console.error('Failed to query knowledge store:', err)
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      <form onSubmit={handleSearch} className="relative mb-8">
        <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 text-text-secondary" />
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="QUERY_KNOWLEDGE_STORE..."
          className="w-full input-dark py-4 pl-[42px] pr-4 rounded-lg border border-border-light text-sm"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 btn-fuchsia px-4 py-1.5 rounded text-[10px]"
        >
          {loading ? 'SEARCHING...' : 'EXECUTE'}
        </button>
      </form>

      <div className="flex items-center justify-between mb-4 pb-4 border-b border-border-light">
        <h3 className="text-mono-caps text-xs font-bold tracking-widest text-text-primary">
          INTELLIGENCE_MATCHES
        </h3>
        <span className="text-text-secondary text-[10px] font-mono tracking-widest">
          {results.length} VECTORS_FOUND
        </span>
      </div>

      <div className="flex-1 overflow-y-auto">
        {!hasSearched && (
           <div className="h-full mt-24 text-text-tertiary text-xs text-mono-caps text-center flex flex-col items-center justify-center">
             <SearchIcon />
             <span className="mt-4">ENTER_QUERY_TO_SEARCH_MEMORY</span>
           </div>
        )}

        {loading && hasSearched && (
          <div className="flex justify-center items-center py-10">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00E5FF" strokeWidth="2" className="animate-spin"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
          </div>
        )}

        {!loading && hasSearched && results.map(res => (
          <div key={res.id} className="bg-surface-base border border-border-light rounded-lg p-5 mb-4 hover:border-accent-cyan/40 transition-colors">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-text-primary font-bold text-sm tracking-wide">{res.title}</h4>
              <div className="flex items-center gap-3">
                <span className="text-text-secondary text-[10px] font-mono">{res.timestamp}</span>
                <span className="bg-white/10 text-text-primary px-2 py-0.5 rounded text-[9px] font-mono border border-white/20">
                  RELEVANCE:{res.score}
                </span>
              </div>
            </div>
            <p className="text-text-secondary text-xs leading-relaxed font-mono">
              {'>'} {res.text}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
