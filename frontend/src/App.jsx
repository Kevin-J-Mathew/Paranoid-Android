import React from 'react'
import { Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard.jsx'
import RunHistory from './pages/RunHistory.jsx'
import KnowledgeBase from './pages/KnowledgeBase.jsx'

const NAV_ITEMS = [
  { to: '/', label: '⚡ Dashboard', end: true },
  { to: '/history', label: '📋 Run History' },
  { to: '/knowledge', label: '🧠 Knowledge Base' },
]

export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-700 px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">S</div>
          <div>
            <h1 className="text-white font-bold text-lg leading-tight">Sentinel-Agent</h1>
            <p className="text-slate-400 text-xs">Autonomous Context-Aware QA Orchestrator</p>
          </div>
        </div>
        <nav className="flex gap-1">
          {NAV_ITEMS.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/history" element={<RunHistory />} />
          <Route path="/knowledge" element={<KnowledgeBase />} />
        </Routes>
      </main>
    </div>
  )
}
