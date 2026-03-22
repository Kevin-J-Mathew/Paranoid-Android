import React, { useState, useEffect, useCallback } from 'react'
import { api, createSSEConnection } from '../api.js'
import StoryInputPanel from '../components/StoryInputPanel.jsx'
import AgentTimeline from '../components/AgentTimeline.jsx'
import TestRunCard from '../components/TestRunCard.jsx'
import ReportModal from '../components/ReportModal.jsx'

export default function Dashboard() {
  const [stories, setStories] = useState([])
  const [storiesSource, setStoriesSource] = useState('mock')
  const [currentRunId, setCurrentRunId] = useState(null)
  const [agentSteps, setAgentSteps] = useState([])
  const [isRunning, setIsRunning] = useState(false)
  const [completedRun, setCompletedRun] = useState(null)
  const [recentRuns, setRecentRuns] = useState([])
  const [reportUrl, setReportUrl] = useState(null)
  const [statusMessage, setStatusMessage] = useState('')

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
    setAgentSteps([])
    setCompletedRun(null)
    setStatusMessage('Initializing agents...')

    try {
      const res = await api.startRun(storyData)
      const runId = res.data.run_id
      setCurrentRunId(runId)
      setStatusMessage('Agents running...')

      const sse = createSSEConnection(
        runId,
        (step) => {
          setAgentSteps(prev => [...prev, step])
          setStatusMessage(step.message)
        },
        (finalData) => {
          setCompletedRun(finalData)
          setIsRunning(false)
          setStatusMessage('✅ Run complete!')
          // Refresh recent runs
          api.listRuns()
            .then(r => setRecentRuns((r.data.runs || []).slice(0, 3)))
            .catch(console.error)
        },
        (err) => {
          setIsRunning(false)
          setStatusMessage('❌ Run failed. Check console.')
        }
      )
    } catch (e) {
      console.error(e)
      setIsRunning(false)
      setStatusMessage('❌ Failed to start run: ' + (e.response?.data?.detail || e.message))
    }
  }, [])

  const handleViewReport = (filename) => {
    setReportUrl(api.getReportUrl(filename))
  }

  const handleFeedback = async (testName) => {
    if (!currentRunId) return
    await api.submitFeedback(currentRunId, testName, true)
    alert(`Marked "${testName}" as false positive. System will learn from this!`)
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white">Dashboard</h2>
        <p className="text-slate-400 text-sm mt-1">
          Select a user story to autonomously generate, execute, and analyze tests.
          {storiesSource === 'jira' ? (
            <span className="ml-2 text-blue-400">● Connected to Jira</span>
          ) : (
            <span className="ml-2 text-yellow-400">● Using demo stories (configure Jira in .env to connect)</span>
          )}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Story Input */}
        <div>
          <h3 className="text-slate-300 font-semibold text-sm uppercase tracking-wider mb-3">
            📥 User Stories
          </h3>
          <StoryInputPanel
            stories={stories}
            onRunStory={handleRunStory}
            isRunning={isRunning}
          />
        </div>

        {/* Right: Agent Timeline */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-slate-300 font-semibold text-sm uppercase tracking-wider">
              🤖 Agent Execution Timeline
            </h3>
            {isRunning && (
              <span className="text-blue-400 text-xs font-medium animate-pulse">
                ● LIVE
              </span>
            )}
            {statusMessage && !isRunning && (
              <span className="text-slate-400 text-xs">{statusMessage}</span>
            )}
          </div>
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 min-h-64">
            <AgentTimeline steps={agentSteps} isRunning={isRunning} />
          </div>
        </div>
      </div>

      {/* Current Run Result */}
      {completedRun && (
        <div className="mt-6">
          <h3 className="text-slate-300 font-semibold text-sm uppercase tracking-wider mb-3">
            ✅ Latest Run Results
          </h3>
          <TestRunCard
            result={{
              run_id: completedRun.run_id,
              story_id: completedRun.run_id?.slice(0, 8),
              story_title: 'Latest Run',
              execution_results: completedRun.execution_results || [],
              regression_analysis: completedRun.regression_analysis || {},
              report_filename: completedRun.report_filename,
            }}
            onViewReport={handleViewReport}
            onFeedback={handleFeedback}
          />
        </div>
      )}

      {/* Recent Runs */}
      {recentRuns.length > 0 && (
        <div className="mt-6">
          <h3 className="text-slate-300 font-semibold text-sm uppercase tracking-wider mb-3">
            📋 Recent Runs
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentRuns.map(run => (
              <TestRunCard
                key={run.id}
                result={run}
                onViewReport={handleViewReport}
              />
            ))}
          </div>
        </div>
      )}

      {/* Report Modal */}
      <ReportModal
        reportUrl={reportUrl}
        onClose={() => setReportUrl(null)}
      />
    </div>
  )
}
