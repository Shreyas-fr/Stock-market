'use client';

import { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';

// Mock high-fidelity data matching seed database
const MOCK_GRAPH_DATA: Record<string, {
  nodes: Array<{ id: string; ticker: string; name: string; sector: string; country: string; risk_score: number; market_cap?: number; type: 'target' | 'supplier' | 'customer'; tier: number }>;
  edges: Array<{ source: string; target: string; product: string; share_of_cogs: number; contract_type: 'sole-source' | 'multi-source'; confidence: number }>;
}> = {
  AAPL: {
    nodes: [
      { id: 'AAPL', ticker: 'AAPL', name: 'Apple Inc.', sector: 'Technology', country: 'USA', risk_score: 0.35, market_cap: 2900000000000, type: 'target', tier: 0 },
      { id: 'TSM', ticker: 'TSM', name: 'TSMC', sector: 'Semiconductors', country: 'TWN', risk_score: 0.58, market_cap: 550000000000, type: 'supplier', tier: 1 },
      { id: 'QCOM', ticker: 'QCOM', name: 'Qualcomm Inc.', sector: 'Semiconductors', country: 'USA', risk_score: 0.42, market_cap: 200000000000, type: 'supplier', tier: 1 },
      { id: 'SONY', ticker: 'SONY', name: 'Sony Group', sector: 'Consumer Electronics', country: 'JPN', risk_score: 0.30, market_cap: 120000000000, type: 'supplier', tier: 1 },
      { id: 'SNE', ticker: 'SNE', name: 'Samsung Electronics', sector: 'Consumer Electronics', country: 'KOR', risk_score: 0.32, market_cap: 330000000000, type: 'supplier', tier: 1 },
      { id: 'AMAT', ticker: 'AMAT', name: 'Applied Materials', sector: 'Semiconductor Equipment', country: 'USA', risk_score: 0.28, market_cap: 150000000000, type: 'supplier', tier: 2 },
      { id: 'WMT', ticker: 'WMT', name: 'Walmart Inc.', sector: 'Discount Retail', country: 'USA', risk_score: 0.22, market_cap: 600000000000, type: 'customer', tier: 1 },
    ],
    edges: [
      { source: 'TSM', target: 'AAPL', product: 'A-series chips', share_of_cogs: 0.18, contract_type: 'sole-source', confidence: 0.95 },
      { source: 'QCOM', target: 'AAPL', product: '5G modems', share_of_cogs: 0.05, contract_type: 'multi-source', confidence: 0.90 },
      { source: 'SONY', target: 'AAPL', product: 'CMOS image sensors', share_of_cogs: 0.04, contract_type: 'sole-source', confidence: 0.88 },
      { source: 'SNE', target: 'AAPL', product: 'OLED displays', share_of_cogs: 0.08, contract_type: 'multi-source', confidence: 0.85 },
      { source: 'AMAT', target: 'TSM', product: 'deposition and etch equipment', share_of_cogs: 0.15, contract_type: 'multi-source', confidence: 0.90 },
      { source: 'AAPL', target: 'WMT', product: 'iPhones & Consumer Tech', share_of_cogs: 0.02, contract_type: 'multi-source', confidence: 0.99 },
    ],
  },
  TSLA: {
    nodes: [
      { id: 'TSLA', ticker: 'TSLA', name: 'Tesla Inc.', sector: 'Electric Vehicles', country: 'USA', risk_score: 0.55, market_cap: 700000000000, type: 'target', tier: 0 },
      { id: 'PCRFY', ticker: 'PCRFY', name: 'Panasonic Holdings', sector: 'Battery Manufacturing', country: 'JPN', risk_score: 0.35, market_cap: 25000000000, type: 'supplier', tier: 1 },
      { id: 'LGES.KS', ticker: 'LGES.KS', name: 'LG Energy Solution', sector: 'Battery Manufacturing', country: 'KOR', risk_score: 0.40, market_cap: 70000000000, type: 'supplier', tier: 1 },
      { id: 'ALB', ticker: 'ALB', name: 'Albemarle Corp.', sector: 'Lithium Mining', country: 'USA', risk_score: 0.48, market_cap: 10000000000, type: 'supplier', tier: 2 },
      { id: 'WMT', ticker: 'WMT', name: 'Walmart Inc.', sector: 'Discount Retail', country: 'USA', risk_score: 0.22, market_cap: 600000000000, type: 'customer', tier: 1 },
    ],
    edges: [
      { source: 'PCRFY', target: 'TSLA', product: 'cylindrical battery cells', share_of_cogs: 0.22, contract_type: 'multi-source', confidence: 0.92 },
      { source: 'LGES.KS', target: 'TSLA', product: 'NMC battery cells', share_of_cogs: 0.15, contract_type: 'multi-source', confidence: 0.90 },
      { source: 'ALB', target: 'TSLA', product: 'lithium hydroxide', share_of_cogs: 0.06, contract_type: 'multi-source', confidence: 0.88 },
      { source: 'ALB', target: 'LGES.KS', product: 'battery-grade lithium carbonate', share_of_cogs: 0.35, contract_type: 'sole-source', confidence: 0.91 },
      { source: 'TSLA', target: 'WMT', product: 'Commercial Solar & Megapacks', share_of_cogs: 0.01, contract_type: 'multi-source', confidence: 0.95 },
    ],
  },
  NVDA: {
    nodes: [
      { id: 'NVDA', ticker: 'NVDA', name: 'NVIDIA Corp.', sector: 'Semiconductors', country: 'USA', risk_score: 0.42, market_cap: 2500000000000, type: 'target', tier: 0 },
      { id: 'TSM', ticker: 'TSM', name: 'TSMC', sector: 'Semiconductors', country: 'TWN', risk_score: 0.58, market_cap: 550000000000, type: 'supplier', tier: 1 },
      { id: 'SNE', ticker: 'SNE', name: 'Samsung Electronics', sector: 'Consumer Electronics', country: 'KOR', risk_score: 0.32, market_cap: 330000000000, type: 'supplier', tier: 1 },
      { id: 'AMAT', ticker: 'AMAT', name: 'Applied Materials', sector: 'Semiconductor Equipment', country: 'USA', risk_score: 0.28, market_cap: 150000000000, type: 'supplier', tier: 2 },
    ],
    edges: [
      { source: 'TSM', target: 'NVDA', product: 'GPU wafers (3nm/4nm)', share_of_cogs: 0.55, contract_type: 'sole-source', confidence: 0.98 },
      { source: 'SNE', target: 'NVDA', product: 'HBM memory', share_of_cogs: 0.10, contract_type: 'multi-source', confidence: 0.80 },
      { source: 'AMAT', target: 'TSM', product: 'deposition and etch equipment', share_of_cogs: 0.15, contract_type: 'multi-source', confidence: 0.90 },
    ],
  },
};

interface SupplyChainGraphProps {
  ticker: string;
  depth?: number;
  onSelectNode?: (node: any) => void;
  onSelectEdge?: (edge: any) => void;
}

export default function SupplyChainGraph({
  ticker,
  depth = 2,
  onSelectNode,
  onSelectEdge,
}: SupplyChainGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [selectedElement, setSelectedElement] = useState<any>(null);

  // Load and render graph
  useEffect(() => {
    if (!containerRef.current) return;

    // 1. Get raw graph data (Mock or API)
    const rawData = MOCK_GRAPH_DATA[ticker.toUpperCase()] || {
      nodes: [
        { id: ticker, ticker, name: `${ticker} Corp.`, sector: 'General Industry', country: 'USA', risk_score: 0.30, type: 'target', tier: 0 },
        { id: 'SUP-A', ticker: 'SUP-A', name: 'Supplier Alpha', sector: 'Raw Materials', country: 'CAN', risk_score: 0.15, type: 'supplier', tier: 1 },
        { id: 'SUP-B', ticker: 'SUP-B', name: 'Supplier Beta', sector: 'Components', country: 'DEU', risk_score: 0.65, type: 'supplier', tier: 1 },
        { id: 'SUB-A', ticker: 'SUB-A', name: 'Sub-tier Corp', sector: 'Basic Metals', country: 'CHN', risk_score: 0.75, type: 'supplier', tier: 2 },
      ],
      edges: [
        { source: 'SUP-A', target: ticker, product: 'Refined Metals', share_of_cogs: 0.10, contract_type: 'multi-source', confidence: 0.92 },
        { source: 'SUP-B', target: ticker, product: 'Integrated Circuits', share_of_cogs: 0.35, contract_type: 'sole-source', confidence: 0.88 },
        { source: 'SUB-A', target: 'SUP-B', product: 'Solder Alloys', share_of_cogs: 0.20, contract_type: 'sole-source', confidence: 0.85 },
      ],
    };

    // Filter by depth
    const nodes = rawData.nodes.filter(n => n.type === 'target' || n.tier <= depth);
    const nodeIds = new Set(nodes.map(n => n.id));
    const edges = rawData.edges.filter(e => nodeIds.has(e.source) && nodeIds.has(e.target));

    // 2. Generate perfect layout positions for horizontal flow
    // Col 1: Tier 2 (x=120)
    // Col 2: Tier 1 (x=360)
    // Col 3: Target (x=600)
    // Col 4: Downstream (x=840)
    const tier2Nodes = nodes.filter(n => n.type === 'supplier' && n.tier === 2);
    const tier1Nodes = nodes.filter(n => n.type === 'supplier' && n.tier === 1);
    const targetNodes = nodes.filter(n => n.type === 'target');
    const customerNodes = nodes.filter(n => n.type === 'customer');

    const getVerticalCoords = (arr: any[], xVal: number) => {
      const spacing = 100;
      const startY = 300 - ((arr.length - 1) * spacing) / 2;
      return arr.map((node, i) => ({
        data: {
          ...node,
          riskColor: node.risk_score >= 0.7 ? '#F43F5E' : node.risk_score >= 0.5 ? '#F97316' : node.risk_score >= 0.3 ? '#F59E0B' : '#10B981',
          riskLevel: node.risk_score >= 0.7 ? 'CRITICAL' : node.risk_score >= 0.5 ? 'HIGH' : node.risk_score >= 0.3 ? 'MEDIUM' : 'LOW',
        },
        position: { x: xVal, y: startY + i * spacing },
      }));
    };

    const cyNodes = [
      ...getVerticalCoords(tier2Nodes, 120),
      ...getVerticalCoords(tier1Nodes, 360),
      ...getVerticalCoords(targetNodes, 600),
      ...getVerticalCoords(customerNodes, 840),
    ];

    const cyEdges = edges.map(e => ({
      data: {
        id: `${e.source}-${e.target}`,
        source: e.source,
        target: e.target,
        product: e.product,
        share_of_cogs: e.share_of_cogs,
        contract_type: e.contract_type,
        confidence: e.confidence,
        weight: e.share_of_cogs * 100,
      },
    }));

    // 3. Initialize Cytoscape
    const cy = cytoscape({
      container: containerRef.current,
      elements: [...cyNodes, ...cyEdges],
      layout: { name: 'preset' },
      style: [
        {
          selector: 'node',
          style: {
            'width': 44,
            'height': 44,
            'label': 'data(ticker)',
            'color': '#E8F0FF',
            'font-family': 'JetBrains Mono, monospace',
            'font-weight': 'bold',
            'font-size': '12px',
            'text-valign': 'bottom',
            'text-margin-y': 8,
            'background-color': '#0D1528',
            'border-width': 2.5,
            'border-color': 'data(riskColor)',
            'overlay-color': '#4F8EF7',
            'overlay-opacity': 0,
            'transition-property': 'background-color, border-color, width, height, border-width',
            'transition-duration': 0.2,
          },
        },
        {
          selector: 'node[type="target"]',
          style: {
            'width': 56,
            'height': 56,
            'border-width': 3,
            'border-color': '#4F8EF7',
            'background-color': '#111D35',
          },
        },
        {
          selector: 'edge',
          style: {
            'width': 'mapData(weight, 0, 100, 1.5, 7)',
            'line-color': 'rgba(99, 160, 255, 0.25)',
            'target-arrow-color': 'rgba(99, 160, 255, 0.45)',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'control-point-step-size': 40,
            'overlay-opacity': 0,
            'transition-property': 'line-color, target-arrow-color',
            'transition-duration': 0.2,
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 4,
            'background-color': '#111D35',
          },
        },
        {
          selector: 'edge:selected',
          style: {
            'line-color': '#4F8EF7',
            'target-arrow-color': '#4F8EF7',
          },
        },
        {
          selector: '.highlighted',
          style: {
            'line-color': '#8B5CF6',
            'target-arrow-color': '#8B5CF6',
          },
        },
        {
          selector: '.faded',
          style: {
            'opacity': 0.15,
          },
        },
      ],
      userZoomingEnabled: true,
      userPanningEnabled: true,
      boxSelectionEnabled: false,
    });

    cyRef.current = cy;

    // Hover Highlight Neighborhood
    cy.on('mouseover', 'node', (e) => {
      const node = e.target;
      const neighborhood = node.neighborhood().add(node);

      cy.elements().addClass('faded');
      neighborhood.removeClass('faded');
      neighborhood.edgesWith(node).addClass('highlighted');
    });

    cy.on('mouseout', 'node', () => {
      cy.elements().removeClass('faded');
      cy.edges().removeClass('highlighted');
    });

    // Handle Clicks
    cy.on('tap', (e) => {
      const target = e.target;
      if (target === cy) {
        setSelectedElement(null);
        if (onSelectNode) onSelectNode(null);
        if (onSelectEdge) onSelectEdge(null);
      } else if (target.isNode()) {
        const nodeData = target.data();
        setSelectedElement({ type: 'node', data: nodeData });
        if (onSelectNode) onSelectNode(nodeData);
      } else if (target.isEdge()) {
        const edgeData = target.data();
        setSelectedElement({ type: 'edge', data: edgeData });
        if (onSelectEdge) onSelectEdge(edgeData);
      }
    });

    // Auto-fit after rendering
    cy.fit(undefined, 40);

    return () => {
      cy.destroy();
    };
  }, [ticker, depth]);

  const resetZoom = () => {
    cyRef.current?.reset();
    cyRef.current?.fit(undefined, 40);
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* Graph Area */}
      <div
        ref={containerRef}
        style={{
          width: '100%',
          height: '450px',
          background: 'rgba(6, 11, 23, 0.5)',
          borderRadius: '12px',
          border: '1px solid rgba(99, 160, 255, 0.08)',
          cursor: 'grab',
        }}
      />

      {/* Control Buttons */}
      <div style={{ position: 'absolute', top: 12, right: 12, display: 'flex', gap: 6 }}>
        <button
          onClick={resetZoom}
          style={{
            padding: '6px 12px',
            borderRadius: 6,
            background: 'rgba(13, 21, 40, 0.85)',
            border: '1px solid rgba(99, 160, 255, 0.15)',
            color: '#8BA4C8',
            fontSize: 12,
            fontWeight: 600,
            cursor: 'pointer',
            backdropFilter: 'blur(10px)',
          }}
        >
          Reset View
        </button>
      </div>

      {/* Selected Element Details Overlay Card */}
      {selectedElement && (
        <div
          className="glass-card"
          style={{
            marginTop: 16,
            padding: '16px 20px',
            background: 'rgba(13, 21, 40, 0.95)',
            borderLeft: `4px solid ${selectedElement.type === 'node' ? selectedElement.data.riskColor : '#4F8EF7'}`,
          }}
        >
          {selectedElement.type === 'node' ? (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: 11, fontWeight: 700, background: selectedElement.data.riskColor + '1C', color: selectedElement.data.riskColor, padding: '2px 8px', borderRadius: 4 }}>
                  {selectedElement.data.riskLevel} RISK
                </span>
                <span style={{ fontSize: 12, color: '#4A6080', fontWeight: 600 }}>Tier {selectedElement.data.tier} Supplier</span>
              </div>
              <h4 style={{ color: '#E8F0FF', fontSize: 16, fontWeight: 700 }}>
                {selectedElement.data.name} ({selectedElement.data.ticker})
              </h4>
              <div style={{ display: 'flex', gap: 16, marginTop: 8, fontSize: 13, color: '#8BA4C8' }}>
                <span>💼 {selectedElement.data.sector}</span>
                <span>🌍 {selectedElement.data.country}</span>
                {selectedElement.data.market_cap && (
                  <span>💰 ${(selectedElement.data.market_cap / 1e9).toFixed(1)}B</span>
                )}
              </div>
            </div>
          ) : (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: 11, fontWeight: 700, background: 'rgba(79, 142, 247, 0.1)', color: '#4F8EF7', padding: '2px 8px', borderRadius: 4, textTransform: 'uppercase' }}>
                  {selectedElement.data.contract_type}
                </span>
                <span style={{ fontSize: 12, color: '#4A6080', fontWeight: 600 }}>Supply Connection</span>
              </div>
              <h4 style={{ color: '#E8F0FF', fontSize: 15, fontWeight: 700 }}>
                {selectedElement.data.source} ➔ {selectedElement.data.target}
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginTop: 10 }}>
                <div>
                  <div style={{ fontSize: 10, color: '#4A6080', fontWeight: 600, textTransform: 'uppercase' }}>Product Supplied</div>
                  <div style={{ fontSize: 13, color: '#C8D8F0', fontWeight: 600, marginTop: 2 }}>{selectedElement.data.product}</div>
                </div>
                <div>
                  <div style={{ fontSize: 10, color: '#4A6080', fontWeight: 600, textTransform: 'uppercase' }}>COGS Share</div>
                  <div style={{ fontSize: 13, color: '#10B981', fontWeight: 700, fontFamily: 'JetBrains Mono', marginTop: 2 }}>
                    {(selectedElement.data.share_of_cogs * 100).toFixed(0)}%
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 10, color: '#4A6080', fontWeight: 600, textTransform: 'uppercase' }}>Confidence</div>
                  <div style={{ fontSize: 13, color: '#22D3EE', fontWeight: 700, fontFamily: 'JetBrains Mono', marginTop: 2 }}>
                    {(selectedElement.data.confidence * 100).toFixed(0)}%
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
