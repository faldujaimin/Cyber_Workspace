import { useEffect, useMemo, useState } from 'react'
import './App.css'

const defaultData = {
  aircraft: {
    registration: 'N-204SKY',
    type: 'Boeing 737-800 (simulated)',
    flight_status: 'Operational simulation',
    phase: 'cruise',
    identification: 'SKYGUARD AI - Research Flight',
  },
  telemetry: {
    altitude: 30000,
    airspeed: 245,
    ground_speed: 250,
    vertical_speed: 0,
    heading: 140,
    pitch: 2,
    roll: -1,
    fuel: 78,
    outside_temp: -20,
    latitude: 40.7128,
    longitude: -74.006,
    destination: 'KJFK',
    departure: 'KATL',
    route_progress: 36,
    distance_nm: 780,
    timestamp: new Date().toISOString(),
  },
  weather: {
    condition: 'Clear',
    wind_speed: 18,
    wind_direction: 145,
    visibility: 10,
    turbulence: 'Low',
    temperature: -18,
    source: 'Simulated weather source',
    timestamp: new Date().toISOString(),
  },
  alerts: [
    {
      category: 'monitoring',
      severity: 'info',
      message: 'Simulated flight monitoring active.',
      explanation: 'All flight information is simulated and for research use only.',
      recommendation: 'Review current operating guidance and flight conditions.',
      timestamp: new Date().toISOString(),
    },
  ],
  co_pilot: {
    assistant_state: 'Online',
    conversation_history: [{ role: 'assistant', text: 'Awaiting flight data...' }],
  },
}

const severityClasses = {
  info: 'info',
  caution: 'caution',
  warning: 'warning',
  critical: 'critical',
}

function MetricCard({ label, value, unit, helper }) {
  return (
    <div className="metric-card">
      <p className="metric-label">{label}</p>
      <div className="metric-line">
        <span className="metric-value">{value}</span>
        {unit ? <span className="metric-unit">{unit}</span> : null}
      </div>
      <small>{helper}</small>
    </div>
  )
}

