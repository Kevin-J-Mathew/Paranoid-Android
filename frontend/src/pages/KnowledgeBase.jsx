import React from 'react'
import KnowledgeBasePanel from '../components/KnowledgeBasePanel.jsx'

export default function KnowledgeBase() {
  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white">Knowledge Base</h2>
        <p className="text-slate-400 text-sm mt-1">
          RAG-powered semantic search over historical tests, bugs, and baselines.
          The system learns from every run.
        </p>
      </div>
      <KnowledgeBasePanel />
    </div>
  )
}
