import { useEffect, useState } from 'react'
import { api } from '../api/client'

type Property = { id: number, name: string }

type Request = {
  id: number
  property_id: number
  category: string
  urgency: string
  description?: string
  status: string
  priority?: number
  created_at: string
}

export default function TenantRequests() {
  const [properties, setProperties] = useState<Property[]>([])
  const [selectedProperty, setSelectedProperty] = useState<number | ''>('')
  const [category, setCategory] = useState('plumbing')
  const [urgency, setUrgency] = useState('medium')
  const [description, setDescription] = useState('')
  const [photo, setPhoto] = useState<File | null>(null)
  const [requests, setRequests] = useState<Request[]>([])
  const [message, setMessage] = useState('')

  useEffect(() => {
    (async () => {
      try {
        const props = await api.get('/tenant/properties')
        setProperties(props.data)
        const reqs = await api.get('/tenant/requests')
        setRequests(reqs.data)
      } catch {}
    })()
  }, [])

  async function submitRequest(e: React.FormEvent) {
    e.preventDefault()
    if (!selectedProperty) return
    const form = new FormData()
    form.set('property_id', String(selectedProperty))
    form.set('category', category)
    form.set('urgency', urgency)
    form.set('description', description)
    if (photo) form.set('photo', photo)
    try {
      await api.post('/tenant/requests', form, { headers: { 'Content-Type': 'multipart/form-data' } })
      const reqs = await api.get('/tenant/requests')
      setRequests(reqs.data)
      setMessage('Request submitted')
      setDescription('')
      setPhoto(null)
    } catch (e: any) {
      setMessage(e?.response?.data?.detail || 'Failed to submit')
    }
  }

  return (
    <div className="container">
      <h2>Submit Maintenance Request</h2>
      <form onSubmit={submitRequest} className="card">
        <label>Property
          <select value={selectedProperty} onChange={e=>setSelectedProperty(Number(e.target.value))}>
            <option value="">Select property</option>
            {properties.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </label>
        <label>Category<input value={category} onChange={e=>setCategory(e.target.value)} /></label>
        <label>Urgency
          <select value={urgency} onChange={e=>setUrgency(e.target.value)}>
            <option>low</option>
            <option>medium</option>
            <option>high</option>
          </select>
        </label>
        <label>Description<textarea value={description} onChange={e=>setDescription(e.target.value)} /></label>
        <label>Photo<input type="file" onChange={e=>setPhoto(e.target.files?.[0] ?? null)} /></label>
        <button type="submit">Submit</button>
        {message && <p>{message}</p>}
      </form>

      <h2>My Requests</h2>
      <div className="list">
        {requests.map(r => (
          <div className="item" key={r.id}>
            <div>
              <strong>#{r.id}</strong> {r.category} ({r.urgency}) — {r.status}
            </div>
            <div>Priority: {r.priority ?? '-'} | {new Date(r.created_at).toLocaleString()}</div>
          </div>
        ))}
      </div>
    </div>
  )
}