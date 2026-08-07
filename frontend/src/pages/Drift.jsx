import React, {useState, useEffect, useRef} from 'react'
import { getDrift } from '../api/api'

export default function Drift(){
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [auto, setAuto] = useState(false)
  const timer = useRef(null)

  const run = async ()=>{
    setLoading(true)
    try{ const r = await getDrift(); setData(r.data) }catch(e){ setData(null) }
    setLoading(false)
  }

  useEffect(()=>{
    if(auto){ run(); timer.current = setInterval(run, 30000); }
    return ()=> clearInterval(timer.current)
  },[auto])

  return (
    <div className="space-y-6">
      <div className="card p-4 flex items-center gap-4">
        <button onClick={run} className="px-4 py-2 bg-accent rounded">{loading? 'Checking...':'Check Drift'}</button>
        <label className="flex items-center gap-2"><input type="checkbox" checked={auto} onChange={e=>setAuto(e.target.checked)} /> Auto-refresh 30s</label>
      </div>

      {data && (
        <div className="card p-4 rounded">
          <div className="flex gap-4 items-center">
            <div className={`px-3 py-1 rounded ${data.drift_detected? 'bg-red-600':'bg-green-600'}`}>{data.drift_detected? 'Drift Detected':'No Drift'}</div>
            <div>Drift Score: <strong>{Number(data.drift_score).toFixed(3)}</strong></div>
          </div>
          <div className="mt-4">
            <div className="font-bold">Affected Features</div>
            <ul className="mt-2 list-disc ml-6">
              {data.affected_features && data.affected_features.length ? data.affected_features.map(f=> <li key={f} className="text-yellow-300">{f}</li>) : <li className="text-sm opacity-80">None</li>}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
