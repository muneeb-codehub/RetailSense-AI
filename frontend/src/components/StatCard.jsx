import React from 'react'

export default function StatCard({title, value, subtitle}){
  return (
    <div className="p-4 card">
      <div className="text-sm text-slate-300">{title}</div>
      <div className="text-2xl font-semibold mt-2">{value}</div>
      {subtitle && <div className="text-xs text-slate-400 mt-1">{subtitle}</div>}
    </div>
  )
}
