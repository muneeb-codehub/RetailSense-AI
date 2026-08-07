import React, {useState} from 'react'
import { postForecast } from '../api/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const families = ['GROCERY I','BEVERAGES','PRODUCE','CLEANING','DAIRY','BREAD/BAKERY','POULTRY','MEATS','PERSONAL CARE','DELI']

const initial = {
  store_nbr:1,family:families[0],onpromotion:0,year:2017,month:1,day:1,dayofweek:0,weekofyear:1,quarter:1,is_weekend:0,is_holiday:0,lag_7:0,lag_14:0,lag_28:0,rolling_7_mean:0,rolling_14_mean:0,rolling_7_std:0,dcoilwtico:67.5,transactions:1500,cluster:1
}

export default function Forecast(){
  const [form, setForm] = useState(initial)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [errors, setErrors] = useState({})

  const handleChange = (e)=>{
    const {name,value,type,checked} = e.target
    const val = type==='checkbox'? (checked?1:0) : (value === '' ? '' : Number(value))
    setForm(prev=> ({...prev, [name]: val}))
    setErrors(prev=> ({...prev, [name]: undefined}))
  }

  const validate = ()=>{
    const err = {}
    if(!Number.isInteger(form.store_nbr) || form.store_nbr <= 0) err.store_nbr = 'Store number required'
    if(!form.family) err.family = 'Family required'
    if(form.month <1 || form.month>12) err.month = 'Invalid month'
    if(form.day <1 || form.day>31) err.day = 'Invalid day'
    if(form.dayofweek <0 || form.dayofweek>6) err.dayofweek = 'Invalid dayofweek'
    if(form.weekofyear <1 || form.weekofyear>53) err.weekofyear = 'Invalid week number'
    if(form.quarter<1 || form.quarter>4) err.quarter='Invalid quarter'
    setErrors(err)
    return Object.keys(err).length===0
  }

  const submit = async ()=>{
    setError(null)
    if(!validate()) return
    setLoading(true)
    try{
      const payload = {...form}
      const res = await postForecast(payload)
      setResult(res.data)
    }catch(e){ setError(e?.response?.data?.detail || e.message) }
    setLoading(false)
  }

  return (
    <div className="space-y-6">
      <div className="card p-4 rounded">
        <h3 className="font-bold mb-4">Forecast Input</h3>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="text-sm">Store #</label>
            <input type="number" name="store_nbr" value={form.store_nbr} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
            {errors.store_nbr && <div className="text-red-400 text-xs">{errors.store_nbr}</div>}
          </div>
          <div>
            <label className="text-sm">Family</label>
            <select name="family" value={form.family} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40">
              {families.map(f=> <option key={f} value={f}>{f}</option>)}
            </select>
            {errors.family && <div className="text-red-400 text-xs">{errors.family}</div>}
          </div>
          <div>
            <label className="text-sm">On Promotion</label>
            <input type="number" name="onpromotion" value={form.onpromotion} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
          </div>

          <div>
            <label className="text-sm">Year</label>
            <input type="number" name="year" value={form.year} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
          </div>
          <div>
            <label className="text-sm">Month</label>
            <input type="number" name="month" value={form.month} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
            {errors.month && <div className="text-red-400 text-xs">{errors.month}</div>}
          </div>
          <div>
            <label className="text-sm">Day</label>
            <input type="number" name="day" value={form.day} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
            {errors.day && <div className="text-red-400 text-xs">{errors.day}</div>}
          </div>

          <div>
            <label className="text-sm">Day of Week</label>
            <input type="number" name="dayofweek" value={form.dayofweek} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
            {errors.dayofweek && <div className="text-red-400 text-xs">{errors.dayofweek}</div>}
          </div>
          <div>
            <label className="text-sm">Week of Year</label>
            <input type="number" name="weekofyear" value={form.weekofyear} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
            {errors.weekofyear && <div className="text-red-400 text-xs">{errors.weekofyear}</div>}
          </div>
          <div>
            <label className="text-sm">Quarter</label>
            <input type="number" name="quarter" value={form.quarter} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
            {errors.quarter && <div className="text-red-400 text-xs">{errors.quarter}</div>}
          </div>

          <div>
            <label className="text-sm">Is Weekend</label>
            <input type="checkbox" name="is_weekend" checked={form.is_weekend===1} onChange={handleChange} className="mt-2" />
          </div>
          <div>
            <label className="text-sm">Is Holiday</label>
            <input type="checkbox" name="is_holiday" checked={form.is_holiday===1} onChange={handleChange} className="mt-2" />
          </div>

          <div>
            <label className="text-sm">Lag 7</label>
            <input type="number" name="lag_7" value={form.lag_7} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
          </div>
          <div>
            <label className="text-sm">Lag 14</label>
            <input type="number" name="lag_14" value={form.lag_14} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
          </div>
          <div>
            <label className="text-sm">Lag 28</label>
            <input type="number" name="lag_28" value={form.lag_28} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
          </div>

          <div>
            <label className="text-sm">Rolling 7 Mean</label>
            <input type="number" name="rolling_7_mean" value={form.rolling_7_mean} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
          </div>
          <div>
            <label className="text-sm">Rolling 14 Mean</label>
            <input type="number" name="rolling_14_mean" value={form.rolling_14_mean} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
          </div>
          <div>
            <label className="text-sm">Rolling 7 Std</label>
            <input type="number" name="rolling_7_std" value={form.rolling_7_std} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
          </div>

          <div>
            <label className="text-sm">Oil Price</label>
            <input type="number" name="dcoilwtico" value={form.dcoilwtico} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
          </div>
          <div>
            <label className="text-sm">Transactions</label>
            <input type="number" name="transactions" value={form.transactions} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
          </div>
          <div>
            <label className="text-sm">Cluster</label>
            <input type="number" name="cluster" value={form.cluster} onChange={handleChange} className="w-full mt-1 p-2 rounded bg-page/40" />
          </div>
        </div>

        <div className="mt-4 flex items-center gap-3">
          <button onClick={submit} className="px-4 py-2 bg-accent rounded">{loading? 'Running...':'Predict'}</button>
          {error && <div className="text-red-500">{error}</div>}
        </div>
      </div>

      {result && (
        <div className="card p-4 rounded">
          <h3 className="font-bold">Prediction</h3>
          <div className="mt-2 grid grid-cols-4 gap-4">
            <div className="p-3 card rounded">Predicted: <div className="text-xl font-bold">{result.prediction}</div></div>
            <div className="p-3 card rounded">CI Lower: <div className="text-xl">{result.ci_lower}</div></div>
            <div className="p-3 card rounded">CI Upper: <div className="text-xl">{result.ci_upper}</div></div>
            <div className="p-3 card rounded">Model: <div className="text-xl">{result.model_used}</div></div>
          </div>

          <div style={{width:'100%', height:200}} className="mt-4">
            <ResponsiveContainer>
              <BarChart data={[{name:'Prediction', val: result.prediction}, {name:'CI Lower', val: result.ci_lower}, {name:'CI Upper', val: result.ci_upper}] }>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="val" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}
