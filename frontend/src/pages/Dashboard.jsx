import React, { useState, useEffect, useCallback } from 'react'
import { api, createSSEConnection } from '../api.js'
import StoryInputPanel from '../components/StoryInputPanel.jsx'
import AgentTimeline from '../components/AgentTimeline.jsx'
import TestRunCard from '../components/TestRunCard.jsx'
import ReportModal from '../components/ReportModal.jsx'

/* SVG Icons */
const SettingsIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
)
const RunIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polygon points="5 3 19 12 5 21 5 3"/></svg>
)

export default function Dashboard() {
  const [stories, setStories] = useState([])
  const [storiesSource, setStoriesSource] = useState('mock')
  const [currentRunId, setCurrentRunId] = useState(null)
  const [agentSteps, setAgentSteps] = useState([])
  const [isRunning, setIsRunning] = useState(false)
  const [completedRun, setCompletedRun] = useState(null)
  const [reportUrl, setReportUrl] = useState(null)
  const [statusMessage, setStatusMessage] = useState('')
  const [activeStoryId, setActiveStoryId] = useState(null)

  useEffect(() => {
    api.getStories()
      .then(r => {
        setStories(r.data.stories || [])
        setStoriesSource(r.data.source)
      })
      .catch(console.error)

    api.listRuns()
      .then(r => setRecentRuns((r.data.runs || []).slice(0, 3)))
      .catch(console.error)
  }, [])

  const handleRunStory = useCallback(async (storyData) => {
    setIsRunning(true)
    setActiveStoryId(storyData.story_id || storyData.title)
    setAgentSteps([])
    setCompletedRun(null)
    setStatusMessage('INITIALIZING_AGENTS')

    try {
      const res = await api.startRun(storyData)
      const runId = res.data.run_id
      setCurrentRunId(runId)
      setStatusMessage('AGENTS_RUNNING')

      const sse = createSSEConnection(
        runId,
        (step) => {
          setAgentSteps(prev => [...prev, step])
          setStatusMessage(step.message)
        },
        (finalData) => {
          setCompletedRun(finalData)
          setIsRunning(false)
          setActiveStoryId(null)
          setStatusMessage('RUN_COMPLETE')
          api.listRuns()
            .then(r => setRecentRuns((r.data.runs || []).slice(0, 3)))
            .catch(console.error)
        },
        (err) => {
          setIsRunning(false)
          setActiveStoryId(null)
          setStatusMessage('RUN_FAILED_ERR')
        }
      )
    } catch (e) {
      console.error(e)
      setIsRunning(false)
      setActiveStoryId(null)
      setStatusMessage('START_FAILED_ERR')
    }
  }, [])

  return (
    <div className="p-8 max-w-7xl mx-auto animate-fade-in relative">
      {/* Top Section matching screenshot layout */}
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-10">
        <div className="max-w-3xl">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-accent-red"></span>
            <span className="text-accent-cyan text-[11px] font-mono tracking-widest font-bold uppercase">
              STATUS: {isRunning ? 'QA_ORCHESTRATOR_ACTIVE' : 'SYSTEM_READY_WAITING_INPUT'}
            </span>
          </div>
          
          <h2 className="text-4xl font-bold tracking-tight mb-4">Orchestrator Control</h2>
          
          <p className="text-text-secondary text-sm leading-relaxed max-w-2xl">
            Select a user story block below to autonomously generate, execute, and analyze end-to-end tests across the application layer. Active sessions will isolate state changes.
          </p>
          
          <div className="mt-4 flex items-center gap-2">
            <span className="text-text-secondary text-xs font-mono">SOURCE:</span>
            {storiesSource === 'jira' ? (
              <span className="text-text-primary text-[10px] bg-white/5 border border-white/10 px-2 py-0.5 rounded font-mono">JIRA_INTEGRATION</span>
            ) : (
              <span className="text-text-primary text-[10px] bg-white/5 border border-white/10 px-2 py-0.5 rounded font-mono">LOCAL_MOCK_DATA</span>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Container */}
        <div className="lg:col-span-7 bg-surface-panel rounded-xl border border-border-light p-6">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-border-light">
            <h3 className="text-mono-caps text-xs font-bold tracking-widest text-text-primary">
              WORKLOAD_QUEUE
            </h3>
            <span className="text-text-secondary text-[10px] font-mono tracking-widest">
              {stories.length} BLOCKS FOUND
            </span>
          </div>
          <StoryInputPanel
            stories={stories}
            onRunStory={handleRunStory}
            isRunning={isRunning}
            activeStoryId={activeStoryId}
          />
        </div>

        {/* Right Container */}
        <div className="lg:col-span-5 bg-surface-panel rounded-xl border border-border-light p-6">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-border-light">
            <h3 className="text-mono-caps text-xs font-bold tracking-widest text-text-primary flex items-center gap-2">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              EXECUTION_LOG
            </h3>
            {isRunning && (
              <span className="text-accent-cyan text-[10px] font-mono tracking-widest animate-pulse">
                {statusMessage}
              </span>
            )}
          </div>
          
          <div className="min-h-[400px]">
             <AgentTimeline steps={agentSteps} isRunning={isRunning} />
          </div>
        </div>
      </div>

      <ReportModal reportUrl={reportUrl} onClose={() => setReportUrl(null)} />
    </div>
  )
}
