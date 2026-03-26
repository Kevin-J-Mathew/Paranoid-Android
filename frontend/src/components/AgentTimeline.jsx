import React from 'react'

const ClockIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="mb-4 text-text-tertiary"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
)

/* SVG Icons mapped to terminal style */
const AgentIcons = {
  'Requirements Agent': (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/></svg>
  ),
  'RAG Knowledge Agent': (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
  ),
  'Test Generation Agent': (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
  ),
  'Test Execution Agent': (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
  ),
  'Regression Detection Agent': (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
  ),
  'Report Agent': (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
  ),
  'Knowledge Store Agent': (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>
  ),
}

const STATUS_TINT = {
  completed: 'text-accent-cyan',
  running: 'text-accent-fuchsia animate-pulse',
  failed: 'text-accent-red',
}

export default function AgentTimeline({ steps = [], isRunning = false }) {
  if (steps.length === 0 && !isRunning) {
    return (
      <div className="h-full mt-24 text-text-tertiary text-xs text-mono-caps text-center flex flex-col items-center justify-center">
        <ClockIcon />
        <span>WAITING_FOR_PROCESS_START...</span>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {steps.map((step, idx) => (
        <div
          key={idx}
          className="bg-surface-card border border-border-light rounded-lg p-4 flex items-start gap-4 animate-slide-up"
          style={{ animationDelay: `${idx * 50}ms` }}
        >
          {/* Left Icon Box (Mimicking screenshot recommendation icon) */}
          <div className="w-8 h-8 rounded-full bg-surface-base border border-border-light flex items-center justify-center shrink-0">
            <span className={STATUS_TINT[step.status] || 'text-text-secondary'}>
              {AgentIcons[step.agent_name] || (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/></svg>
              )}
            </span>
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-1">
              <span className="font-bold text-text-primary text-sm tracking-wide">{step.agent_name}</span>
              {step.timestamp && (
                <span className="text-text-secondary opacity-60 text-[10px] font-mono tracking-wider">
                  {new Date(step.timestamp).toLocaleTimeString()}
                </span>
              )}
            </div>
            
            <p className="text-text-secondary text-xs leading-[1.6]">{step.message}</p>

            {step.data && step.status === 'completed' && (
              <div className="mt-3 flex flex-wrap gap-2">
                {step.data.test_count !== undefined && (
                  <span className="bg-surface-base border border-border-light text-text-secondary font-mono text-[9px] px-2 py-0.5 rounded uppercase">
                    {step.data.test_count}_TESTS_GEN
                  </span>
                )}
                {step.data.passed !== undefined && (
                  <span className="bg-accent-cyan/10 border border-accent-cyan/20 text-accent-cyan font-mono text-[9px] px-2 py-0.5 rounded uppercase font-bold">
                    PASS_RATE: {step.data.passed}/{step.data.total}
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      ))}
      
      {isRunning && (
        <div className="bg-surface-card border border-border-light border-dashed rounded-lg p-4 flex items-center gap-4 animate-pulse">
           <div className="w-8 h-8 rounded-full bg-surface-base border border-accent-cyan flex items-center justify-center shrink-0">
             <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00E5FF" strokeWidth="2" className="animate-spin">
               <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
             </svg>
          </div>
          <div className="flex-1">
            <span className="font-bold text-accent-cyan text-sm tracking-wide">PROCESS_ACTIVE</span>
            <p className="text-text-secondary text-xs mt-0.5">Asynchronous orchestration in progress...</p>
          </div>
        </div>
      )}
    </div>
  )
}
