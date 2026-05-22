'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function AlertsPage() {
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    // Simulate loading alerts data
    const timer = setTimeout(() => {
      setAlerts([
        { id: 1, type: 'critical', message: 'China restricts gallium exports — affects 47 semiconductor companies in your tracked network.', time: '2 hours ago', actionable: true },
        { id: 2, type: 'high', message: 'India PLI scheme expands: EV battery manufacturing incentives doubled. Impacts TSLA, TATAMOTORS.NS.', time: '5 hours ago', actionable: true },
        { id: 3, type: 'medium', message: 'TSMC Taiwan concentration risk elevated: approaching typhoon season.', time: '1 day ago', actionable: false },
        { id: 4, type: 'high', message: 'US CHIPS Act funding round 2 announced — $10B allocated for domestic fabs. Impacts INTC, AMAT.', time: '2 days ago', actionable: true },
        { id: 5, type: 'low', message: 'Quarterly earnings for AAPL exceed expectations, financial risk score decreased.', time: '3 days ago', actionable: false },
      ]);
      setLoading(false);
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 48, height: 48, borderRadius: '50%', border: '3px solid rgba(79,142,247,0.2)', borderTopColor: '#4F8EF7', animation: 'spin 0.8s linear infinite' }} />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', fontFamily: 'Inter, sans-serif' }}>
      <header style={{
        position: 'sticky', top: 0, zIndex: 50,
        background: 'rgba(6,11,23,0.9)', backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(99,160,255,0.1)',
        padding: '0 32px', height: 64,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Link href="/" style={{ color: '#8BA4C8', textDecoration: 'none', fontSize: 14 }}>← Home</Link>
          <span style={{ color: '#4A6080' }}>/</span>
          <span style={{ color: '#E8F0FF', fontWeight: 600 }}>System Alerts</span>
        </div>
        <nav style={{ display: 'flex', gap: 16 }}>
          <Link href="/dashboard" style={{ color: '#8BA4C8', textDecoration: 'none', fontSize: 14 }}>Dashboard</Link>
          <Link href="/policies" style={{ color: '#8BA4C8', textDecoration: 'none', fontSize: 14 }}>Policies</Link>
          <Link href="/risk" style={{ color: '#8BA4C8', textDecoration: 'none', fontSize: 14 }}>Global Risk</Link>
          <Link href="/alerts" style={{ color: '#4F8EF7', textDecoration: 'none', fontSize: 14, fontWeight: 600 }}>Alerts</Link>
        </nav>
      </header>

      <div style={{ maxWidth: 800, margin: '0 auto', padding: '32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 32 }}>
          <div>
            <h1 style={{ fontSize: 32, fontWeight: 900, color: '#E8F0FF', letterSpacing: '-0.02em', marginBottom: 8 }}>🔔 Live Alerts</h1>
            <p style={{ color: '#8BA4C8' }}>Real-time notifications for supply chain disruptions, policy changes, and risk thresholds.</p>
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
            <button className="btn btn-secondary" style={{ fontSize: 12, padding: '6px 12px' }}>Mark All Read</button>
            <button className="btn btn-secondary" style={{ fontSize: 12, padding: '6px 12px' }}>Filter: Critical</button>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {alerts.map(alert => (
            <div key={alert.id} className="glass-card" style={{ padding: '20px 24px', display: 'flex', gap: 16, borderLeft: `4px solid ${alert.type === 'critical' ? '#F43F5E' : alert.type === 'high' ? '#F97316' : alert.type === 'medium' ? '#F59E0B' : '#10B981'}` }}>
              <div style={{ paddingTop: 4 }}>
                <span style={{
                  display: 'inline-block', width: 12, height: 12, borderRadius: '50%',
                  background: alert.type === 'critical' ? '#F43F5E' : alert.type === 'high' ? '#F97316' : alert.type === 'medium' ? '#F59E0B' : '#10B981',
                  boxShadow: `0 0 10px ${alert.type === 'critical' ? 'rgba(244,63,94,0.5)' : alert.type === 'high' ? 'rgba(249,115,22,0.5)' : 'transparent'}`
                }} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', color: alert.type === 'critical' ? '#F43F5E' : alert.type === 'high' ? '#F97316' : alert.type === 'medium' ? '#F59E0B' : '#10B981', letterSpacing: '0.05em' }}>
                    {alert.type} PRIORITY
                  </span>
                  <span style={{ fontSize: 12, color: '#4A6080' }}>{alert.time}</span>
                </div>
                <p style={{ color: '#E8F0FF', fontSize: 14, lineHeight: 1.6, fontWeight: 500, marginBottom: alert.actionable ? 16 : 0 }}>
                  {alert.message}
                </p>
                {alert.actionable && (
                  <button className="btn btn-primary" style={{ padding: '6px 16px', fontSize: 12 }}>
                    Analyze Impact
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
