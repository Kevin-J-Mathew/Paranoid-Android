import React from 'react'
import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard.jsx'
import RunHistory from './pages/RunHistory.jsx'
import KnowledgeBase from './pages/KnowledgeBase.jsx'

/* SVG Icons for Navbar */
const SearchIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" /></svg>
)
const TerminalIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="4 17 10 11 4 5" /><line x1="12" x2="20" y1="19" y2="19" /></svg>
)
const SettingsIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" /></svg>
)
const UserIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
)

/* SVG Icons for Sidebar */
const CoreIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" /></svg>
)
const OrchestratorIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" /></svg>
)
const TestRunsIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect width="18" height="18" x="3" y="3" rx="2" /><path d="M7 7h10" /><path d="M7 12h10" /><path d="M7 17h10" /></svg>
)
const IntelIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" /></svg>
)
const RegistryIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><ellipse cx="12" cy="5" rx="9" ry="3" /><path d="M3 5V19A9 3 0 0 0 21 19V5" /><path d="M3 12A9 3 0 0 0 21 12" /></svg>
)
const LogsIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" /><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" /></svg>
)

const NAV_ITEMS = [
  { to: '/', label: 'Orchestrator', icon: OrchestratorIcon, end: true },
  { to: '/history', label: 'Test_Runs', icon: TestRunsIcon },
  { to: '/knowledge', label: 'Intelligence', icon: IntelIcon },
]

export default function App() {
  const location = useLocation()

  // Helper to sync topnav and sidebar active states
  const isActiveTab = (path) => {
    if (path === '/') return location.pathname === '/'
    return location.pathname.startsWith(path)
  }

  return (
    <div className="min-h-screen bg-surface-base p-6 font-sans">
      <div className="main-window-wrapper h-[calc(100vh-48px)]">

        {/* Top Header */}
        <header className="h-16 border-b border-border-light flex items-center justify-between px-6 shrink-0 z-10 bg-surface-container">
          <div className="flex items-center gap-10">
            {/* Logo */}
            <div className="font-mono font-bold text-cyan-400 tracking-wider drop-shadow-[0_0_10px_rgba(34,211,238,0.8)] text-lg select-none">
              PARANOID ANDROID
            </div>

            {/* Top Nav Tabs */}
            <nav className="hidden md:flex flex-row items-center gap-6 h-full mt-0.5">
              {[
                { path: '/', label: 'ORCHESTRATOR' },
                { path: '/history', label: 'TEST_RUNS' },
                { path: '/knowledge', label: 'INTELLIGENCE' }
              ].map(tab => {
                const active = isActiveTab(tab.path)
                return (
                  <NavLink
                    key={tab.path}
                    to={tab.path}
                    className={`text-mono-caps text-xs h-16 flex items-center relative transition-colors ${active ? 'text-cyan-400 drop-shadow-[0_0_5px_rgba(34,211,238,0.5)]' : 'text-text-secondary hover:text-text-primary'
                      }`}
                  >
                    {tab.label}
                    {active && (
                      <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.8)]"></div>
                    )}
                  </NavLink>
                )
              })}
            </nav>
          </div>

          <div className="flex items-center gap-6">
            {/* Nav area spacing if needed */}
          </div>
        </header>

        {/* Body Container */}
        <div className="flex flex-1 overflow-hidden bg-surface-container">

          {/* Left Sidebar */}
          <aside className="w-64 border-r border-border-light flex flex-col pt-6 pb-4">
            {/* Node Status Box */}
            <div className="mx-4 mb-8 bg-surface-panel border border-border-light rounded-lg p-3 flex items-center gap-3">
              <div className="w-8 h-8 rounded bg-cyan-500/10 flex items-center justify-center text-cyan-400 border border-cyan-500/30 shadow-[0_0_15px_rgba(34,211,238,0.1)] group hover:shadow-[0_0_20px_rgba(34,211,238,0.2)] transition-shadow cursor-default">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="4" y="4" width="16" height="16" rx="2" ry="2" /><rect x="9" y="9" width="6" height="6" /><line x1="9" y1="1" x2="9" y2="4" /><line x1="15" y1="1" x2="15" y2="4" /><line x1="9" y1="20" x2="9" y2="23" /><line x1="15" y1="20" x2="15" y2="23" /><line x1="20" y1="9" x2="23" y2="9" /><line x1="20" y1="14" x2="23" y2="14" /><line x1="1" y1="9" x2="4" y2="9" /><line x1="1" y1="14" x2="4" y2="14" /></svg>
              </div>
              <div>
                <div className="text-text-primary font-mono text-xs font-bold leading-tight">NODE_01</div>
                <div className="text-text-secondary font-mono text-[10px] leading-tight mt-0.5">Active_Session</div>
              </div>
            </div>

            {/* Sidebar Nav */}
            <nav className="flex-1 px-3 space-y-1">
              {NAV_ITEMS.map(item => {
                const active = isActiveTab(item.to) && item.to !== '#registry' && item.to !== '#logs'
                return (
                  <NavLink
                    key={item.label}
                    to={item.to}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all duration-300 relative group overflow-hidden ${active ? 'bg-cyan-500/10 text-cyan-400 shadow-[inset_0_0_15px_rgba(34,211,238,0.1)] border border-cyan-500/20' : 'text-text-secondary hover:text-text-primary hover:bg-surface-panel border border-transparent'
                      }`}
                  >
                    {/* Background glow sweep on active */}
                    {active && <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/20 to-transparent opacity-50"></div>}
                    
                    {active && <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.8)] rounded-r"></div>}
                    <span className={`opacity-80 group-hover:opacity-100 relative z-10 ${active ? 'opacity-100 drop-shadow-[0_0_5px_rgba(34,211,238,0.5)]' : ''}`}>
                      <item.icon />
                    </span>
                    <span className="relative z-10">{item.label}</span>
                  </NavLink>
                )
              })}
            </nav>
          </aside>

          {/* Main Route Content */}
          <main className="flex-1 overflow-auto bg-surface-container">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/history" element={<RunHistory />} />
              <Route path="/knowledge" element={<KnowledgeBase />} />
            </Routes>
          </main>
        </div>
      </div>
    </div>
  )
}
