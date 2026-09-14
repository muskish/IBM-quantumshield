import { useState } from 'react'

const ROLES = [
  { value: 'viewer', label: 'Viewer (risk scores & summaries only)' },
  { value: 'analyst', label: 'Security Analyst (full technical details)' },
]

function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [role, setRole] = useState('viewer')
  const [error, setError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!username.trim()) {
      setError('Please enter a name to continue.')
      return
    }
    onLogin({ username: username.trim(), role })
  }

  return (
    <div className="login-screen">
      <div className="login-card">
        <h1>QuantumShield Banking</h1>
        <p className="login-subtitle">Sign in to view the readiness dashboard</p>

        <form onSubmit={handleSubmit}>
          <label>
            Name
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. Jordan"
            />
          </label>

          <label>
            Role
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              {ROLES.map((r) => (
                <option key={r.value} value={r.value}>{r.label}</option>
              ))}
            </select>
          </label>

          {error && <p className="login-error">{error}</p>}

          <button type="submit">Sign In</button>
        </form>

        <p className="login-note">
          Demo prototype: in production this would connect to the bank's
          real identity provider (e.g. SSO / Active Directory) rather than
          a self-declared role.
        </p>
      </div>
    </div>
  )
}

export default Login