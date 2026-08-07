import React, {useState} from 'react'
import { postSegment } from '../api/api'
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts'

export default function Segmentation(){
  const [form, setForm] = useState({total_sales:0,avg_sales:0,std_sales:0,total_promo:0,avg_oil:0,avg_trans:0,holiday_count:0,unique_families:0})
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const handle = (e)=>{ const {name,value} = e.target; setForm(prev=>({...prev,[name]: Number(value)})) }
  const submit = async ()=>{ setLoading(true); try{ const r = await postSegment(form); setResult(r.data);}catch(e){alert(e.message)} setLoading(false)}

  const radarData = Object.keys(form).map(k=> ({feature:k, value: form[k]}))

  return (
    <div className="space-y-6">
      <div className="card p-4 grid grid-cols-4 gap-3">
        {Object.keys(form).map(k=> (
          <div key={k}><label className="text-xs">{k}</label>
            <input name={k} value={form[k]} onChange={handle} className="w-full mt-1 p-2 rounded bg-page/40" /></div>
        ))}
        <div className="col-span-4 mt-2"><button onClick={submit} className="px-4 py-2 bg-accent rounded">{loading? 'Running...':'Segment'}</button></div>
      </div>

      {result && (
        <div className="card p-4 rounded">
          <div className="flex gap-4">
            <div className="p-3 card rounded">KMeans Cluster: <span className="font-bold">{result.kmeans_cluster}</span></div>
            <div className="p-3 card rounded">GMM Cluster: <span className="font-bold">{result.gmm_cluster}</span></div>
            <div className="p-3 card rounded">GMM Confidence: <span className="font-bold">{(result.gmm_confidence*100).toFixed(1)}%</span></div>
          </div>
          <div style={{width:400,height:300}} className="mt-4">
            <ResponsiveContainer>
              <RadarChart data={radarData} outerRadius={100}>
                <PolarGrid />
                <PolarAngleAxis dataKey="feature" />
                <PolarRadiusAxis />
                <Radar name="input" dataKey="value" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}
