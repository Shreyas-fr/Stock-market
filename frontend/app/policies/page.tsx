'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPolicies = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API_URL}/policies?limit=20`);
        if (res.ok) {
          const data = await res.json();
          setPolicies(data);
        } else {
          throw new Error('API not available');
        }
      } catch (e) {
        // Fallback mock data
        setPolicies([
          {
            id: '1',
            title: 'India Reduces Lithium Battery Import Duty to 5%',
            summary: 'The Indian government has reduced import duty on lithium-ion batteries from 18% to 5% to boost EV adoption.',
            source_name: 'PIB India',
            policy_type: 'tariff_reduction',
            status: 'enacted',
            announced_date: '2024-02-01',
            affected_sectors: ['Electric Vehicles', 'Energy Storage'],
            impact_severity: 'high'
          },
          {
            id: '2',
            title: 'US CHIPS Act: $52B Semiconductor Manufacturing Subsidies',
            summary: 'Provides subsidies for domestic semiconductor manufacturing, aiming to reduce dependence on Asian chipmakers.',
            source_name: 'White House',
            policy_type: 'subsidy',
            status: 'enacted',
            announced_date: '2022-08-09',
            affected_sectors: ['Semiconductors', 'Technology'],
            impact_severity: 'critical'
          },
          {
            id: '3',
            title: 'China Restricts Gallium and Germanium Exports',
            summary: 'Export controls on materials critical for semiconductor manufacturing, affecting global chip supply chains.',
            source_name: 'Ministry of Commerce China',
            policy_type: 'export_restriction',
            status: 'enacted',
            announced_date: '2023-07-03',
            affected_sectors: ['Semiconductors', 'Defense'],
            impact_severity: 'high'
          },
        ]);
      } finally {
        setLoading(false);
      }
    };
    fetchPolicies();
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
          <span style={{ color: '#E8F0FF', fontWeight: 600 }}>Policy Intelligence</span>
        </div>
        <nav style={{ display: 'flex', gap: 16 }}>
          <Link href="/dashboard" style={{ color: '#8BA4C8', textDecoration: 'none', fontSize: 14 }}>Dashboard</Link>
          <Link href="/policies" style={{ color: '#4F8EF7', textDecoration: 'none', fontSize: 14, fontWeight: 600 }}>Policies</Link>
          <Link href="/risk" style={{ color: '#8BA4C8', textDecoration: 'none', fontSize: 14 }}>Global Risk</Link>
          <Link href="/alerts" style={{ color: '#8BA4C8', textDecoration: 'none', fontSize: 14 }}>Alerts</Link>
        </nav>
      </header>

      <div style={{ maxWidth: 1000, margin: '0 auto', padding: '32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 32 }}>
          <div>
            <h1 style={{ fontSize: 32, fontWeight: 900, color: '#E8F0FF', letterSpacing: '-0.02em', marginBottom: 8 }}>🏛️ Policy Intelligence Feed</h1>
            <p style={{ color: '#8BA4C8' }}>Live tracking of government regulations, subsidies, and export controls.</p>
          </div>
          <div className="input" style={{ width: 300, display: 'flex', gap: 8, alignItems: 'center' }}>
            <span>🔍</span>
            <input type="text" placeholder="Search policies..." style={{ background: 'transparent', border: 'none', color: '#FFF', outline: 'none', width: '100%' }} />
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {policies.map(policy => (
            <div key={policy.id} className="glass-card" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                  <span style={{ fontSize: 24 }}>{policy.policy_type === 'tariff_reduction' ? '📉' : policy.policy_type === 'subsidy' ? '💰' : '📋'}</span>
                  <h2 style={{ fontSize: 18, fontWeight: 700, color: '#E8F0FF' }}>{policy.title}</h2>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <span className="badge" style={{ background: 'rgba(79,142,247,0.1)', color: '#4F8EF7' }}>{policy.status}</span>
                  {policy.impact_severity === 'critical' && <span className="badge" style={{ background: 'rgba(244,63,94,0.1)', color: '#F43F5E' }}>CRITICAL</span>}
                  {policy.impact_severity === 'high' && <span className="badge" style={{ background: 'rgba(249,115,22,0.1)', color: '#F97316' }}>HIGH IMPACT</span>}
                </div>
              </div>
              <p style={{ color: '#8BA4C8', fontSize: 14, lineHeight: 1.6, marginBottom: 16 }}>
                {policy.summary}
              </p>
              <div style={{ display: 'flex', gap: 24, fontSize: 13, color: '#4A6080', borderTop: '1px solid rgba(99,160,255,0.08)', paddingTop: 16 }}>
                <div><strong>Source:</strong> <span style={{ color: '#C8D8F0' }}>{policy.source_name}</span></div>
                <div><strong>Announced:</strong> <span style={{ color: '#C8D8F0' }}>{policy.announced_date}</span></div>
                <div><strong>Sectors:</strong> <span style={{ color: '#C8D8F0' }}>{policy.affected_sectors.join(', ')}</span></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
