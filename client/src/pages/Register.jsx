import React, { useState } from 'react'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:4000'

export default function Register({ onSuccess }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await fetch(`${API}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Registration failed')
      onSuccess()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <form onSubmit={submit}>
      <div>
        <input placeholder="email" value={email} onChange={e => setEmail(e.target.value)} />
      </div>
      <div>
        <input type="password" placeholder="password" value={password} onChange={e => setPassword(e.target.value)} />
      </div>
      <button type="submit">Create account</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </form>
  )
}


