import React from 'react'
import { NavLink } from 'react-router-dom'

const links = [
  ['/', 'Dashboard'],
  ['/forecast', 'Forecast'],
  ['/segmentation', 'Segmentation'],
  ['/explainability', 'Explainability'],
  ['/abtest', 'A/B Test'],
  ['/drift', 'Drift']
]

export default function Sidebar(){
  return (
    <aside className="w-60 p-4 space-y-4">
      <nav className="space-y-2">
        {links.map(([to, label]) => (
          <NavLink key={to} to={to} className={({isActive})=>`block p-3 rounded ${isActive? 'bg-accent/20 text-white':'text-slate-300 hover:bg-white/5'}`}>
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
