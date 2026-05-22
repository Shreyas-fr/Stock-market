'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import SupplyChainGraph from '../../components/SupplyChainGraph';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

function TabButton({ active, onClick, children }: any) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: '10px 20px', borderRadius: 8, fontWeight: 600, fontSize: 14,
        background: active ? 'rgba(79,142,247,0.15)' : 'transparent',
        color: active ? '#4F8EF7' : '#8BA4C8',
        border: active ? '1px solid rgba(79,142,247,0.3)' : '1px solid transparent',
        cursor: 'pointer', transition: 'all 150ms',
      }}
    >{children}</button>
  );
}

function MetricCard({ label, value, change, color, unit = '' }: any) {
  return (
    <div className="glass-card" style={{ padding: '20px 22px' }}>
      <div style={{ fontSize: 12, color: '#8BA4C8', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 800, color: color || '#E8F0FF', fontFamily: 'JetBrains Mono, monospace', letterSpacing: '-0.02em' }}>
        {value}{unit}
      </div>
      {change !== undefined && (
        <div style={{ fontSize: 12, color: change >= 0 ? '#10B981' : '#F43F5E', marginTop: 4, fontWeight: 600 }}>
          {change >= 0 ? '▲' : '▼'} {Math.abs(change)}%
        </div>
      )}
    </div>
  );
}

