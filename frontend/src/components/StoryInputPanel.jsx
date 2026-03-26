import React, { useState } from 'react'

const PlayIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
)
const SpinnerIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="animate-spin"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
)

export default function StoryInputPanel({ stories = [], onRunStory, isRunning = false, activeStoryId = null }) {
  const [activeTab, setActiveTab] = useState('jira')
  const [manualTitle, setManualTitle] = useState('')
  const [manualDesc, setManualDesc] = useState('')
  const [manualCriteria, setManualCriteria] = useState('')

  const handleRunManual = () => {
    if (!manualTitle.trim() || !manualDesc.trim()) return
    onRunStory({
      title: manualTitle,
      description: manualDesc,
      acceptance_criteria: manualCriteria,
      source: 'manual'
    })
  }

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="flex border-b border-border-light mb-5">
        <button
          onClick={() => setActiveTab('jira')}
          className={`px-1 py-3 mr-6 text-[10px] text-mono-caps transition-all duration-200 border-b-[2px] ${
            activeTab === 'jira'
              ? 'text-accent-cyan border-accent-cyan shadow-glow-cyan'
              : 'text-text-secondary border-transparent hover:text-text-primary'
          }`}
        >
          INTEGRATED_STORIES
        </button>
        <button
          onClick={() => setActiveTab('manual')}
          className={`px-1 py-3 text-[10px] text-mono-caps transition-all duration-200 border-b-[2px] ${
            activeTab === 'manual'
              ? 'text-accent-cyan border-accent-cyan shadow-glow-cyan'
              : 'text-text-secondary border-transparent hover:text-text-primary'
          }`}
        >
          MANUAL_OVERRIDE
        </button>
      </div>

      <div className="flex-1">
        {activeTab === 'jira' ? (
          <div className="space-y-4">
            {stories.map(story => (
              <div
                key={story.id}
                className="group bg-surface-base rounded-lg border border-border-light p-4 hover:border-accent-cyan/40 transition-all duration-300"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-1 mb-2">
                      <div className="flex items-center gap-3">
                        <h3 className="text-text-primary font-bold tracking-wide text-[15px]">{story.title}</h3>
                        {story.priority === 'high' ? (
                          <span className="pill-critical">HIGH_PRIORITY</span>
                        ) : (
                          <span className="pill-high">MEDIUM_PRIORITY</span>
                        )}
                      </div>
                      <div className="text-right">
                        <span className="text-text-secondary text-mono-caps text-[9px]">ID: </span>
                        <span className="text-accent-cyan text-mono-caps text-[11px] font-bold">{story.id}</span>
                      </div>
                    </div>
                    
                    <div className="text-text-secondary font-mono text-[10px] mb-3 opacity-70">
                      source: ./jira/epic/auth_flow.json
                    </div>
                    
                    <p className="text-text-secondary text-xs leading-relaxed mb-4 2xl:w-5/6">{story.description}</p>
                    
                    <div className="flex items-center justify-between mt-auto">
                      <div className="flex items-center gap-2 text-text-secondary text-mono-caps text-[9px] font-bold">
                        {isRunning && activeStoryId === story.id ? (
                          <>
                            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.8)] animate-pulse"></span>
                            <span className="text-cyan-400 drop-shadow-[0_0_5px_rgba(34,211,238,0.5)]">EXECUTING</span>
                          </>
                        ) : isRunning ? (
                          <>
                            <span className="w-1.5 h-1.5 rounded-full bg-text-tertiary"></span>
                            <span className="opacity-50">LOCKED</span>
                          </>
                        ) : (
                          <>
                            <span className="w-1.5 h-1.5 rounded-full bg-text-secondary"></span>
                            IDLE
                          </>
                        )}
                      </div>
                      
                      <button
                        onClick={() => onRunStory({
                          story_id: story.id,
                          title: story.title,
                          description: story.description,
                          acceptance_criteria: story.acceptance_criteria || '',
                          source: 'mock'
                        })}
                        disabled={isRunning}
                        className={`relative overflow-hidden px-4 py-1.5 rounded text-[10px] tracking-widest font-bold flex items-center gap-2 transition-all duration-300 ${
                          isRunning && activeStoryId === story.id
                            ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-400 shadow-[inset_0_0_15px_rgba(34,211,238,0.2),0_0_10px_rgba(34,211,238,0.5)] cursor-wait'
                            : isRunning
                            ? 'bg-transparent text-text-tertiary border border-border-light opacity-50 cursor-not-allowed'
                            : 'bg-transparent text-text-secondary border border-border-light hover:text-black hover:border-cyan-400 hover:shadow-[0_0_15px_rgba(34,211,238,0.6)] group/btn'
                        }`}
                      >
                        {/* Hover fill animation bg */}
                        {!isRunning && (
                          <div className="absolute inset-0 bg-cyan-400 translate-y-full group-hover/btn:translate-y-0 transition-transform duration-300 ease-out z-0"></div>
                        )}
                        
                        <div className="relative z-10 flex items-center gap-1.5 group-hover/btn:text-black">
                          {isRunning && activeStoryId === story.id ? <SpinnerIcon /> : <PlayIcon />}
                          {isRunning && activeStoryId === story.id ? 'EXECUTING...' : 'INIT_RUN'}
                        </div>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-5 bg-surface-base rounded-lg border border-border-light p-5">
            <div>
              <label className="text-text-secondary text-mono-caps text-[10px] block mb-2">TARGET_TITLE *</label>
              <input
                type="text"
                value={manualTitle}
                onChange={e => setManualTitle(e.target.value)}
                placeholder="DEFINE_OBJECTIVE..."
                className="w-full input-dark rounded px-3 py-2 transition-colors"
              />
            </div>
            <div>
              <label className="text-text-secondary text-mono-caps text-[10px] block mb-2">SPECIFICATION_BLOCK *</label>
              <textarea
                value={manualDesc}
                onChange={e => setManualDesc(e.target.value)}
                placeholder="DESCRIBE_FEATURE_REQUIREMENTS..."
                rows={4}
                className="w-full input-dark rounded px-3 py-2 resize-none transition-colors"
              />
            </div>
            <div>
              <label className="text-text-secondary text-mono-caps text-[10px] block mb-2">ACCEPTANCE_CRITERIA</label>
              <textarea
                value={manualCriteria}
                onChange={e => setManualCriteria(e.target.value)}
                placeholder="GIVEN... WHEN... THEN..."
                rows={3}
                className="w-full input-dark rounded px-3 py-2 resize-none transition-colors"
              />
            </div>
            <button
              onClick={handleRunManual}
              disabled={isRunning || !manualTitle.trim() || !manualDesc.trim()}
              className="w-full relative overflow-hidden bg-fuchsia-500/10 text-fuchsia-400 border border-fuchsia-500/50 hover:border-fuchsia-400 hover:shadow-[0_0_20px_rgba(232,121,249,0.5)] group/btn py-3 mt-4 flex items-center justify-center gap-2 rounded tracking-widest font-bold text-xs font-mono transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {!isRunning && (
                <div className="absolute inset-0 bg-fuchsia-400 translate-y-[101%] group-hover/btn:translate-y-0 transition-transform duration-300 ease-out z-0"></div>
              )}
              <div className="relative z-10 flex items-center gap-2 group-hover/btn:text-black transition-colors">
                {isRunning ? <><SpinnerIcon /> EXECUTING_MANUAL_PROCESS...</> : <><PlayIcon /> FORCE_EXECUTE</>}
              </div>
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
