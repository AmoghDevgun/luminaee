import React, { useState } from 'react'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:4000'

export default function Dashboard({ token, onLogout }) {
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [leads, setLeads] = useState([])
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setLeads([])
    try {
      const res = await fetch(`${API}/api/leads`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ username })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Request failed')
      setLeads(data.leads_ranked || [])
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <form onSubmit={submit}>
          <input placeholder="instagram username" value={username} onChange={e => setUsername(e.target.value)} />
          <button type="submit" disabled={loading}>Fetch Leads</button>
        </form>
        <button onClick={onLogout}>Logout</button>
      </div>
      {loading && <p>Processing… this may take a few minutes.</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {leads.length > 0 && (
        <table border="1" cellPadding="6" style={{ marginTop: 12, borderCollapse: 'collapse', width: '100%' }}>
          <thead>
            <tr>
              <th>Username</th>
              <th>Full Name</th>
              <th>Followers</th>
              <th>Following</th>
              <th>Bio</th>
              <th>Lead Score</th>
              <th>Category</th>
            </tr>
          </thead>
          <tbody>
            {leads.map((r, i) => (
              <tr key={i}>
                <td>{r.username}</td>
                <td>{r.full_name}</td>
                <td>{r.followers}</td>
                <td>{r.following}</td>
                <td>{r.bio}</td>
                <td>{r.lead_score}</td>
                <td>{r.category}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}


