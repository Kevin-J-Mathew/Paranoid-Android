import React from 'react'

export default function ReportModal({ reportUrl, onClose }) {
  if (!reportUrl) return null

  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl w-full max-w-6xl h-[90vh] flex flex-col shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b bg-slate-800 rounded-t-xl">
          <h2 className="text-white font-bold text-lg">📊 Test Report</h2>
          <div className="flex items-center gap-3">
            <a
              href={reportUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              Open in New Tab ↗
            </a>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white text-2xl leading-none transition-colors"
            >
              ×
            </button>
          </div>
        </div>
        <iframe
          src={reportUrl}
          className="flex-1 w-full rounded-b-xl"
          title="Test Report"
        />
      </div>
    </div>
  )
}
