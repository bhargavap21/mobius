import React, { useEffect, useState, useCallback } from 'react'
import StrategySidebar from './StrategySidebar'

const LS_KEY = 'refineSidebarOpen'

const RefineSidebar = ({ currentStrategy, onRefineStrategy, onRunBacktest }) => {
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

  // Persist to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(LS_KEY, open ? '1' : '0')
    } catch (e) {
      console.error('Failed to save sidebar state:', e)
    }
  }, [open])

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
    <div className="fixed inset-y-0 right-0 z-40 flex items-stretch pointer-events-none">
      {/* Slide-in drawer */}
      <aside
        role="complementary"
        aria-label="Refine Strategy"
        className={`pointer-events-auto h-full w-[380px] md:w-[420px] border-l border-white/10 bg-[#0f1117] shadow-xl transition-transform duration-300 ease-out ${
          open ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {/* Keep your existing refine panel inside */}
        <StrategySidebar
          isOpen={open}
          onClose={close}
          currentStrategy={currentStrategy}
          onRefineStrategy={onRefineStrategy}
          onRunBacktest={onRunBacktest}
        />
      </aside>

      {/* Vertical handle */}
      <button
        type="button"
        aria-label={open ? 'Close refine panel' : 'Open refine panel'}
        aria-expanded={open}
        onClick={toggle}
        className="pointer-events-auto my-auto mr-0 flex h-28 -translate-x-2 items-center justify-center rounded-l-xl border border-r-0 border-white/10 bg-white/5 px-2 text-white/80 backdrop-blur transition hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-accent"
      >
        <span
          className={`inline-flex rotate-90 select-none text-xs font-medium tracking-wide ${
            open ? 'text-accent' : 'text-white/70'
          }`}
        >
          Refine
        </span>
      </button>
    </div>
  )
}

export default RefineSidebar

