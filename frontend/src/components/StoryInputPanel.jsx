import React, { useState } from 'react'

export default function StoryInputPanel({ stories = [], onRunStory, isRunning = false }) {
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
    <div className="bg-slate-800 rounded-xl border border-slate-700">
      {/* Tabs */}
      <div className="flex border-b border-slate-700">
        <button
          onClick={() => setActiveTab('jira')}
          className={`flex-1 py-3 text-sm font-medium transition-colors rounded-tl-xl ${
            activeTab === 'jira' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-white'
          }`}
        >
          🎯 Jira / Demo Stories
        </button>
        <button
          onClick={() => setActiveTab('manual')}
          className={`flex-1 py-3 text-sm font-medium transition-colors rounded-tr-xl ${
            activeTab === 'manual' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-white'
          }`}
        >
          ✏️ Manual Input
        </button>
      </div>

      <div className="p-4">
        {activeTab === 'jira' ? (
          <div className="space-y-3">
            <p className="text-slate-400 text-xs mb-3">
              {stories.length > 0 ? `${stories.length} stories loaded. Click "Run Tests" on any story.` : 'Loading stories...'}
            </p>
            {stories.map(story => (
              <div
                key={story.id}
                className="bg-slate-900 rounded-lg p-4 border border-slate-700 hover:border-blue-500/50 transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="bg-blue-600 text-white text-xs px-2 py-0.5 rounded font-mono">{story.id}</span>
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        story.priority === 'high' ? 'bg-red-900/50 text-red-300' : 'bg-yellow-900/50 text-yellow-300'
                      }`}>
                        {story.priority || 'medium'}
                      </span>
                    </div>
                    <h3 className="text-white text-sm font-semibold mb-1 truncate">{story.title}</h3>
                    <p className="text-slate-400 text-xs line-clamp-2">{story.description}</p>
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
                    className="shrink-0 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white px-3 py-2 rounded-lg text-xs font-semibold transition-colors"
                  >
                    {isRunning ? '⟳ Running' : '▶ Run Tests'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            <div>
              <label className="text-slate-400 text-xs font-medium block mb-1">Story Title *</label>
              <input
                type="text"
                value={manualTitle}
                onChange={e => setManualTitle(e.target.value)}
                placeholder="As a user, I want to..."
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500 placeholder-slate-600"
              />
            </div>
            <div>
              <label className="text-slate-400 text-xs font-medium block mb-1">Description *</label>
              <textarea
                value={manualDesc}
                onChange={e => setManualDesc(e.target.value)}
                placeholder="Detailed description of the feature..."
                rows={4}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500 placeholder-slate-600 resize-none"
              />
            </div>
            <div>
              <label className="text-slate-400 text-xs font-medium block mb-1">Acceptance Criteria</label>
              <textarea
                value={manualCriteria}
                onChange={e => setManualCriteria(e.target.value)}
                placeholder="GIVEN... WHEN... THEN..."
                rows={3}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500 placeholder-slate-600 resize-none"
              />
            </div>
            <button
              onClick={handleRunManual}
              disabled={isRunning || !manualTitle.trim() || !manualDesc.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white py-2.5 rounded-lg font-semibold text-sm transition-colors"
            >
              {isRunning ? '⟳ Agents Running...' : '▶ Generate & Run Tests'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
