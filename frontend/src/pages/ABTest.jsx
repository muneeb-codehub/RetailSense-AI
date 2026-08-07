import React, {useState} from 'react'
import { postABTest } from '../api/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

// realistic sample payload: 20 samples with typical numeric feature keys used by forecasting
const makeSample = (n=20) => {
  const rows = []
  const trues = []
  for(let i=0;i<n;i++){
    rows.push({
      onpromotion: Math.round(Math.random()*3),
      year: 2017,
      month: Math.ceil(Math.random()*12),
      day: Math.ceil(Math.random()*28),
      dayofweek: Math.floor(Math.random()*7),
      weekofyear: Math.ceil(Math.random()*52),
      quarter: Math.ceil(Math.random()*4),
      is_weekend: Math.random()>0.7?1:0,
      is_holiday: Math.random()>0.95?1:0,
      lag_7: Math.random()*200,
      lag_14: Math.random()*200,
      lag_28: Math.random()*200,
      rolling_7_mean: Math.random()*200,
      rolling_14_mean: Math.random()*200,
      rolling_7_std: Math.random()*50,
      dcoilwtico: 60 + Math.random()*20,
      transactions: 500 + Math.random()*2500,
      cluster: Math.ceil(Math.random()*16),
    })
    trues.push(200 + Math.random()*500)
  }
  return {features: rows, true_values: trues}
}

const samplePayload = makeSample(20)

export default function ABTest(){
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const run = async ()=>{
    setLoading(true)
    try{ const r = await postABTest(samplePayload); setResult(r.data) }catch(e){alert(e.message)}
    setLoading(false)
  }

  // normalize result fields for display
  const xgb = result?.xgboost?.mae ?? result?.xgb_mae ?? result?.xgb_mae
  const lgb = result?.lightgbm?.mae ?? result?.lgb_mae ?? result?.lgb_mae
  const tstat = result?.t_statistic ?? result?.t_stat ?? null
  const pval = result?.p_value ?? result?.p_value ?? null
  const winner = result?.winner ?? (xgb && lgb ? (xgb < lgb ? 'XGBoost' : 'LightGBM') : '—')

  return (
    <div className="space-y-6">
      <div className="card p-4 flex gap-2">
        <button onClick={run} className="px-4 py-2 bg-accent rounded">{loading? 'Running...':'Run A/B Test'}</button>
      </div>

      {result && (
        <div className="card p-4 rounded">
          <div className="flex gap-4">
            <div className="p-3 card rounded">XGBoost MAE: <div className="font-bold">{xgb ?? '—'}</div></div>
            <div className="p-3 card rounded">LightGBM MAE: <div className="font-bold">{lgb ?? '—'}</div></div>
            <div className="p-3 card rounded">Winner: <div className="font-bold text-green-400">{winner}</div></div>
          </div>
          <div style={{width:'100%', height:250}} className="mt-4">
            <ResponsiveContainer>
              <BarChart data={[{name:'XGBoost', mae: xgb ?? 0}, {name:'LightGBM', mae: lgb ?? 0}] }>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="mae" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4">T-stat: {tstat ?? '—'} • P-value: {pval ?? '—'}</div>
        </div>
      )}
    </div>
  )
}
