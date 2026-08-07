import React from 'react'

export default function Navbar() {
  return (
    <header className="flex items-center justify-between p-4 border-b border-slate-700 card">
      <div>
        <div className="text-xl font-bold">RetailSense AI</div>
        <div className="text-sm text-slate-300">Retail Demand Forecasting</div>
      </div>
      <div className="text-sm text-slate-300">v1.0</div>
    </header>
  )
}
