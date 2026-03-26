import React from 'react'
import { createPortal } from 'react-dom'

const CloseIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
)

const MaximizeIcon = () => (
  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/></svg>
)

const MinimizeIcon = () => (
   <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="5" y1="12" x2="19" y2="12"/></svg>
)

export default function ReportModal({ reportUrl, onClose }) {
  if (!reportUrl) return null

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 animate-fade-in">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-surface-base/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal Window Container */}
      <div className="relative w-full max-w-6xl h-[85vh] flex flex-col bg-surface-base rounded-lg border border-border-light shadow-[0_0_50px_rgba(99,102,241,0.15)] overflow-hidden">
        
        {/* Browser native-like Header */}
        <div className="h-10 bg-[#161616] border-b border-border-light flex items-center justify-between px-4 shrink-0 select-none">
          <div className="flex items-center gap-2">
             <button onClick={onClose} className="w-3 h-3 rounded-full bg-accent-red hover:brightness-110 flex items-center justify-center group"><CloseIcon className="w-2 h-2 opacity-0 group-hover:opacity-100 text-black"/></button>
             <button className="w-3 h-3 rounded-full bg-[#fbbc05] hover:brightness-110 flex items-center justify-center group"><MinimizeIcon className="w-2 h-2 opacity-0 group-hover:opacity-100 text-black"/></button>
             <button className="w-3 h-3 rounded-full bg-accent-green hover:brightness-110 flex items-center justify-center group"><MaximizeIcon className="w-2 h-2 opacity-0 group-hover:opacity-100 text-black"/></button>
          </div>
          
          <div className="flex-1 flex justify-center">
            <div className="bg-[#080808] border border-border-light text-text-secondary text-[10px] font-mono px-4 py-1 rounded w-1/2 text-center truncate">
              playwright://report/{reportUrl.split('/').pop()}
            </div>
          </div>
          
          <div className="w-16"></div> {/* Spacer to center URL */}
        </div>

        {/* Content Area */}
        <div className="flex-1 bg-white relative">
          <iframe 
            src={reportUrl} 
            title="Playwright HTML Report"
            className="w-full h-full border-0 absolute inset-0"
            sandbox="allow-scripts allow-same-origin allow-popups"
          />
        </div>
      </div>
    </div>,
    document.body
  )
}
