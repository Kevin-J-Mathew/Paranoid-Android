import React from 'react'

const ChartIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
)
const FlagIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" x2="4" y1="22" y2="15"/></svg>
)

export default function TestRunCard({ result, onViewReport, onFeedback }) {
  const total = result.total_tests || result.execution_results?.length || 0
  const passed = result.passed_tests || result.execution_results?.filter(r => r.status === 'passed').length || 0
  const failed = result.failed_tests || (total - passed)
  const passRate = total > 0 ? Math.round((passed / total) * 100) : 0
  const regressionRisk = result.regression_risk ||
    result.regression_analysis?.overall_regression_risk || 'unknown'

  return (
    <div className="bg-surface-panel rounded-xl border border-border-light p-6 flex flex-col h-full hover:border-cyan-500/50 hover:shadow-[0_0_20px_rgba(34,211,238,0.15)] transition-all duration-300 relative overflow-hidden group">
      {/* Decorative top gradient line */}
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>

      {/* Header matching FAILED_HIGH_PRIORITY_TESTS style */}
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-border-light">
        <h3 className="text-mono-caps text-xs font-bold tracking-widest text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.5)]">
          TEST_RUN_ANALYSIS
        </h3>
        <span className="text-text-secondary text-[10px] font-mono tracking-widest bg-black/50 px-2 py-1 rounded border border-white/5">
          {total} CASES EVALUATED
        </span>
      </div>

      {/* Main Info */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex-1 min-w-0 pr-4">
          <h4 className="text-xl font-bold text-white tracking-tight mb-2 truncate group-hover:text-cyan-50 transition-colors">
            {result.story_title || 'Autonomous Suite Execution'}
          </h4>
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="text-fuchsia-300 text-[10px] font-mono bg-fuchsia-500/10 border border-fuchsia-500/20 px-2 py-0.5 rounded shadow-[0_0_10px_rgba(217,70,239,0.1)]">
              SESSION_ID: {result.run_id?.slice(0, 8).toUpperCase() || result.story_id}
            </span>
            {regressionRisk === 'critical' ? (
              <span className="pill-critical drop-shadow-[0_0_5px_rgba(255,94,94,0.5)]">CRITICAL_REGRESSION</span>
            ) : regressionRisk === 'high' ? (
              <span className="pill-high drop-shadow-[0_0_5px_rgba(255,165,0,0.5)]">HIGH_RISK</span>
            ) : (
              <span className="bg-cyan-500/10 text-cyan-400 text-[10px] font-mono font-bold border border-cyan-500/30 px-2 py-0.5 rounded drop-shadow-[0_0_5px_rgba(34,211,238,0.3)]">
                NORMAL_OPERATION
              </span>
            )}
          </div>
          {result.created_at && (
            <p className="text-text-secondary text-[10px] font-mono tracking-wide mt-2">
              TIMESTAMP: <span className="text-gray-400">{new Date(result.created_at).toISOString()}</span>
            </p>
          )}
        </div>
        
        {/* Pass rate circular/large display */}
        <div className="text-right shrink-0">
          <div className={`font-bold tracking-tight text-4xl drop-shadow-[0_0_12px_currentColor] ${passRate >= 80 ? 'text-green-400' : passRate >= 50 ? 'text-amber-400' : 'text-red-500'}`}>
            {passRate}%
          </div>
          <div className="text-text-secondary text-mono-caps text-[9px] font-bold mt-1">SUCCESS_RATE</div>
        </div>
      </div>

      {/* Execution Results (mimicking the code block errors) */}
      <div className="flex-1 mb-6">
        {result.execution_results && result.execution_results.length > 0 ? (
          <div className="space-y-4 max-h-[320px] overflow-y-auto pr-2 custom-scrollbar">
            {result.execution_results.map((r, idx) => {
              const fails = r.status === 'failed'
              return (
                <div key={idx} className="flex flex-col pb-4 border-b border-border-light/40 last:border-0 last:pb-0 group/test">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <span className={`font-mono text-xs font-bold truncate transition-colors ${fails ? 'text-red-400 drop-shadow-[0_0_5px_rgba(248,113,113,0.5)]' : 'text-text-secondary group-hover/test:text-green-400'}`}>
                        {r.test_name}
                      </span>
                      {fails && <span className="pill-critical opacity-90 text-[8px] py-0">ERR</span>}
                    </div>
                    
                    <div className="flex items-center gap-3 shrink-0">
                      <div className="text-right">
                        <div className="text-mono-caps text-[8px] text-text-secondary">LATENCY</div>
                        <div className={`font-mono text-[11px] font-bold ${fails ? 'text-red-400' : 'text-cyan-400'}`}>{r.duration_ms}ms</div>
                      </div>
                      
                      {onFeedback && fails && (
                        <button
                          onClick={() => onFeedback(r.test_name)}
                          className="text-text-secondary hover:text-fuchsia-400 hover:drop-shadow-[0_0_5px_rgba(232,121,249,0.8)] transition-all p-1"
                          title="Flag false positive"
                        >
                          <FlagIcon />
                        </button>
                      )}
                    </div>
                  </div>
                  
                  {fails && (
                    <div className="bg-red-500/10 border-l-2 border-red-500 p-2 my-2 rounded-r font-mono text-[10px] text-red-400 break-all leading-relaxed relative shadow-[inset_0_0_10px_rgba(239,68,68,0.05)]">
                      {'> '}Playwright Assert Error trace logged during execution...
                    </div>
                  )}

                  {r.video_url && (
                    <div className="w-full mt-2 rounded bg-[#080808] border border-border-light overflow-hidden group/video">
                      <video
                        controls
                        className="w-full max-h-[140px] object-contain opacity-70 group-hover/video:opacity-100 transition-opacity"
                        preload="metadata"
                      >
                        <source src={`http://localhost:8000${r.video_url}`} type="video/webm" />
                      </video>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center font-mono text-xs text-text-tertiary">
            NO_EXECUTION_LOGS_AVAILABLE
          </div>
        )}
      </div>

      {/* Actions */}
      {result.report_filename && onViewReport && (
        <div className="mt-auto pt-2">
          <button
            onClick={() => onViewReport(result.report_filename)}
            className="w-full btn-ghost border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10 hover:border-cyan-400 hover:shadow-[0_0_15px_rgba(34,211,238,0.2)] py-3 text-[10px] tracking-widest flex items-center justify-center gap-2 rounded-md"
          >
            <ChartIcon /> OPEN_FULL_TRACE
          </button>
        </div>
      )}
    </div>
  )
}
