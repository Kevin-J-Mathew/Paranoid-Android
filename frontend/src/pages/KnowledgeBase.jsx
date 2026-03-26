import React from 'react'
import KnowledgeBasePanel from '../components/KnowledgeBasePanel.jsx'

export default function KnowledgeBase() {
  return (
    <div className="p-8 max-w-7xl mx-auto h-full flex flex-col animate-fade-in relative">
      <div className="mb-10">
        <div className="flex items-center gap-2 mb-3">
          <span className="w-2 h-2 rounded-full bg-accent-cyan animate-pulse"></span>
          <span className="text-accent-cyan text-[11px] font-mono tracking-widest font-bold uppercase">
            VECTOR_INDEX_READY
          </span>
        </div>
        <h2 className="text-4xl font-bold tracking-tight mb-3">Intelligence Store</h2>
        <p className="text-text-secondary text-sm">Query historical triages, resolution logs, and pattern analyses from the RAG knowledge agent.</p>
      </div>

      <div className="bg-surface-panel rounded-xl border border-border-light p-6 h-[600px] flex flex-col">
        <KnowledgeBasePanel />
      </div>
    </div>
  )
}
