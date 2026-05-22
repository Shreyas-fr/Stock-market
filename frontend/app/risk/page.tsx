'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function GlobalRiskPage() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading risk data
    const timer = setTimeout(() => setLoading(false), 500);
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
          <span style={{ color: '#E8F0FF', fontWeight: 600 }}>Global Risk Assessment</span>
        </div>
        <nav style={{ display: 'flex', gap: 16 }}>
          <Link href="/dashboard" style={{ color: '#8BA4C8', textDecoration: 'none', fontSize: 14 }}>Dashboard</Link>
          <Link href="/policies" style={{ color: '#8BA4C8', textDecoration: 'none', fontSize: 14 }}>Policies</Link>
          <Link href="/risk" style={{ color: '#4F8EF7', textDecoration: 'none', fontSize: 14, fontWeight: 600 }}>Global Risk</Link>
          <Link href="/alerts" style={{ color: '#8BA4C8', textDecoration: 'none', fontSize: 14 }}>Alerts</Link>
        </nav>
      </header>

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '32px' }}>
        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 32, fontWeight: 900, color: '#E8F0FF', letterSpacing: '-0.02em', marginBottom: 8 }}>⚠️ Global Risk Assessment</h1>
          <p style={{ color: '#8BA4C8' }}>Aggregate supply chain, geopolitical, and financial risk across all monitored entities.</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
          <div className="glass-card" style={{ padding: '32px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#E8F0FF', marginBottom: 24 }}>Systemic Risk Score</h3>
            <svg width="200" height="200" viewBox="0 0 160 160">
              <circle cx="80" cy="80" r="60" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="16" />
              <circle cx="80" cy="80" r="60" fill="none" stroke="#F59E0B" strokeWidth="16" strokeLinecap="round" strokeDasharray={`${0.45 * 2 * Math.PI * 60} ${2 * Math.PI * 60}`} transform="rotate(-90 80 80)" />
              <text x="80" y="75" textAnchor="middle" fill="#F59E0B" fontSize="36" fontWeight="900" fontFamily="JetBrains Mono">45</text>
              <text x="80" y="100" textAnchor="middle" fill="#8BA4C8" fontSize="14" fontWeight="600">MODERATE</text>
            </svg>
          </div>

          <div className="glass-card" style={{ padding: '32px' }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#E8F0FF', marginBottom: 24 }}>Top Risk Factors</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {[
                { label: 'Taiwan Semiconductor Concentration', impact: 85, trend: 'stable' },
                { label: 'Lithium Supply Squeeze', impact: 72, trend: 'increasing' },
                { label: 'Export Control Policies (Semiconductors)', impact: 68, trend: 'increasing' },
                { label: 'Red Sea Shipping Delays', impact: 45, trend: 'decreasing' },
              ].map(risk => (
                <div key={risk.label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 14, color: '#C8D8F0', marginBottom: 6 }}>
                    <span>{risk.label}</span>
                    <span style={{ fontWeight: 700, color: risk.impact > 70 ? '#F43F5E' : risk.impact > 50 ? '#F97316' : '#F59E0B' }}>{risk.impact}/100</span>
                  </div>
                  <div style={{ height: 8, background: 'rgba(255,255,255,0.06)', borderRadius: 4 }}>
                    <div style={{ width: `${risk.impact}%`, height: '100%', borderRadius: 4, background: risk.impact > 70 ? '#F43F5E' : risk.impact > 50 ? '#F97316' : '#F59E0B' }} />
                  </div>
                  <div style={{ fontSize: 11, color: '#4A6080', marginTop: 4, textAlign: 'right' }}>
                    Trend: <span style={{ color: risk.trend === 'increasing' ? '#F43F5E' : risk.trend === 'decreasing' ? '#10B981' : '#8BA4C8' }}>{risk.trend.toUpperCase()}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
