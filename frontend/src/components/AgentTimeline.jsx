import React from 'react'

const AGENT_ICONS = {
  'Requirements Agent': '📋',
  'RAG Knowledge Agent': '🧠',
  'Test Generation Agent': '✏️',
  'Test Execution Agent': '▶️',
  'Regression Detection Agent': '🔍',
  'Report Agent': '📊',
  'Knowledge Store Agent': '💾',
}

const STATUS_STYLES = {
  completed: 'border-l-green-500 bg-green-500/5',
  running: 'border-l-blue-500 bg-blue-500/5 animate-pulse',
  failed: 'border-l-red-500 bg-red-500/5',
}

const STATUS_DOTS = {
  completed: 'bg-green-500',
  running: 'bg-blue-500 animate-ping',
  failed: 'bg-red-500',
}

export default function AgentTimeline({ steps = [], isRunning = false }) {
  if (steps.length === 0 && !isRunning) {
    return (
      <div className="text-slate-500 text-sm text-center py-8">
        Agent timeline will appear here when you start a run.
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {steps.map((step, idx) => (
        <div
          key={idx}
          className={`border-l-4 pl-4 pr-4 py-3 rounded-r-lg ${STATUS_STYLES[step.status] || 'border-l-slate-600 bg-slate-800/30'}`}
        >
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg">{AGENT_ICONS[step.agent_name] || '🤖'}</span>
            <span className="text-white font-semibold text-sm">{step.agent_name}</span>
            <div className={`w-2 h-2 rounded-full ml-auto ${STATUS_DOTS[step.status] || 'bg-slate-500'}`} />
          </div>
          <p className="text-slate-300 text-sm">{step.message}</p>
          {step.timestamp && (
            <p className="text-slate-500 text-xs mt-1">
              {new Date(step.timestamp).toLocaleTimeString()}
            </p>
          )}
          {step.data && step.status === 'completed' && (
            <div className="mt-2 flex flex-wrap gap-2">
              {step.data.test_count !== undefined && (
                <span className="bg-slate-700 text-slate-300 text-xs px-2 py-0.5 rounded">
                  {step.data.test_count} tests generated
                </span>
              )}
              {step.data.passed !== undefined && (
                <span className="bg-green-900/50 text-green-300 text-xs px-2 py-0.5 rounded">
                  {step.data.passed}/{step.data.total} passed
                </span>
              )}
              {step.data.overall_regression_risk && (
                <span className={`text-xs px-2 py-0.5 rounded font-bold uppercase ${
                  step.data.overall_regression_risk === 'none' || step.data.overall_regression_risk === 'low'
                    ? 'bg-green-900/50 text-green-300'
                    : step.data.overall_regression_risk === 'critical'
                    ? 'bg-red-900/50 text-red-300'
                    : 'bg-yellow-900/50 text-yellow-300'
                }`}>
                  {step.data.overall_regression_risk} risk
                </span>
              )}
            </div>
          )}
        </div>
      ))}
      {isRunning && (
        <div className="border-l-4 border-l-slate-600 pl-4 py-3">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
            <span className="text-slate-400 text-sm">Agents working...</span>
          </div>
        </div>
      )}
    </div>
  )
}
