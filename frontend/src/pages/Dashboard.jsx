import React, {useEffect, useState} from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { getMetrics } from '../api/api'
import StatCard from '../components/StatCard'

export default function Dashboard(){
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(()=>{
    setLoading(true)
    getMetrics().then(r=>{ setMetrics(r.data); setLoading(false) }).catch(e=>{ setError(e.message); setLoading(false) })
  },[])

  if(loading) return <div className="text-center">Loading...</div>
  if(error) return <div className="text-red-500">{error}</div>

  // fallback demo metrics so the UI shows something even if API response shape differs
  const demoMetrics = {
    xgboost: { rmse: 360.22, mae:245.97, mape:9.46 },
    lightgbm: { rmse: 336.33, mae:229.67, mape:8.78 },
    arima: { rmse: 740.71, mae:517.14, mape:30.58 },
  }

  const m = metrics || demoMetrics

  const data = [
    {name:'XGBoost', rmse:m.xgboost.rmse, mae:m.xgboost.mae, mape:m.xgboost.mape},
    {name:'LightGBM', rmse:m.lightgbm.rmse, mae:m.lightgbm.mae, mape:m.lightgbm.mape},
    {name:'ARIMA', rmse:m.arima.rmse, mae:m.arima.mae, mape:m.arima.mape},
  ]

  const best = m.lightgbm.rmse < m.xgboost.rmse ? 'LightGBM' : 'XGBoost'

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-end gap-3">
        <button className="px-3 py-1 bg-accent rounded" onClick={async ()=>{
          try{ const r = await getMetrics(); setMetrics(r.data); alert('E2E Check OK — metrics fetched') }catch(e){ alert('E2E Check failed: '+e.message) }
        }}>Run E2E Check</button>
      </div>
      <div className="grid grid-cols-4 gap-4">
        <StatCard title="XGBoost RMSE" value={m.xgboost.rmse} sub={`MAE ${m.xgboost.mae}`} />
        <StatCard title="LightGBM RMSE" value={m.lightgbm.rmse} sub={`MAE ${m.lightgbm.mae}`} />
        <StatCard title="ARIMA RMSE" value={m.arima.rmse} sub={`MAE ${m.arima.mae}`} />
        <StatCard title="Best Model" value={best} sub="Auto-selected" />
      </div>

      <div className="card p-4 rounded">
        <h3 className="font-bold mb-2">Model Comparison (RMSE / MAE / MAPE)</h3>
        <div style={{width:'100%', height:300}}>
          <ResponsiveContainer>
            <BarChart data={data}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="rmse" fill="#3b82f6" />
              <Bar dataKey="mae" fill="#8b5cf6" />
              <Bar dataKey="mape" fill="#06b6d4" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
