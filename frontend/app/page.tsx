'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

const FEATURED_COMPANIES = [
  { ticker: 'AAPL', name: 'Apple Inc.', sector: 'Technology', risk: 0.35, change: +2.1 },
  { ticker: 'NVDA', name: 'NVIDIA Corp.', sector: 'Semiconductors', risk: 0.42, change: +5.3 },
  { ticker: 'TSLA', name: 'Tesla Inc.', sector: 'Electric Vehicles', risk: 0.55, change: -1.8 },
  { ticker: 'TSM', name: 'TSMC', sector: 'Semiconductors', risk: 0.58, change: +1.2 },
  { ticker: 'RELIANCE.NS', name: 'Reliance Industries', sector: 'Energy', risk: 0.38, change: +0.9 },
  { ticker: 'TCS.NS', name: 'Tata Consultancy Services', sector: 'Technology', risk: 0.28, change: +1.5 },
];

const RECENT_ALERTS = [
  { type: 'critical', text: 'China restricts gallium exports — affects 47 semiconductor companies', time: '2h ago' },
  { type: 'high', text: 'India PLI scheme expands: EV battery manufacturing incentives doubled', time: '5h ago' },
  { type: 'medium', text: 'TSMC Taiwan concentration risk elevated: typhoon season risk', time: '1d ago' },
  { type: 'high', text: 'US CHIPS Act funding round 2 announced — $10B for domestic fabs', time: '2d ago' },
];

const STATS = [
  { label: 'Companies Tracked', value: '50+', icon: '🏢', color: '#4F8EF7' },
  { label: 'Supply Relationships', value: '500+', icon: '🔗', color: '#8B5CF6' },
  { label: 'Policies Monitored', value: '1,200+', icon: '📋', color: '#22D3EE' },
  { label: 'Risk Alerts Today', value: '12', icon: '⚠️', color: '#F59E0B' },
];

function RiskBadge({ score }: { score: number }) {
  const level = score >= 0.7 ? 'critical' : score >= 0.5 ? 'high' : score >= 0.3 ? 'medium' : 'low';
  const colors = {
    critical: { bg: 'rgba(244,63,94,0.12)', text: '#F43F5E', border: 'rgba(244,63,94,0.3)' },
    high: { bg: 'rgba(249,115,22,0.12)', text: '#F97316', border: 'rgba(249,115,22,0.3)' },
    medium: { bg: 'rgba(245,158,11,0.12)', text: '#F59E0B', border: 'rgba(245,158,11,0.3)' },
    low: { bg: 'rgba(16,185,129,0.12)', text: '#10B981', border: 'rgba(16,185,129,0.3)' },
  };
  const c = colors[level];
  return (
    <span style={{ background: c.bg, color: c.text, border: `1px solid ${c.border}`, padding: '2px 10px', borderRadius: 999, fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
      {level}
    </span>
  );
}

function AlertBadge({ type }: { type: string }) {
  const colors = {
    critical: '#F43F5E',
    high: '#F97316',
    medium: '#F59E0B',
    low: '#10B981',
  };
  return (
    <span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: '50%', background: colors[type as keyof typeof colors] || '#8BA4C8', flexShrink: 0 }} />
  );
}

