import React, { useState, useEffect } from 'react'
import { api } from '../api.js'
import TestRunCard from '../components/TestRunCard.jsx'
import ReportModal from '../components/ReportModal.jsx' // Updated export later

export default function RunHistory() {
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState(true)
  const [reportUrl, setReportUrl] = useState(null)

  useEffect(() => {
    api.listRuns()
      .then(r => {
        setRuns(r.data.runs || [])
        setLoading(false)
      })
      .catch(e => {
        console.error(e)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="p-8 max-w-7xl mx-auto h-full flex flex-col items-center justify-center font-mono">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="animate-spin mb-4 text-cyan-400 drop-shadow-[0_0_10px_rgba(34,211,238,0.5)]"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
        <span className="text-cyan-400 text-xs uppercase tracking-widest text-mono-caps drop-shadow-[0_0_5px_rgba(34,211,238,0.5)]">FETCHING_HISTORY...</span>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-7xl mx-auto animate-fade-in relative h-full flex flex-col">
      <div className="mb-10 relative">
        <div className="absolute -left-10 top-0 bottom-0 w-[2px] bg-gradient-to-b from-cyan-400 to-transparent opacity-50 shadow-[0_0_10px_rgba(34,211,238,0.5)] hidden md:block"></div>
        <div className="flex items-center gap-2 mb-3">
          <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)] animate-pulse"></span>
          <span className="text-cyan-400 text-[11px] font-mono tracking-widest font-bold uppercase drop-shadow-[0_0_5px_rgba(34,211,238,0.5)]">
            ARCHIVE_ACCESS
          </span>
        </div>
        <h2 className="text-4xl font-bold tracking-tight mb-3 text-white drop-shadow-md">Test Runs Archive</h2>
        <p className="text-text-secondary text-sm font-mono opacity-80">Historical traces of all QA cycles executed by the Sentinel cluster.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-fr">
        {runs.map(run => (
          <div key={run.run_id || Math.random()} className="h-full">
            <TestRunCard
              result={run}
              onViewReport={(filename) => setReportUrl(api.getReportUrl(filename))}
              onFeedback={async (testName) => {
                await api.submitFeedback(run.run_id, testName, true)
                alert(`System feedback registered: False Positive in ${testName}`)
              }}
            />
          </div>
        ))}
        {runs.length === 0 && (
          <div className="col-span-full py-20 text-center border border-border-light/50 border-dashed rounded-xl bg-surface-panel/30 flex flex-col items-center justify-center group hover:border-cyan-500/30 transition-colors">
             <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-text-tertiary mb-3 group-hover:text-cyan-400 transition-colors"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
            <span className="text-mono-caps text-text-secondary text-xs group-hover:text-cyan-400 transition-colors">NO_RECORDS_FOUND</span>
          </div>
        )}
      </div>

      <ReportModal reportUrl={reportUrl} onClose={() => setReportUrl(null)} />
    </div>
  )
}
