'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function DashboardPage() {
  const [companies, setCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API_URL}/companies/search?q=&limit=20`);
        if (res.ok) {
          const data = await res.json();
          setCompanies(data);
        } else {
          throw new Error('API not available');
        }
      } catch (e) {
        // Fallback mock data
        setCompanies([
          { ticker: 'AAPL', name: 'Apple Inc.', sector: 'Technology', risk: 0.35, market_cap: 2900000000000 },
          { ticker: 'NVDA', name: 'NVIDIA Corp.', sector: 'Semiconductors', risk: 0.42, market_cap: 2500000000000 },
          { ticker: 'TSLA', name: 'Tesla Inc.', sector: 'Electric Vehicles', risk: 0.55, market_cap: 700000000000 },
          { ticker: 'TSM', name: 'TSMC', sector: 'Semiconductors', risk: 0.58, market_cap: 550000000000 },
          { ticker: 'WMT', name: 'Walmart Inc.', sector: 'Retail', risk: 0.22, market_cap: 600000000000 },
          { ticker: 'INTC', name: 'Intel Corporation', sector: 'Semiconductors', risk: 0.65, market_cap: 100000000000 },
          { ticker: 'AMAT', name: 'Applied Materials', sector: 'Semiconductors', risk: 0.28, market_cap: 150000000000 },
          { ticker: 'QCOM', name: 'Qualcomm Inc.', sector: 'Semiconductors', risk: 0.40, market_cap: 200000000000 },
          { ticker: 'TATAMOTORS.NS', name: 'Tata Motors', sector: 'Automotive', risk: 0.45, market_cap: 28000000000 },
          { ticker: 'LGES.KS', name: 'LG Energy Solution', sector: 'Battery', risk: 0.38, market_cap: 70000000000 },
        ]);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
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
          <span style={{ color: '#E8F0FF', fontWeight: 600 }}>Global Dashboard</span>
        </div>
        <nav style={{ display: 'flex', gap: 16 }}>
          <Link href="/dashboard" style={{ color: '#4F8EF7', textDecoration: 'none', fontSize: 14, fontWeight: 600 }}>Dashboard</Link>
          <Link href="/policies" style={{ color: '#8BA4C8', textDecoration: 'none', fontSize: 14 }}>Policies</Link>
          <Link href="/risk" style={{ color: '#8BA4C8', textDecoration: 'none', fontSize: 14 }}>Global Risk</Link>
          <Link href="/alerts" style={{ color: '#8BA4C8', textDecoration: 'none', fontSize: 14 }}>Alerts</Link>
        </nav>
      </header>

      <div style={{ maxWidth: 1400, margin: '0 auto', padding: '32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 32 }}>
          <div>
            <h1 style={{ fontSize: 32, fontWeight: 900, color: '#E8F0FF', letterSpacing: '-0.02em', marginBottom: 8 }}>Global Dashboard</h1>
            <p style={{ color: '#8BA4C8' }}>Overview of all tracked supply chains and aggregate risk metrics.</p>
          </div>
          <div style={{ display: 'flex', gap: 12 }}>
             <button className="btn btn-secondary">Download Report</button>
             <button className="btn btn-primary">+ Add Company</button>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32 }}>
          {[
            { label: 'Tracked Entities', value: '1,420', change: '+12 this week' },
            { label: 'Critical Alerts', value: '8', change: '-2 from yesterday', color: '#F43F5E' },
            { label: 'Avg Network Risk', value: '42.5', change: '+1.2% this month', color: '#F59E0B' },
            { label: 'Policies Tracked', value: '3,842', change: '+45 this week' },
          ].map((stat, i) => (
             <div key={i} className="glass-card" style={{ padding: '24px' }}>
               <div style={{ fontSize: 13, color: '#8BA4C8', fontWeight: 600, textTransform: 'uppercase', marginBottom: 8 }}>{stat.label}</div>
               <div style={{ fontSize: 28, fontWeight: 800, color: stat.color || '#E8F0FF', fontFamily: 'JetBrains Mono' }}>{stat.value}</div>
               <div style={{ fontSize: 12, color: '#4A6080', marginTop: 8 }}>{stat.change}</div>
             </div>
          ))}
        </div>

        <h2 style={{ fontSize: 20, fontWeight: 700, color: '#E8F0FF', marginBottom: 16 }}>Monitored Companies</h2>
        <div className="glass-card" style={{ overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Company Name</th>
                <th>Sector</th>
                <th>Market Cap</th>
                <th>Composite Risk</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {companies.map(c => (
                <tr key={c.ticker}>
                  <td><span style={{ fontWeight: 700, color: '#E8F0FF', fontFamily: 'JetBrains Mono' }}>{c.ticker}</span></td>
                  <td style={{ fontWeight: 500 }}>{c.name}</td>
                  <td>{c.sector}</td>
                  <td style={{ fontFamily: 'JetBrains Mono' }}>{c.market_cap ? `$${(c.market_cap / 1e9).toFixed(1)}B` : 'N/A'}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ flex: 1, height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 3, maxWidth: 100 }}>
                         <div style={{ 
                           width: `${(c.risk || 0) * 100}%`, height: '100%', borderRadius: 3,
                           background: c.risk >= 0.7 ? '#F43F5E' : c.risk >= 0.5 ? '#F97316' : c.risk >= 0.3 ? '#F59E0B' : '#10B981'
                         }} />
                      </div>
                      <span style={{ fontSize: 12, fontWeight: 600, fontFamily: 'JetBrains Mono' }}>
                        {Math.round((c.risk || 0) * 100)}
                      </span>
                    </div>
                  </td>
                  <td>
                    <Link href={`/company/${c.ticker}`} style={{ color: '#4F8EF7', textDecoration: 'none', fontWeight: 600, fontSize: 13 }}>
                      Analyze →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
