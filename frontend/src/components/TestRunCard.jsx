import React from 'react'

const STATUS_COLORS = {
  passed: 'text-green-400',
  failed: 'text-red-400',
  error: 'text-orange-400',
  running: 'text-blue-400',
}

const RISK_COLORS = {
  critical: 'text-red-400 bg-red-900/30 border-red-700',
  high: 'text-orange-400 bg-orange-900/30 border-orange-700',
  medium: 'text-yellow-400 bg-yellow-900/30 border-yellow-700',
  low: 'text-green-400 bg-green-900/30 border-green-700',
  none: 'text-green-400 bg-green-900/30 border-green-700',
  unknown: 'text-slate-400 bg-slate-800 border-slate-600',
}

export default function TestRunCard({ result, onViewReport, onFeedback }) {
  const total = result.total_tests || result.execution_results?.length || 0
  const passed = result.passed_tests || result.execution_results?.filter(r => r.status === 'passed').length || 0
  const failed = result.failed_tests || (total - passed)
  const passRate = total > 0 ? Math.round((passed / total) * 100) : 0
  const regressionRisk = result.regression_risk ||
    result.regression_analysis?.overall_regression_risk || 'unknown'

  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-5 hover:border-slate-600 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="bg-slate-700 text-slate-300 text-xs px-2 py-0.5 rounded font-mono">
              {result.story_id || result.run_id?.slice(0, 8)}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded border font-semibold uppercase ${RISK_COLORS[regressionRisk]}`}>
              {regressionRisk} risk
            </span>
          </div>
          <h3 className="text-white font-semibold text-sm truncate">
            {result.story_title || 'Test Run'}
          </h3>
          {result.created_at && (
            <p className="text-slate-500 text-xs mt-0.5">
              {new Date(result.created_at).toLocaleString()}
            </p>
          )}
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-white">{passRate}%</div>
          <div className="text-slate-400 text-xs">pass rate</div>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-slate-900 rounded-lg p-3 text-center">
          <div className="text-xl font-bold text-white">{total}</div>
          <div className="text-slate-500 text-xs">Total</div>
        </div>
        <div className="bg-slate-900 rounded-lg p-3 text-center">
          <div className="text-xl font-bold text-green-400">{passed}</div>
          <div className="text-slate-500 text-xs">Passed</div>
        </div>
        <div className="bg-slate-900 rounded-lg p-3 text-center">
          <div className="text-xl font-bold text-red-400">{failed}</div>
          <div className="text-slate-500 text-xs">Failed</div>
        </div>
      </div>

      {/* Pass rate bar */}
      <div className="w-full bg-slate-700 rounded-full h-1.5 mb-4">
        <div
          className={`h-1.5 rounded-full transition-all ${passRate >= 80 ? 'bg-green-500' : passRate >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
          style={{ width: `${passRate}%` }}
        />
      </div>

      {/* Test results list */}
      {result.execution_results && result.execution_results.length > 0 && (
        <div className="space-y-3 mb-4 max-h-96 overflow-y-auto pr-1">
          {result.execution_results.map((r, idx) => (
            <div key={idx} className="flex flex-col text-xs pb-3 border-b border-slate-700 last:border-0 last:pb-0">
              <div className="flex items-center justify-between w-full mb-1">
                <span className="text-slate-400 truncate flex-1 mr-2">{r.test_name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-slate-500">{r.duration_ms}ms</span>
                  <span className={`font-bold uppercase ${STATUS_COLORS[r.status] || 'text-slate-400'}`}>
                    {r.status}
                  </span>
                  {onFeedback && r.status === 'failed' && (
                    <button
                      onClick={() => onFeedback(r.test_name)}
                      className="text-slate-500 hover:text-yellow-400 transition-colors"
                      title="Mark as false positive"
                    >
                      🚩
                    </button>
                  )}
                </div>
              </div>
              
              {r.video_url && (
                <div className="w-full mt-2">
                  <video
                    controls
                    className="w-full rounded-lg border border-slate-700 bg-black"
                    style={{ maxHeight: '200px', objectFit: 'contain' }}
                  >
                    <source src={`http://localhost:8000${r.video_url}`} type="video/webm" />
                  </video>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      {result.report_filename && onViewReport && (
        <button
          onClick={() => onViewReport(result.report_filename)}
          className="w-full bg-slate-700 hover:bg-slate-600 text-white py-2 rounded-lg text-sm font-medium transition-colors"
        >
          📊 View Full Report
        </button>
      )}
    </div>
  )
}
