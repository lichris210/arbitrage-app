import React, { useState, useEffect } from 'react';
import './App.css';
import ArbitrageTable from './components/ArbitrageTable';
import ScanControls from './components/ScanControls';
import { ArbitrageOpportunity, ScanRequest } from './types';

const API_BASE = 'http://localhost:8000';

function App() {
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [bankroll, setBankroll] = useState(1000);

  const handleScan = async (scanRequest: ScanRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/arbs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...scanRequest,
          bankroll,
          min_roi: 0.006,
          max_slippage: 0.004,
          stake_policy: { type: 'equal_profit', min_bet: 1, max_bet_per_book: 500 }
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch arbitrage opportunities');
      }

      const data = await response.json();
      setOpportunities(data.opportunities);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleHealthCheck = async () => {
    try {
      const response = await fetch(`${API_BASE}/health`);
      if (!response.ok) {
        throw new Error('Health check failed');
      }
      const data = await response.json();
      console.log('API Health:', data);
    } catch (err) {
      console.error('Health check error:', err);
    }
  };

  useEffect(() => {
    handleHealthCheck();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Arbitrage Betting Scanner</h1>
        <p>Find risk-free betting opportunities across multiple sportsbooks</p>
      </header>

      <main className="App-main">
        <ScanControls 
          onScan={handleScan} 
          loading={loading}
          bankroll={bankroll}
          onBankrollChange={setBankroll}
        />
        
        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
          </div>
        )}

        <ArbitrageTable 
          opportunities={opportunities} 
          loading={loading}
          bankroll={bankroll}
        />
      </main>
    </div>
  );
}

export default App;