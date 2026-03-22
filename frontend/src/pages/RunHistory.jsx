import React, { useState, useEffect } from 'react'
import { api } from '../api.js'
import TestRunCard from '../components/TestRunCard.jsx'
import ReportModal from '../components/ReportModal.jsx'

export default function RunHistory() {
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState(true)
  const [reportUrl, setReportUrl] = useState(null)

  useEffect(() => {
    api.listRuns()
      .then(r => setRuns(r.data.runs || []))
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="p-6 text-center text-slate-400">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        Loading run history...
      </div>
    )
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Run History</h2>
          <p className="text-slate-400 text-sm mt-1">All past test runs stored in the system.</p>
        </div>
        <span className="bg-slate-700 text-slate-300 px-3 py-1 rounded-full text-sm font-medium">
          {runs.length} runs total
        </span>
      </div>

      {runs.length === 0 ? (
        <div className="text-center text-slate-500 py-16">
          <div className="text-5xl mb-4">📋</div>
          <p className="text-lg font-medium">No runs yet</p>
          <p className="text-sm mt-1">Run your first test from the Dashboard.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {runs.map(run => (
            <TestRunCard
              key={run.id}
              result={run}
              onViewReport={(filename) => setReportUrl(api.getReportUrl(filename))}
            />
          ))}
        </div>
      )}

      <ReportModal reportUrl={reportUrl} onClose={() => setReportUrl(null)} />
    </div>
  )
}
