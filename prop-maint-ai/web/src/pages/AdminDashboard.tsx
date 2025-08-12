import { useEffect, useState } from 'react'
import { api } from '../api/client'

type Metrics = { active_count: number, pending_count: number, predicted_count: number, avg_resolution_hours?: number|null }

type Property = { id: number, name: string, address?: string|null, year_built?: number|null }

type Prediction = { property_id: number, predicted_category: string, severity: string, priority: number, predicted_for_date: string }

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [properties, setProperties] = useState<Property[]>([])
  const [propName, setPropName] = useState('Block A')
  const [propYear, setPropYear] = useState<number | ''>('')
  const [preds, setPreds] = useState<Prediction[]>([])
  const [message, setMessage] = useState('')

  async function refresh() {
    try {
      const m = await api.get('/admin/metrics')
      setMetrics(m.data)
      const p = await api.get('/admin/properties')
      setProperties(p.data)
    } catch {}
  }

  useEffect(() => { refresh() }, [])

  async function createProperty() {
    try {
      await api.post('/admin/properties', { name: propName, year_built: propYear ? Number(propYear) : null })
      setMessage('Property created')
      setPropName('')
      setPropYear('')
      refresh()
    } catch (e: any) {
      setMessage(e?.response?.data?.detail || 'Failed to create property')
    }
  }

  async function suggest() {
    const { data } = await api.post('/predictions/suggest')
    setPreds(data)
    setMessage('Predictions generated')
  }

  async function applyPriorities() {
    await api.post('/predictions/apply-priorities')
    setMessage('Priorities applied to pending tasks')
  }

  async function assignWeekly() {
    await api.post('/admin/assign')
    setMessage('Weekly schedule assigned')
  }

  return (
    <div className="container">
      <h1>Admin Dashboard</h1>
      <section className="card">
        <h3>Metrics</h3>
        {metrics && <div>
          <div>Active: {metrics.active_count}</div>
          <div>Pending: {metrics.pending_count}</div>
          <div>Predicted: {metrics.predicted_count}</div>
        </div>}
        <div className="row">
          <button onClick={refresh}>Refresh</button>
          <button onClick={suggest}>Generate Predictions</button>
          <button onClick={applyPriorities}>Apply Priorities</button>
          <button onClick={assignWeekly}>Assign Weekly</button>
        </div>
        {message && <p>{message}</p>}
      </section>

      <section className="card">
        <h3>Properties</h3>
        <div className="row">
          <input placeholder="Name" value={propName} onChange={e=>setPropName(e.target.value)} />
          <input placeholder="Year Built" value={propYear} onChange={e=>setPropYear(e.target.value as any)} />
          <button onClick={createProperty}>Create</button>
        </div>
        <ul>
          {properties.map(p => <li key={p.id}>{p.name} {p.year_built ? `(${p.year_built})` : ''}</li>)}
        </ul>
      </section>

      <section className="card">
        <h3>Latest Predictions</h3>
        <div className="list">
          {preds.map(x => (
            <div className="item" key={`${x.property_id}-${x.predicted_for_date}`}>
              Property {x.property_id}: {x.predicted_category} — {x.severity} (priority {x.priority})
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}