export default function HomePage() {
  const [search, setSearch] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const router = useRouter();
  const searchRef = useRef<HTMLDivElement>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setShowResults(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (search.length < 2) {
      setSearchResults([]);
      setShowResults(false);
      return;
    }
    const timer = setTimeout(async () => {
      setSearching(true);
      try {
        const res = await fetch(`${API_URL}/companies/search?q=${encodeURIComponent(search)}&limit=8`);
        if (res.ok) {
          const data = await res.json();
          setSearchResults(data);
          setShowResults(true);
        }
      } catch {
        // API not available — show mock results
        setSearchResults(FEATURED_COMPANIES.filter(c =>
          c.name.toLowerCase().includes(search.toLowerCase()) ||
          c.ticker.toLowerCase().includes(search.toLowerCase())
        ));
        setShowResults(true);
      } finally {
        setSearching(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const handleSelect = (ticker: string) => {
    router.push(`/company/${ticker}`);
    setShowResults(false);
    setSearch('');
  };

  return (
    <div style={{ minHeight: '100vh', fontFamily: 'Inter, sans-serif' }}>
      {/* Header */}
      <header style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
        background: 'rgba(6, 11, 23, 0.85)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(99, 160, 255, 0.1)',
        padding: '0 32px',
        height: 64,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'linear-gradient(135deg, #4F8EF7, #8B5CF6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 18,
          }}>⬡</div>
          <span style={{ fontWeight: 800, fontSize: 18, letterSpacing: '-0.02em' }}>
            <span className="gradient-text">SCI</span>
            <span style={{ color: 'rgba(232,240,255,0.6)', fontWeight: 400 }}> Platform</span>
          </span>
        </div>
        <nav style={{ display: 'flex', gap: 8 }}>
          {['Dashboard', 'Supply Chain', 'Policies', 'Risk'].map(item => (
            <Link key={item} href={`/${item.toLowerCase().replace(' ', '-')}`}
              style={{
                padding: '6px 16px', borderRadius: 8,
                color: 'rgba(139, 164, 200, 1)',
                fontSize: 14, fontWeight: 500,
                textDecoration: 'none',
                transition: 'all 150ms',
              }}
              onMouseEnter={e => (e.currentTarget.style.color = '#fff')}
              onMouseLeave={e => (e.currentTarget.style.color = 'rgba(139,164,200,1)')}
            >{item}</Link>
          ))}
        </nav>
        <Link href="/dashboard" style={{
          padding: '8px 20px', borderRadius: 10,
          background: 'linear-gradient(135deg, #4F8EF7, #8B5CF6)',
          color: 'white', fontWeight: 600, fontSize: 14,
          textDecoration: 'none',
        }}>Get Started →</Link>
      </header>

      {/* Hero Section */}
      <section style={{
        paddingTop: 160, paddingBottom: 80,
        textAlign: 'center', padding: '160px 24px 80px',
        position: 'relative', overflow: 'hidden',
      }}>
        {/* Background glow orbs */}
        <div style={{
          position: 'absolute', top: '20%', left: '20%',
          width: 600, height: 600, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(79,142,247,0.06) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />
        <div style={{
          position: 'absolute', top: '30%', right: '15%',
          width: 400, height: 400, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(139,92,246,0.06) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        {/* Badge */}
        <div style={{ marginBottom: 24, display: 'inline-flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            padding: '6px 16px', borderRadius: 999,
            background: 'rgba(79, 142, 247, 0.1)',
            border: '1px solid rgba(79, 142, 247, 0.2)',
          }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#10B981', display: 'inline-block' }} className="pulse-glow" />
            <span style={{ color: '#4F8EF7', fontSize: 13, fontWeight: 600 }}>Live Intelligence Platform</span>
          </div>
        </div>

        {/* Headline */}
        <h1 style={{
          fontSize: 'clamp(40px, 5vw, 72px)',
          fontWeight: 900,
          lineHeight: 1.1,
          letterSpacing: '-0.03em',
          maxWidth: 900, margin: '0 auto 24px',
          color: '#E8F0FF',
        }}>
          Supply Chain Intelligence
          <br />
          <span className="gradient-text">Powered by AI</span>
        </h1>

        <p style={{
          fontSize: 20, color: 'rgba(139, 164, 200, 0.9)',
          maxWidth: 640, margin: '0 auto 48px',
          lineHeight: 1.6, fontWeight: 400,
        }}>
          Monitor global supply chains, track government policies,
          analyze financial risk, and predict market impact with AI.
        </p>

        {/* Search Bar */}
        <div ref={searchRef} style={{ maxWidth: 640, margin: '0 auto', position: 'relative' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 12,
            background: 'rgba(13, 21, 40, 0.9)',
            border: '1px solid rgba(99, 160, 255, 0.2)',
            borderRadius: 16, padding: '4px 4px 4px 20px',
            boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
          }}>
            <span style={{ fontSize: 18 }}>🔍</span>
            <input
              type="text"
              placeholder="Search company, ticker, or sector..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter' && searchResults.length > 0) {
                  handleSelect(searchResults[0].ticker);
                }
              }}
              style={{
                flex: 1, background: 'transparent', border: 'none',
                outline: 'none', color: '#E8F0FF', fontSize: 16,
                padding: '10px 0',
              }}
            />
            {searching && (
              <div style={{ width: 20, height: 20, borderRadius: '50%', border: '2px solid rgba(79,142,247,0.3)', borderTopColor: '#4F8EF7', animation: 'spin 0.8s linear infinite' }} />
            )}
            <button
              onClick={() => searchResults.length > 0 && handleSelect(searchResults[0].ticker)}
              style={{
                padding: '10px 24px', borderRadius: 12,
                background: 'linear-gradient(135deg, #4F8EF7, #8B5CF6)',
                color: 'white', fontWeight: 700, fontSize: 14,
                border: 'none', cursor: 'pointer',
              }}
            >Analyze →</button>
          </div>

          {/* Search Results Dropdown */}
          {showResults && searchResults.length > 0 && (
            <div style={{
              position: 'absolute', top: '100%', left: 0, right: 0, marginTop: 8,
              background: 'rgba(13, 21, 40, 0.98)',
              border: '1px solid rgba(99,160,255,0.2)',
              borderRadius: 12, overflow: 'hidden',
              boxShadow: '0 20px 60px rgba(0,0,0,0.6)',
              zIndex: 200,
            }}>
              {searchResults.map((company, i) => (
                <button
                  key={company.ticker}
                  onClick={() => handleSelect(company.ticker)}
                  style={{
                    width: '100%', display: 'flex', alignItems: 'center',
                    gap: 16, padding: '14px 20px',
                    background: i === 0 ? 'rgba(79,142,247,0.05)' : 'transparent',
                    border: 'none', cursor: 'pointer',
                    textAlign: 'left',
                    borderBottom: i < searchResults.length - 1 ? '1px solid rgba(99,160,255,0.07)' : 'none',
                    transition: 'background 150ms',
                  }}
                  onMouseEnter={e => (e.currentTarget.style.background = 'rgba(79,142,247,0.08)')}
                  onMouseLeave={e => (e.currentTarget.style.background = i === 0 ? 'rgba(79,142,247,0.05)' : 'transparent')}
                >
                  {company.logo_url ? (
                    <img src={company.logo_url} alt="" width={32} height={32} style={{ borderRadius: 8, objectFit: 'contain' }} />
                  ) : (
                    <div style={{ width: 32, height: 32, borderRadius: 8, background: 'rgba(79,142,247,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 700, color: '#4F8EF7' }}>
                      {company.ticker?.[0]}
                    </div>
                  )}
                  <div style={{ flex: 1 }}>
                    <div style={{ color: '#E8F0FF', fontWeight: 600, fontSize: 14 }}>{company.name}</div>
                    <div style={{ color: 'rgba(139,164,200,0.7)', fontSize: 12 }}>{company.ticker} · {company.sector}</div>
                  </div>
                  {company.market_cap && (
                    <div style={{ color: '#8BA4C8', fontSize: 12 }}>
                      ${(company.market_cap / 1e9).toFixed(1)}B
                    </div>
                  )}
                  <span style={{ color: '#4F8EF7', fontSize: 12 }}>→</span>
                </button>
              ))}
            </div>
          )}
        </div>

        <p style={{ marginTop: 16, color: 'rgba(139,164,200,0.5)', fontSize: 13 }}>
          Try: AAPL · NVDA · TSLA · TSM · RELIANCE.NS · TCS.NS
        </p>
      </section>

      {/* Stats Bar */}
      <section style={{ padding: '0 32px 60px' }}>
        <div style={{
          maxWidth: 1200, margin: '0 auto',
          display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16,
        }}>
          {STATS.map(stat => (
            <div key={stat.label} className="glass-card" style={{ padding: '24px 28px', display: 'flex', alignItems: 'center', gap: 16 }}>
              <div style={{ fontSize: 32 }}>{stat.icon}</div>
              <div>
                <div style={{ fontSize: 28, fontWeight: 800, color: stat.color, fontFamily: 'JetBrains Mono, monospace', letterSpacing: '-0.02em' }}>{stat.value}</div>
                <div style={{ fontSize: 13, color: '#8BA4C8', fontWeight: 500, marginTop: 2 }}>{stat.label}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Main Content Grid */}
      <section style={{ padding: '0 32px 80px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', display: 'grid', gridTemplateColumns: '1fr 380px', gap: 24 }}>
          {/* Companies Grid */}
          <div>
            <div style={{ marginBottom: 20, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#E8F0FF' }}>Tracked Companies</h2>
              <Link href="/dashboard" style={{ color: '#4F8EF7', fontSize: 14, textDecoration: 'none', fontWeight: 500 }}>View all →</Link>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              {FEATURED_COMPANIES.map(company => (
                <Link key={company.ticker} href={`/company/${company.ticker}`} style={{ textDecoration: 'none' }}>
                  <div className="glass-card gradient-border" style={{ padding: '20px 22px', cursor: 'pointer' }}
                    onMouseEnter={e => (e.currentTarget.style.transform = 'translateY(-2px)')}
                    onMouseLeave={e => (e.currentTarget.style.transform = 'translateY(0)')}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: 16, color: '#E8F0FF' }}>{company.ticker}</div>
                        <div style={{ fontSize: 12, color: '#8BA4C8', marginTop: 2 }}>{company.name}</div>
                      </div>
                      <RiskBadge score={company.risk} />
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: 12, color: '#8BA4C8' }}>{company.sector}</span>
                      <span style={{ fontSize: 13, fontWeight: 600, color: company.change >= 0 ? '#10B981' : '#F43F5E', fontFamily: 'JetBrains Mono, monospace' }}>
                        {company.change >= 0 ? '+' : ''}{company.change}%
                      </span>
                    </div>
                    {/* Mini risk bar */}
                    <div style={{ marginTop: 12, height: 3, background: 'rgba(255,255,255,0.06)', borderRadius: 2 }}>
                      <div style={{
                        width: `${company.risk * 100}%`, height: '100%', borderRadius: 2,
                        background: company.risk >= 0.7 ? '#F43F5E' : company.risk >= 0.5 ? '#F97316' : company.risk >= 0.3 ? '#F59E0B' : '#10B981',
                        transition: 'width 0.5s ease',
                      }} />
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Alerts Panel */}
          <div>
            <div style={{ marginBottom: 20, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <h2 style={{ fontSize: 20, fontWeight: 700, color: '#E8F0FF' }}>🔔 Live Alerts</h2>
              <Link href="/alerts" style={{ color: '#4F8EF7', fontSize: 14, textDecoration: 'none', fontWeight: 500 }}>All alerts →</Link>
            </div>
            <div className="glass-card" style={{ overflow: 'hidden' }}>
              {RECENT_ALERTS.map((alert, i) => (
                <div key={i} style={{
                  display: 'flex', gap: 12, padding: '16px 20px',
                  borderBottom: i < RECENT_ALERTS.length - 1 ? '1px solid rgba(99,160,255,0.07)' : 'none',
                }}>
                  <div style={{ paddingTop: 5, flexShrink: 0 }}>
                    <AlertBadge type={alert.type} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <p style={{ fontSize: 13, color: '#C8D8F0', lineHeight: 1.5, marginBottom: 4 }}>{alert.text}</p>
                    <span style={{ fontSize: 11, color: '#4A6080' }}>{alert.time}</span>
                  </div>
                </div>
              ))}
              <div style={{ padding: '12px 20px', background: 'rgba(79,142,247,0.04)', borderTop: '1px solid rgba(99,160,255,0.07)' }}>
                <Link href="/alerts" style={{ color: '#4F8EF7', fontSize: 13, textDecoration: 'none', fontWeight: 500, display: 'flex', alignItems: 'center', gap: 4 }}>
                  View all risk alerts <span>→</span>
                </Link>
              </div>
            </div>

            {/* Quick action */}
            <div className="glass-card" style={{ marginTop: 16, padding: '20px 22px', background: 'linear-gradient(135deg, rgba(79,142,247,0.08), rgba(139,92,246,0.08))' }}>
              <div style={{ fontSize: 24, marginBottom: 8 }}>🤖</div>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: '#E8F0FF', marginBottom: 6 }}>AI Policy Analyzer</h3>
              <p style={{ fontSize: 13, color: '#8BA4C8', lineHeight: 1.5, marginBottom: 14 }}>Paste any government policy text and get instant AI-powered supply chain impact analysis.</p>
              <Link href="/dashboard?tab=ai" style={{
                display: 'block', textAlign: 'center', padding: '10px',
                borderRadius: 10, background: 'linear-gradient(135deg, #4F8EF7, #8B5CF6)',
                color: 'white', fontWeight: 600, fontSize: 13,
                textDecoration: 'none',
              }}>Try AI Analysis →</Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section style={{ padding: '0 32px 100px' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <h2 style={{ fontSize: 36, fontWeight: 800, textAlign: 'center', marginBottom: 48, letterSpacing: '-0.02em' }}>
            Everything you need for
            <span className="gradient-text"> intelligent</span> decisions
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
            {[
              { icon: '🕸️', title: 'Supply Chain Graph', desc: 'Interactive Tier 1-3 supplier visualization with risk coloring and dependency analysis', color: '#4F8EF7' },
              { icon: '📊', title: 'Financial Intelligence', desc: 'Real-time stock prices, income statements, balance sheets, and financial ratios', color: '#8B5CF6' },
              { icon: '🏛️', title: 'Policy Tracking', desc: 'Auto-detect policies from PIB India, White House, SEC, EU, WTO and more', color: '#22D3EE' },
              { icon: '⚠️', title: 'Risk Scoring', desc: 'AI-powered composite risk scores across 5 dimensions with trend history', color: '#F59E0B' },
              { icon: '🤖', title: 'AI Impact Simulation', desc: 'Simulate how policy changes ripple through supply chains and estimate stock impact', color: '#10B981' },
              { icon: '📰', title: 'News Intelligence', desc: 'FinBERT sentiment analysis on thousands of articles with company linking', color: '#F43F5E' },
            ].map(feature => (
              <div key={feature.title} className="glass-card gradient-border" style={{ padding: '28px' }}>
                <div style={{ fontSize: 36, marginBottom: 16 }}>{feature.icon}</div>
                <h3 style={{ fontSize: 17, fontWeight: 700, color: '#E8F0FF', marginBottom: 10 }}>{feature.title}</h3>
                <p style={{ fontSize: 14, color: '#8BA4C8', lineHeight: 1.6 }}>{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid rgba(99,160,255,0.1)',
        padding: '32px',
        textAlign: 'center',
        color: '#4A6080',
        fontSize: 13,
      }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontWeight: 700, color: '#8BA4C8' }}>SCI Platform</span>
            <span>·</span>
            <span>Supply Chain Intelligence</span>
          </div>
          <div>Built with FastAPI · Neo4j · Next.js · AI</div>
          <div>v1.0.0</div>
        </div>
      </footer>

      <style jsx global>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
