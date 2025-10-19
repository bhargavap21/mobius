import React, { useEffect, useState, useCallback } from 'react'
import StrategySidebar from './StrategySidebar'

const LS_KEY = 'refineSidebarOpen'

const RefineSidebar = ({ currentStrategy, onRefineStrategy, onRunBacktest, onOpenChange }) => {
  const [open, setOpen] = useState(false)

  // Seed from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem(LS_KEY)
      if (saved !== null) setOpen(saved === '1')
    } catch (e) {
      console.error('Failed to load sidebar state:', e)
    }
  }, [])

  // Persist to localStorage and notify parent
  useEffect(() => {
    try {
      localStorage.setItem(LS_KEY, open ? '1' : '0')
      onOpenChange?.(open)
    } catch (e) {
      console.error('Failed to save sidebar state:', e)
    }
  }, [open, onOpenChange])

  const toggle = useCallback(() => setOpen((v) => !v), [])
  const close = useCallback(() => setOpen(false), [])

  // Keyboard: Esc closes
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape' && open) close()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, close])

  return (
    <>
      {/* Fixed vertical handle - always visible and centered */}
      <button
        type="button"
        aria-label={open ? 'Close refine panel' : 'Open refine panel'}
        aria-expanded={open}
        onClick={toggle}
        className={`fixed top-1/2 -translate-y-1/2 flex h-28 w-10 items-center justify-center rounded-l-xl border border-r-0 border-white/10 bg-white/5 px-2 text-white/80 backdrop-blur transition-all duration-300 hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-accent z-50 ${
          open ? 'right-[380px] md:right-[420px]' : 'right-0'
        }`}
      >
        <span
          className={`inline-flex rotate-90 select-none text-xs font-medium tracking-wide transition-colors ${
            open ? 'text-accent' : 'text-white/70'
          }`}
        >
          Refine
        </span>
      </button>

      {/* Slide-in drawer */}
      <aside
        role="complementary"
        aria-label="Refine Strategy"
        className={`fixed top-0 right-0 h-screen border-l border-white/10 bg-[#0f1117] shadow-xl transition-all duration-300 ease-out overflow-hidden z-40 ${
          open ? 'w-[380px] md:w-[420px]' : 'w-0'
        }`}
      >
        {/* Keep your existing refine panel inside */}
        <div className="w-[380px] md:w-[420px] h-full overflow-y-auto">
          <StrategySidebar
            isOpen={open}
            onClose={close}
            currentStrategy={currentStrategy}
            onRefineStrategy={onRefineStrategy}
            onRunBacktest={onRunBacktest}
          />
        </div>
      </aside>
    </>
  )
}

export default RefineSidebar

