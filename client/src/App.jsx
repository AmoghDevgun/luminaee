import React, { useState } from 'react'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [view, setView] = useState(token ? 'dash' : 'login')

  const onLogin = (t) => {
    localStorage.setItem('token', t)
    setToken(t)
    setView('dash')
  }
  const logout = () => {
    localStorage.removeItem('token')
    setToken('')
    setView('login')
  }

  return (
    <div style={{ maxWidth: 720, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h2>Leads MERN</h2>
      {view === 'login' && (
        <>
          <Login onSuccess={onLogin} />
          <p>or</p>
          <button onClick={() => setView('register')}>Create account</button>
        </>
      )}
      {view === 'register' && (
        <>
          <Register onSuccess={() => setView('login')} />
          <p>
            <button onClick={() => setView('login')}>Back to login</button>
          </p>
        </>
      )}
      {view === 'dash' && <Dashboard token={token} onLogout={logout} />}
    </div>
  )
}


