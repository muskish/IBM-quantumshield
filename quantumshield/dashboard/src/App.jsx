import { useState, useEffect } from 'react'
import cbomData from './cbom_report.json'
import DependencyGraph from './DependencyGraph'
import Login from './Login'
import './App.css'

const RISK_COLORS = {
  Critical: '#dc2626',
  High: '#ea580c',
  Medium: '#ca8a04',
  Low: '#16a34a',
}

function RiskBadge({ level }) {
  const color = RISK_COLORS[level] || '#6b7280'
  return (
    <span
      style={{
        backgroundColor: color,
        color: 'white',
        padding: '4px 12px',
        borderRadius: '999px',
        fontSize: '0.85rem',
        fontWeight: 600,
      }}
    >
      {level}
    </span>
  )
}

function ServiceCard({ serviceName, serviceData, isExpanded, onToggle, isAnalyst }) {
  const risk = serviceData.risk_assessment || {}
  const context = serviceData.business_context || {}

  return (
    <div className="service-card">
      <div className="service-card-header" onClick={onToggle}>
        <div>
          <h3>{serviceName}</h3>
          <p className="service-description">{context.description}</p>
        </div>
        <div className="service-card-header-right">
          <RiskBadge level={risk.risk_level} />
          <span className="risk-score">{risk.risk_score}</span>
          <span className="expand-arrow">{isExpanded ? '▲' : '▼'}</span>
        </div>
      </div>

      {isExpanded && (
        <div className="service-card-body">
          <div className="context-grid">
            <div><strong>Public exposure:</strong> {String(context.public_exposure)}</div>
            <div><strong>Data sensitivity:</strong> {context.data_sensitivity}</div>
            <div><strong>Retention:</strong> {context.retention_period_years} years</div>
            <div><strong>Business criticality:</strong> {context.business_criticality}</div>
          </div>

          {isAnalyst && context.vendor_dependencies && context.vendor_dependencies.length > 0 && (
            <>
              <h4>Vendor dependencies (Analyst-only):</h4>
              <ul className="findings-list">
                {context.vendor_dependencies.map((v, i) => (
                  v.name && v.name !== 'none' && (
                    <li key={i}>{v.name} — PQC roadmap confirmed: {String(v.quantum_safe_roadmap_confirmed)}</li>
                  )
                ))}
              </ul>
            </>
          )}

          <h4>Why this score:</h4>
          <ul className="explanation-list">
            {(risk.explanation || []).map((line, i) => (
              <li key={i}>{line}</li>
            ))}
          </ul>

          <h4>Source code findings:</h4>
          <ul className="findings-list">
            {(serviceData.source_code_findings || []).map((f, i) => (
              <li key={i}>
                {f.algorithm} — <span className={`tag tag-${f.risk_category}`}>{f.risk_category}</span> (x{f.occurrences})
              </li>
            ))}
          </ul>

          {isAnalyst && (serviceData.certificate_findings || []).length > 0 && (
            <>
              <h4>Certificate findings (Analyst-only):</h4>
              <ul className="findings-list">
                {serviceData.certificate_findings.map((c, i) => (
                  <li key={i}>
                    {c.algorithm} ({c.key_size} bits) — expires {c.expiry_date}
                  </li>
                ))}
              </ul>
            </>
          )}
          {!isAnalyst && (serviceData.certificate_findings || []).length > 0 && (
            <p style={{ color: '#64748b', fontSize: '0.85rem' }}>
              🔒 Certificate details hidden — Security Analyst role required.
            </p>
          )}
        </div>
      )}
    </div>
  )
}

function App() {
  const [expandedService, setExpandedService] = useState(null)
  const [currentUser, setCurrentUser] = useState(null)
  const [auditLog, setAuditLog] = useState([])

  const services = cbomData.services || {}
  const roadmap = cbomData.migration_roadmap || {}

  const handleLogin = (user) => {
    setCurrentUser(user)
    const entry = {
      username: user.username,
      role: user.role,
      timestamp: new Date().toLocaleString(),
    }
    setAuditLog((prev) => [entry, ...prev])
  }

  const isAnalyst = currentUser?.role === 'analyst'

  // Build a priority-ranked list (highest risk score first)
  const rankedServices = Object.entries(services).sort((a, b) => {
    const scoreA = a[1].risk_assessment?.risk_score || 0
    const scoreB = b[1].risk_assessment?.risk_score || 0
    return scoreB - scoreA
  })

  const toggleService = (name) => {
    setExpandedService(expandedService === name ? null : name)
  }

    if (!currentUser) {
    return <Login onLogin={handleLogin} />
  }

  return (
    <div className="dashboard">
      <div className="session-bar">
        Signed in as <strong>{currentUser.username}</strong> ({currentUser.role === 'analyst' ? 'Security Analyst' : 'Viewer'})
        <button className="signout-btn" onClick={() => setCurrentUser(null)}>Sign out</button>
      </div>
      <header className="dashboard-header">
        <h1>QuantumShield Banking</h1>
        <p>Quantum-Safe Readiness Scanner Dashboard</p>
        <p className="report-timestamp">
          Report generated: {new Date(cbomData.report_generated_at).toLocaleString()}
        </p>
      </header>

      {isAnalyst && (
        <section className="priority-ranking">
          <h2>Access Audit Log (Analyst-only)</h2>
          <ul className="explanation-list">
            {auditLog.map((entry, i) => (
              <li key={i}>{entry.timestamp} — {entry.username} signed in as {entry.role}</li>
            ))}
          </ul>
        </section>
      )}

      <section className="priority-ranking">
        <h2>Priority Ranking</h2>
        <ol>
          {rankedServices.map(([name, data]) => (
            <li key={name}>
              <strong>{name}</strong> — <RiskBadge level={data.risk_assessment?.risk_level} />
              {' '}({data.risk_assessment?.risk_score})
            </li>
          ))}
        </ol>
      </section>

      <section className="priority-ranking">
        <h2>Dependency & Risk Graph</h2>
        <DependencyGraph />
      </section>

      <section className="priority-ranking">
        <h2>Migration Roadmap</h2>
        {[1, 2, 3, 4].map((phaseNum) => {
          const phaseItems = roadmap[phaseNum] || []
          const phaseLabels = {
            1: 'Phase 1 — Critical (fix immediately)',
            2: 'Phase 2 — High (fix soon)',
            3: 'Phase 3 — Medium (plan for)',
            4: 'Phase 4 — Low (monitor)',
          }
          return (
            <div key={phaseNum} style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ color: '#f8fafc', fontSize: '1.05rem' }}>{phaseLabels[phaseNum]}</h3>
              {phaseItems.length === 0 ? (
                <p style={{ color: '#64748b', fontSize: '0.9rem' }}>No services in this phase.</p>
              ) : (
                phaseItems.map((item) => (
                  <div key={item.service_name} style={{ marginBottom: '1rem', paddingLeft: '0.5rem' }}>
                    <strong>{item.service_name}</strong>
                    <span style={{ color: '#94a3b8' }}> — score {item.risk_score}</span>
                    <ul className="explanation-list">
                      {item.actions.map((action, i) => (
                        <li key={i}>{action}</li>
                      ))}
                    </ul>
                  </div>
                ))
              )}
            </div>
          )
        })}
      </section>

      <section className="service-list">
        <h2>All Services</h2>
        {rankedServices.map(([name, data]) => (
          <ServiceCard
            key={name}
            serviceName={name}
            serviceData={data}
            isExpanded={expandedService === name}
            onToggle={() => toggleService(name)}
            isAnalyst={isAnalyst}
          />
        ))}
      </section>
    </div>
  )
}

export default App