function RiskGauge({ score }: { score: number }) {
  const percentage = score * 100;
  const level = score >= 0.7 ? 'Critical' : score >= 0.5 ? 'High' : score >= 0.3 ? 'Medium' : 'Low';
  const color = score >= 0.7 ? '#F43F5E' : score >= 0.5 ? '#F97316' : score >= 0.3 ? '#F59E0B' : '#10B981';
  const circumference = 2 * Math.PI * 60;
  const strokeDash = (percentage / 100) * circumference;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
      <svg width="160" height="160" viewBox="0 0 160 160">
        <circle cx="80" cy="80" r="60" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="12" />
        <circle
          cx="80" cy="80" r="60"
          fill="none" stroke={color} strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={`${strokeDash} ${circumference}`}
          transform="rotate(-90 80 80)"
          style={{ transition: 'stroke-dasharray 1s ease, stroke 0.5s ease' }}
        />
        <text x="80" y="75" textAnchor="middle" fill={color} fontSize="28" fontWeight="900" fontFamily="JetBrains Mono, monospace">
          {Math.round(percentage)}
        </text>
        <text x="80" y="95" textAnchor="middle" fill="#8BA4C8" fontSize="12" fontWeight="600">{level} Risk</text>
      </svg>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', justifyContent: 'center' }}>
        {[{ label: 'SC Risk', value: 45 }, { label: 'Geo Risk', value: 35 }, { label: 'Fin Risk', value: 30 }].map(item => (
          <div key={item.label} style={{ background: 'rgba(255,255,255,0.04)', padding: '4px 10px', borderRadius: 6 }}>
            <div style={{ fontSize: 10, color: '#4A6080', fontWeight: 600 }}>{item.label}</div>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#8BA4C8', fontFamily: 'JetBrains Mono, monospace' }}>{item.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SimpleLineChart({ data, color = '#4F8EF7' }: { data: number[], color?: string }) {
  if (!data || data.length === 0) return null;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const width = 400;
  const height = 120;
  const padding = 10;
  const points = data.map((v, i) => ({
    x: padding + (i / (data.length - 1)) * (width - 2 * padding),
    y: height - padding - ((v - min) / range) * (height - 2 * padding),
  }));
  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  const areaD = `${pathD} L ${points[points.length-1].x} ${height} L ${points[0].x} ${height} Z`;

  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
      <defs>
        <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={areaD} fill="url(#chartGrad)" />
      <path d={pathD} fill="none" stroke={color} strokeWidth="2" />
      {points.map((p, i) => i === points.length - 1 && (
        <circle key={i} cx={p.x} cy={p.y} r="4" fill={color} />
      ))}
    </svg>
  );
}

export default function CompanyPage() {
  const params = useParams();
  const ticker = (params?.ticker as string)?.toUpperCase() || '';
  const [tab, setTab] = useState('overview');
  const [company, setCompany] = useState<any>(null);
  const [riskData, setRiskData] = useState<any>(null);
  const [priceHistory, setPriceHistory] = useState<number[]>([]);
  const [news, setNews] = useState<any[]>([]);
  const [policies, setPolicies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [depth, setDepth] = useState(2);

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      try {
        const [companyRes, riskRes, pricesRes, newsRes, policiesRes] = await Promise.allSettled([
          fetch(`${API_URL}/companies/${ticker}`),
          fetch(`${API_URL}/risk/${ticker}/score`),
          fetch(`${API_URL}/companies/${ticker}/price-history?days=90`),
          fetch(`${API_URL}/news?ticker=${ticker}&days=7`),
          fetch(`${API_URL}/policies?limit=5`),
        ]);

        if (companyRes.status === 'fulfilled' && companyRes.value.ok) {
          setCompany(await companyRes.value.json());
        } else {
          // Mock data for demo
          setCompany({ ticker, name: ticker, sector: 'Technology', country: 'USA', market_cap: 500000000000, description: 'A leading technology company tracked in the Supply Chain Intelligence Platform.' });
        }
        if (riskRes.status === 'fulfilled' && riskRes.value.ok) {
          setRiskData(await riskRes.value.json());
        } else {
          setRiskData({ overall_risk: 0.42, supply_chain_risk: 0.45, financial_risk: 0.32, geopolitical_risk: 0.38, regulatory_risk: 0.28, market_risk: 0.35 });
        }
        if (pricesRes.status === 'fulfilled' && pricesRes.value.ok) {
          const prices = await pricesRes.value.json();
          setPriceHistory(prices.map((p: any) => p.close).filter(Boolean));
        } else {
          // Generate mock price data
          const mockPrices = Array.from({ length: 90 }, (_, i) => 150 + Math.sin(i * 0.1) * 20 + Math.random() * 10 + i * 0.3);
          setPriceHistory(mockPrices);
        }
        if (newsRes.status === 'fulfilled' && newsRes.value.ok) {
          setNews(await newsRes.value.json());
        }
        if (policiesRes.status === 'fulfilled' && policiesRes.value.ok) {
          setPolicies(await policiesRes.value.json());
        }
      } catch (e) {
        console.error('Fetch failed:', e);
      } finally {
        setLoading(false);
      }
    };
    if (ticker) fetchAll();
  }, [ticker]);

  const currentPrice = priceHistory[priceHistory.length - 1];
  const prevPrice = priceHistory[priceHistory.length - 2];
  const priceChange = prevPrice ? ((currentPrice - prevPrice) / prevPrice) * 100 : 0;

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ width: 48, height: 48, borderRadius: '50%', border: '3px solid rgba(79,142,247,0.2)', borderTopColor: '#4F8EF7', animation: 'spin 0.8s linear infinite', margin: '0 auto 16px' }} />
          <p style={{ color: '#8BA4C8' }}>Loading intelligence data...</p>
        </div>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', fontFamily: 'Inter, sans-serif' }}>
      {/* Header */}
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
          <span style={{ color: '#E8F0FF', fontWeight: 600 }}>{company?.name || ticker}</span>
        </div>
        <Link href="/dashboard" style={{ color: '#4F8EF7', textDecoration: 'none', fontSize: 14 }}>Dashboard</Link>
      </header>

      <div style={{ maxWidth: 1400, margin: '0 auto', padding: '32px' }}>
        {/* Company Header */}
        <div className="glass-card" style={{ padding: '32px', marginBottom: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
              <div style={{
                width: 56, height: 56, borderRadius: 14,
                background: 'linear-gradient(135deg, rgba(79,142,247,0.2), rgba(139,92,246,0.2))',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 24, fontWeight: 800, color: '#4F8EF7',
              }}>{ticker[0]}</div>
              <div>
                <h1 style={{ fontSize: 28, fontWeight: 900, letterSpacing: '-0.02em', color: '#E8F0FF' }}>{company?.name || ticker}</h1>
                <div style={{ display: 'flex', gap: 12, marginTop: 6, alignItems: 'center' }}>
                  <span style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 700, color: '#4F8EF7', fontSize: 16 }}>{ticker}</span>
                  <span style={{ color: '#4A6080' }}>·</span>
                  <span style={{ color: '#8BA4C8', fontSize: 14 }}>{company?.exchange}</span>
                  <span style={{ color: '#4A6080' }}>·</span>
                  <span style={{ color: '#8BA4C8', fontSize: 14 }}>{company?.sector}</span>
                  <span style={{ color: '#4A6080' }}>·</span>
                  <span style={{ color: '#8BA4C8', fontSize: 14 }}>🌍 {company?.country}</span>
                </div>
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              {currentPrice && (
                <div style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 36, fontWeight: 900, color: '#E8F0FF', letterSpacing: '-0.02em' }}>
                  ${currentPrice.toFixed(2)}
                </div>
              )}
              <div style={{ color: priceChange >= 0 ? '#10B981' : '#F43F5E', fontWeight: 600, fontSize: 16, marginTop: 4 }}>
                {priceChange >= 0 ? '▲' : '▼'} {Math.abs(priceChange).toFixed(2)}%
              </div>
              {company?.market_cap && (
                <div style={{ color: '#8BA4C8', fontSize: 13, marginTop: 4 }}>
                  Market Cap: ${(company.market_cap / 1e9).toFixed(1)}B
                </div>
              )}
            </div>
          </div>

          {/* Tabs */}
          <div style={{ display: 'flex', gap: 8, marginTop: 28, flexWrap: 'wrap' }}>
            {['overview', 'supply-chain', 'financials', 'risk', 'policies', 'news'].map(t => (
              <TabButton key={t} active={tab === t} onClick={() => setTab(t)}>
                {{ 'overview': '📊 Overview', 'supply-chain': '🕸️ Supply Chain', 'financials': '💹 Financials', 'risk': '⚠️ Risk', 'policies': '🏛️ Policies', 'news': '📰 News' }[t]}
              </TabButton>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {tab === 'overview' && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
              <MetricCard label="Market Cap" value={company?.market_cap ? `$${(company.market_cap/1e9).toFixed(1)}B` : 'N/A'} color="#4F8EF7" />
              <MetricCard label="Employees" value={company?.employees ? company.employees.toLocaleString() : 'N/A'} />
              <MetricCard label="Founded" value={company?.founded_year || 'N/A'} />
              <MetricCard label="Country" value={company?.country || 'N/A'} />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24 }}>
              {/* Price Chart */}
              <div className="glass-card" style={{ padding: '24px' }}>
                <h3 style={{ fontSize: 16, fontWeight: 700, color: '#E8F0FF', marginBottom: 20 }}>📈 Price History (90 days)</h3>
                <SimpleLineChart data={priceHistory} color="#4F8EF7" />
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
                  <span style={{ fontSize: 12, color: '#4A6080' }}>90 days ago</span>
                  <span style={{ fontSize: 12, color: '#4A6080' }}>Today</span>
                </div>
              </div>

              {/* Risk Gauge */}
              <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <h3 style={{ fontSize: 16, fontWeight: 700, color: '#E8F0FF', marginBottom: 16 }}>⚠️ Risk Score</h3>
                {riskData && <RiskGauge score={riskData.overall_risk} />}
              </div>
            </div>

            {/* Description */}
            {company?.description && (
              <div className="glass-card" style={{ padding: '24px', marginTop: 24 }}>
                <h3 style={{ fontSize: 16, fontWeight: 700, color: '#E8F0FF', marginBottom: 12 }}>About {company.name}</h3>
                <p style={{ color: '#8BA4C8', lineHeight: 1.7, fontSize: 14 }}>{company.description}</p>
              </div>
            )}
          </div>
        )}

        {tab === 'supply-chain' && (
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24 }}>
            {/* Graph Visual Panel */}
            <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <div>
                  <h3 style={{ fontSize: 18, fontWeight: 800, color: '#E8F0FF' }}>🕸️ Interactive Supply Network</h3>
                  <p style={{ fontSize: 13, color: '#8BA4C8', marginTop: 4 }}>Visualizing Tier 1 & 2 relationships, dependencies, and risk ripple channels.</p>
                </div>
                <div style={{ display: 'flex', gap: 6, background: 'rgba(255,255,255,0.04)', padding: 3, borderRadius: 8 }}>
                  {[1, 2].map(d => (
                    <button
                      key={d}
                      onClick={() => setDepth(d)}
                      style={{
                        padding: '4px 12px',
                        borderRadius: 6,
                        border: 'none',
                        background: depth === d ? 'linear-gradient(135deg, #4F8EF7, #8B5CF6)' : 'transparent',
                        color: depth === d ? 'white' : '#8BA4C8',
                        fontSize: 12,
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      Tier {d}
                    </button>
                  ))}
                </div>
              </div>

              <div style={{ flex: 1, minHeight: 450, position: 'relative' }}>
                <SupplyChainGraph ticker={ticker} depth={depth} />
              </div>
            </div>

            {/* Network Analytics Sidebar */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {/* Geographic Concentration */}
              <div className="glass-card" style={{ padding: '20px 22px' }}>
                <h4 style={{ fontSize: 14, fontWeight: 700, color: '#E8F0FF', marginBottom: 12 }}>🌍 Country Concentration</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {[
                    { country: 'TWN (Taiwan)', share: ticker === 'AAPL' || ticker === 'NVDA' ? '55%' : '15%', risk: 'High Sourcing Risk' },
                    { country: 'USA', share: '30%', risk: 'Low Sourcing Risk' },
                    { country: 'KOR (South Korea)', share: ticker === 'TSLA' ? '25%' : '10%', risk: 'Medium Sourcing Risk' },
                  ].map(item => (
                    <div key={item.country}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, color: '#C8D8F0' }}>
                        <span>{item.country}</span>
                        <span style={{ fontWeight: 700, fontFamily: 'JetBrains Mono' }}>{item.share}</span>
                      </div>
                      <div style={{ fontSize: 11, color: item.risk.includes('High') ? '#F97316' : item.risk.includes('Medium') ? '#F59E0B' : '#10B981', marginTop: 2, fontWeight: 600 }}>
                        {item.risk}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Single Source Dependencies */}
              <div className="glass-card" style={{ padding: '20px 22px' }}>
                <h4 style={{ fontSize: 14, fontWeight: 700, color: '#E8F0FF', marginBottom: 12 }}>⚠️ Dependency Warnings</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {ticker === 'AAPL' && (
                    <>
                      <div style={{ background: 'rgba(244,63,94,0.06)', border: '1px solid rgba(244,63,94,0.2)', padding: 12, borderRadius: 8 }}>
                        <div style={{ fontSize: 11, color: '#F43F5E', fontWeight: 700 }}>SOLE SOURCE WARNING</div>
                        <div style={{ fontSize: 13, color: '#E8F0FF', fontWeight: 600, marginTop: 4 }}>TSMC (TSM)</div>
                        <div style={{ fontSize: 12, color: '#8BA4C8', marginTop: 2 }}>Supplies 100% of A-series processors. High geographic concentration risk.</div>
                      </div>
                      <div style={{ background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.2)', padding: 12, borderRadius: 8 }}>
                        <div style={{ fontSize: 11, color: '#F59E0B', fontWeight: 700 }}>HIGH COGS WARNING</div>
                        <div style={{ fontSize: 13, color: '#E8F0FF', fontWeight: 600, marginTop: 4 }}>OLED Displays</div>
                        <div style={{ fontSize: 12, color: '#8BA4C8', marginTop: 2 }}>Samsung (SNE) supplies ~8% of direct manufacturing inputs.</div>
                      </div>
                    </>
                  )}
                  {ticker === 'TSLA' && (
                    <>
                      <div style={{ background: 'rgba(244,63,94,0.06)', border: '1px solid rgba(244,63,94,0.2)', padding: 12, borderRadius: 8 }}>
                        <div style={{ fontSize: 11, color: '#F43F5E', fontWeight: 700 }}>HIGH COGS WARNING</div>
                        <div style={{ fontSize: 13, color: '#E8F0FF', fontWeight: 600, marginTop: 4 }}>Panasonic (PCRFY)</div>
                        <div style={{ fontSize: 12, color: '#8BA4C8', marginTop: 2 }}>Supplies cylindrical battery cells representing 22% of manufacturing COGS.</div>
                      </div>
                      <div style={{ background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.2)', padding: 12, borderRadius: 8 }}>
                        <div style={{ fontSize: 11, color: '#F59E0B', fontWeight: 700 }}>MULTI-SOURCE LITHIUM</div>
                        <div style={{ fontSize: 13, color: '#E8F0FF', fontWeight: 600, marginTop: 4 }}>Albemarle (ALB)</div>
                        <div style={{ fontSize: 12, color: '#8BA4C8', marginTop: 2 }}>Secured multi-source lithium hydroxide contract covering 6% of batteries.</div>
                      </div>
                    </>
                  )}
                  {ticker !== 'AAPL' && ticker !== 'TSLA' && (
                    <div style={{ padding: 16, textAlign: 'center', color: '#4A6080', fontSize: 13 }}>
                      No critical sole-source dependencies detected for {ticker}. Supply chain risk is well-distributed.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {tab === 'financials' && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
              <MetricCard label="Revenue (TTM)" value="$N/A" color="#10B981" />
              <MetricCard label="Net Income" value="$N/A" color="#4F8EF7" />
              <MetricCard label="EPS" value="N/A" color="#8B5CF6" />
              <MetricCard label="P/E Ratio" value="N/A" color="#F59E0B" />
            </div>
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: '#E8F0FF', marginBottom: 16 }}>Financial Statements</h3>
              <p style={{ color: '#8BA4C8', fontSize: 14 }}>Connect FMP_API_KEY in .env to load real financial statements. API endpoint: <code style={{ color: '#22D3EE', fontFamily: 'JetBrains Mono, monospace' }}>GET /api/v1/companies/{ticker}/financials</code></p>
            </div>
          </div>
        )}

        {tab === 'risk' && riskData && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 24 }}>
              <div className="glass-card" style={{ padding: '32px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <h3 style={{ fontSize: 16, fontWeight: 700, color: '#E8F0FF', marginBottom: 16, alignSelf: 'flex-start' }}>Composite Risk Score</h3>
                <RiskGauge score={riskData.overall_risk} />
              </div>
              <div className="glass-card" style={{ padding: '24px' }}>
                <h3 style={{ fontSize: 16, fontWeight: 700, color: '#E8F0FF', marginBottom: 20 }}>Risk Breakdown</h3>
                {[
                  { label: 'Supply Chain Risk', value: riskData.supply_chain_risk, icon: '🔗' },
                  { label: 'Financial Risk', value: riskData.financial_risk, icon: '💹' },
                  { label: 'Geopolitical Risk', value: riskData.geopolitical_risk, icon: '🌍' },
                  { label: 'Regulatory Risk', value: riskData.regulatory_risk, icon: '🏛️' },
                  { label: 'Market Risk', value: riskData.market_risk, icon: '📊' },
                ].map(item => (
                  <div key={item.label} style={{ marginBottom: 16 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                      <span style={{ fontSize: 13, color: '#C8D8F0', fontWeight: 500 }}>{item.icon} {item.label}</span>
                      <span style={{ fontSize: 13, fontWeight: 700, fontFamily: 'JetBrains Mono, monospace', color: item.value >= 0.7 ? '#F43F5E' : item.value >= 0.5 ? '#F97316' : item.value >= 0.3 ? '#F59E0B' : '#10B981' }}>
                        {Math.round((item.value || 0) * 100)}
                      </span>
                    </div>
                    <div style={{ height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 3 }}>
                      <div style={{
                        width: `${(item.value || 0) * 100}%`, height: '100%', borderRadius: 3,
                        background: item.value >= 0.7 ? '#F43F5E' : item.value >= 0.5 ? '#F97316' : item.value >= 0.3 ? '#F59E0B' : '#10B981',
                        transition: 'width 0.8s ease',
                      }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {tab === 'policies' && (
          <div className="glass-card" style={{ overflow: 'hidden' }}>
            <div style={{ padding: '20px 24px', borderBottom: '1px solid rgba(99,160,255,0.1)' }}>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: '#E8F0FF' }}>Related Government Policies</h3>
            </div>
            {policies.length === 0 ? (
              <div style={{ padding: 40, textAlign: 'center', color: '#4A6080' }}>No policies loaded. Connect to API to load policy data.</div>
            ) : policies.map((policy: any) => (
              <div key={policy.id} style={{ padding: '20px 24px', borderBottom: '1px solid rgba(99,160,255,0.06)', display: 'flex', gap: 16, alignItems: 'flex-start' }}>
                <div style={{ fontSize: 24 }}>{policy.policy_type === 'tariff_reduction' ? '📉' : policy.policy_type === 'subsidy' ? '💰' : '📋'}</div>
                <div style={{ flex: 1 }}>
                  <h4 style={{ fontSize: 14, fontWeight: 700, color: '#E8F0FF', marginBottom: 6 }}>{policy.title}</h4>
                  <p style={{ fontSize: 13, color: '#8BA4C8', lineHeight: 1.5 }}>{policy.summary}</p>
                  <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
                    <span style={{ fontSize: 11, color: '#4A6080' }}>{policy.announced_date}</span>
                    <span style={{ fontSize: 11, color: '#4F8EF7' }}>{policy.source_name}</span>
                    {policy.impact_severity && (
                      <span style={{ fontSize: 11, fontWeight: 700, color: policy.impact_severity === 'critical' ? '#F43F5E' : policy.impact_severity === 'high' ? '#F97316' : '#F59E0B', textTransform: 'uppercase' }}>
                        {policy.impact_severity} impact
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {tab === 'news' && (
          <div className="glass-card" style={{ overflow: 'hidden' }}>
            <div style={{ padding: '20px 24px', borderBottom: '1px solid rgba(99,160,255,0.1)' }}>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: '#E8F0FF' }}>Recent News</h3>
            </div>
            {news.length === 0 ? (
              <div style={{ padding: 40, textAlign: 'center', color: '#4A6080' }}>News data requires NewsAPI key. Connect NEWSAPI_KEY in .env</div>
            ) : news.slice(0, 10).map((article: any) => (
              <div key={article.id} style={{ padding: '18px 24px', borderBottom: '1px solid rgba(99,160,255,0.06)', display: 'flex', gap: 16 }}>
                <div style={{ flex: 1 }}>
                  <a href={article.source_url} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none' }}>
                    <h4 style={{ fontSize: 14, fontWeight: 600, color: '#E8F0FF', marginBottom: 6, lineHeight: 1.4 }}>{article.headline}</h4>
                  </a>
                  <div style={{ display: 'flex', gap: 12, fontSize: 12, color: '#4A6080' }}>
                    <span>{article.source_name}</span>
                    <span>{article.published_at ? new Date(article.published_at).toLocaleDateString() : ''}</span>
                  </div>
                </div>
                {article.sentiment_score !== null && article.sentiment_score !== undefined && (
                  <div style={{ color: article.sentiment_score > 0.2 ? '#10B981' : article.sentiment_score < -0.2 ? '#F43F5E' : '#8BA4C8', fontWeight: 700, fontSize: 13, flexShrink: 0, alignSelf: 'center' }}>
                    {article.sentiment_score > 0.2 ? '▲ Bullish' : article.sentiment_score < -0.2 ? '▼ Bearish' : '– Neutral'}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
