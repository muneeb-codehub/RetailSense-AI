import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Forecast from './pages/Forecast'
import Segmentation from './pages/Segmentation'
import Explainability from './pages/Explainability'
import ABTest from './pages/ABTest'
import Drift from './pages/Drift'

export default function App(){
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6">
          <Routes>
            <Route path='/' element={<Dashboard/>} />
            <Route path='/forecast' element={<Forecast/>} />
            <Route path='/segmentation' element={<Segmentation/>} />
            <Route path='/explainability' element={<Explainability/>} />
            <Route path='/abtest' element={<ABTest/>} />
            <Route path='/drift' element={<Drift/>} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