function App() {
  const [flightData, setFlightData] = useState(defaultData)
  const [connectionState, setConnectionState] = useState('connecting')
  const [isLoading, setIsLoading] = useState(true)

  const telemetry = flightData.telemetry
  const weather = flightData.weather
  const alerts = flightData.alerts || []
  const aircraft = flightData.aircraft
  const assistantMessage = useMemo(
    () =>
      flightData.co_pilot?.conversation_history?.[flightData.co_pilot.conversation_history.length - 1]?.text ||
      'Monitoring systems are online and in research mode.',
    [flightData],
  )

  useEffect(() => {
    let cancelled = false

    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/flight-status')
        if (!response.ok) {
          throw new Error('Failed to load flight status')
        }
        const payload = await response.json()
        if (!cancelled) {
          setFlightData(payload)
          setIsLoading(false)
        }
      } catch (error) {
        console.error(error)
      }
    }

    fetchStatus()
    const intervalId = window.setInterval(fetchStatus, 5000)

    return () => {
      cancelled = true
      window.clearInterval(intervalId)
    }
  }, [])

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws/telemetry')
    socket.onopen = () => setConnectionState('live')
    socket.onclose = () => setConnectionState('offline')
    socket.onerror = () => setConnectionState('offline')
    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data)
        setFlightData(payload)
        setIsLoading(false)
      } catch (error) {
        console.error('Could not parse telemetry payload', error)
      }
    }

    return () => socket.close()
  }, [])

  const actionSimulation = async (action) => {
    try {
      const response = await fetch(`/api/simulation/${action}`, { method: 'POST' })
      if (!response.ok) {
        throw new Error(`Simulation action ${action} failed`)
      }
      const payload = await response.json()
      if (payload.simulation && payload.simulation.active !== undefined) {
        const refreshed = await fetch('/api/flight-status')
        const data = await refreshed.json()
        setFlightData(data)
      }
    } catch (error) {
      console.error(error)
    }
  }

  const headingDisplay = `${Math.round(telemetry.heading)}°`
  const phaseLabel = aircraft.phase || 'cruise'

  return (
    <div className="app-shell">
      <header className="topbar panel">
        <div>
          <p className="eyebrow">AUTONOMOUS FLIGHT RESEARCH</p>
          <h1>SKYGUARD AI</h1>
        </div>
        <div className="topbar-meta">
          <div className={`status-pill ${connectionState}`}>
            {connectionState === 'live' ? 'LIVE FEED' : connectionState === 'connecting' ? 'CONNECTING' : 'OFFLINE'}
          </div>
          <span className="sim-badge">SIMULATED DATA</span>
        </div>
      </header>

      <section className="overview-grid">
        <div className="panel main-panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">AIRCRAFT</p>
              <h2>{aircraft.identification}</h2>
            </div>
            <div className="phase-chip">{phaseLabel.toUpperCase()}</div>
          </div>

          <div className="telemetry-grid">
            <MetricCard label="Altitude" value={Math.round(telemetry.altitude).toLocaleString()} unit="ft" helper="pressure altitude" />
            <MetricCard label="Airspeed" value={Math.round(telemetry.airspeed)} unit="kt" helper="indicated" />
            <MetricCard label="Heading" value={headingDisplay} unit="" helper="magnetic" />
            <MetricCard label="Fuel" value={Math.round(telemetry.fuel)} unit="%" helper="remaining reserve" />
          </div>

          <div className="flight-ribbon">
            <div className="route-line">
              <span className="route-point route-point-start">{telemetry.departure}</span>
              <span className="route-progress" style={{ width: `${Math.min(100, telemetry.route_progress || 0)}%` }}></span>
              <span className="route-point route-point-end">{telemetry.destination}</span>
            </div>
            <div className="route-caption">
              <span>{telemetry.route_progress || 0}% route complete</span>
              <span>{telemetry.distance_nm || 0} NM remaining</span>
            </div>
          </div>

          <div className="gauge-grid">
            <div className="gauge-panel">
              <p>Pitch</p>
              <div className="gauge-track">
                <div className="gauge-fill pitch" style={{ width: `${Math.min(100, Math.abs(telemetry.pitch) * 12)}%` }}></div>
              </div>
              <strong>{telemetry.pitch.toFixed(2)}°</strong>
            </div>
            <div className="gauge-panel">
              <p>Roll</p>
              <div className="gauge-track">
                <div className="gauge-fill roll" style={{ width: `${Math.min(100, Math.abs(telemetry.roll) * 12)}%` }}></div>
              </div>
              <strong>{telemetry.roll.toFixed(2)}°</strong>
            </div>
            <div className="gauge-panel">
              <p>Vertical speed</p>
              <div className="gauge-track">
                <div className="gauge-fill vertical" style={{ width: `${Math.min(100, Math.abs(telemetry.vertical_speed) / 12)}%` }}></div>
              </div>
              <strong>{Math.round(telemetry.vertical_speed)} fpm</strong>
            </div>
          </div>
        </div>

        <aside className="panel side-panel">
          <div className="panel-header compact">
            <div>
              <p className="eyebrow">SYSTEM STATUS</p>
              <h2>{aircraft.flight_status}</h2>
            </div>
          </div>

          <div className="stat-stack">
            <div className="stat-row">
              <span>Registration</span>
              <strong>{aircraft.registration}</strong>
            </div>
            <div className="stat-row">
              <span>Type</span>
              <strong>{aircraft.type}</strong>
            </div>
            <div className="stat-row">
              <span>Flight phase</span>
              <strong>{phaseLabel}</strong>
            </div>
            <div className="stat-row">
              <span>Wind</span>
              <strong>{weather.wind_speed} kt / {weather.wind_direction}°</strong>
            </div>
            <div className="stat-row">
              <span>Visibility</span>
              <strong>{weather.visibility} mi</strong>
            </div>
            <div className="stat-row">
              <span>Outside temp</span>
              <strong>{weather.temperature}°C</strong>
            </div>
          </div>

          <div className="control-panel">
            <button type="button" onClick={() => actionSimulation('start')}>Start</button>
            <button type="button" onClick={() => actionSimulation('pause')}>Pause</button>
            <button type="button" onClick={() => actionSimulation('resume')}>Resume</button>
            <button type="button" className="secondary" onClick={() => actionSimulation('reset')}>Reset</button>
            <button type="button" onClick={() => actionSimulation('speedup')}>Speed +</button>
            <button type="button" onClick={() => actionSimulation('slowdown')}>Speed -</button>
          </div>
        </aside>
      </section>

      <section className="lower-grid">
        <div className="panel weather-panel">
          <div className="panel-header compact">
            <div>
              <p className="eyebrow">WEATHER</p>
              <h2>{weather.condition}</h2>
            </div>
            <span className="muted">{weather.turbulence} turbulence</span>
          </div>
          <div className="weather-grid">
            <div>
              <p>Wind</p>
              <strong>{weather.wind_speed} kt</strong>
            </div>
            <div>
              <p>Direction</p>
              <strong>{weather.wind_direction}°</strong>
            </div>
            <div>
              <p>Visibility</p>
              <strong>{weather.visibility} mi</strong>
            </div>
            <div>
              <p>Temp</p>
              <strong>{weather.temperature}°C</strong>
            </div>
          </div>
        </div>

        <div className="panel alerts-panel">
          <div className="panel-header compact">
            <div>
              <p className="eyebrow">ALERTS</p>
              <h2>{alerts.length} active items</h2>
            </div>
          </div>
          <div className="alert-list">
            {alerts.map((alert, index) => (
              <div key={`${alert.message}-${index}`} className={`alert-item ${severityClasses[alert.severity] || 'info'}`}>
                <span className="alert-severity">{alert.severity.toUpperCase()}</span>
                <div>
                  <strong>{alert.message}</strong>
                  <p>{alert.explanation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="panel co-pilot-panel">
          <div className="panel-header compact">
            <div>
              <p className="eyebrow">AI CO-PILOT</p>
              <h2>{flightData.co_pilot?.assistant_state || 'Online'}</h2>
            </div>
          </div>
          <div className="assistant-box">
            <p className="assistant-label">Latest guidance</p>
            <p>{assistantMessage}</p>
          </div>
          <div className="assistant-footer">
            <span>{telemetry.timestamp ? new Date(telemetry.timestamp).toLocaleTimeString() : 'Realtime'}</span>
            <span>Research-only simulation</span>
          </div>
        </div>
      </section>

      <section className="panel footer-panel">
        <div className="panel-header compact">
          <div>
            <p className="eyebrow">NAVIGATION</p>
            <h2>Position & route</h2>
          </div>
        </div>
        <div className="nav-grid">
          <div className="mini-map">
            <div className="map-ring">
              <div className="map-dot" style={{ transform: `translate(${Math.sin(Math.PI / 180 * telemetry.heading) * 30}px, ${Math.cos(Math.PI / 180 * telemetry.heading) * 16}px)` }} />
            </div>
          </div>
          <div className="nav-details">
            <div className="nav-row"><span>Departure</span><strong>{telemetry.departure}</strong></div>
            <div className="nav-row"><span>Destination</span><strong>{telemetry.destination}</strong></div>
            <div className="nav-row"><span>Latitude</span><strong>{telemetry.latitude}</strong></div>
            <div className="nav-row"><span>Longitude</span><strong>{telemetry.longitude}</strong></div>
          </div>
        </div>
      </section>

      {isLoading ? <div className="loading-indicator">Loading telemetry…</div> : null}
    </div>
  )
}

export default App
