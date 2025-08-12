import { useState } from 'react'
import { api } from '../api/client'

export default function Login() {
  const [email, setEmail] = useState('admin@example.com')
  const [password, setPassword] = useState('Admin123!')
  const [role, setRole] = useState<'tenant'|'admin'>('admin')
  const [message, setMessage] = useState('')

  async function register() {
    try {
      await api.post('/auth/register', { email, password, full_name: 'Admin', role })
      setMessage('Registered. You can now login.')
    } catch (e: any) {
      setMessage(e?.response?.data?.detail || 'Register failed')
    }
  }

  async function login(e: React.FormEvent) {
    e.preventDefault()
    const form = new URLSearchParams()
    form.set('username', email)
    form.set('password', password)
    try {
      const { data } = await api.post('/auth/login', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
      localStorage.setItem('token', data.access_token)
      setMessage('Logged in')
      window.location.href = role === 'admin' ? '/admin' : '/tenant'
    } catch (e: any) {
      setMessage(e?.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <div className="container">
      <h1>Sign in</h1>
      <form onSubmit={login} className="card">
        <label>Email<input value={email} onChange={e=>setEmail(e.target.value)} /></label>
        <label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} /></label>
        <label>Role
          <select value={role} onChange={e=>setRole(e.target.value as any)}>
            <option value="admin">Admin</option>
            <option value="tenant">Tenant</option>
          </select>
        </label>
        <div className="row">
          <button type="submit">Login</button>
          <button type="button" onClick={register}>Quick Register</button>
        </div>
      </form>
      {message && <p>{message}</p>}
    </div>
  )
}