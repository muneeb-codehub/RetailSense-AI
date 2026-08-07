import React, {useState} from 'react'
import { getExplain } from '../api/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function Explainability(){
  const [store, setStore] = useState(1)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  const run = async ()=>{
    setLoading(true)
    try{ const r = await getExplain(store); setData(Object.entries(r.data.feature_importance).map(([k,v])=>({name:k, value:v}))) }catch(e){alert(e.message)}
    setLoading(false)
  }

  return (
    <div className="space-y-6">
      <div className="card p-4 flex gap-2 items-end">
        <div>
          <label className="text-sm">Store #</label>
          <input type="number" value={store} onChange={e=>setStore(Number(e.target.value))} className="ml-2 p-2 rounded bg-page/40" />
        </div>
        <button onClick={run} className="px-4 py-2 bg-accent rounded">Run</button>
      </div>

      {data && (
        <div className="card p-4 rounded">
          <h3 className="font-bold">Top feature importances</h3>
          <div style={{width:'100%', height:400}} className="mt-4">
            <ResponsiveContainer>
              <BarChart layout="vertical" data={data} margin={{left:80}}>
                <XAxis type="number" />
                <YAxis type="category" dataKey="name" width={160} />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="mt-4 text-sm opacity-80">Positive values indicate features that increase predicted sales for this store.</p>
        </div>
      )}
    </div>
  )
}
