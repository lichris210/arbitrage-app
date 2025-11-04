import React, { useState } from 'react';
import { ScanRequest } from '../types';
import './ScanControls.css';

interface ScanControlsProps {
  onScan: (request: ScanRequest) => void;
  loading: boolean;
  bankroll: number;
  onBankrollChange: (value: number) => void;
}

const AVAILABLE_BOOKS = [
  'DraftKings', 'FanDuel', 'BetMGM', 'Caesars', 
  'bet365', 'BetRivers', 'Fanatics Sportsbook'
];

const AVAILABLE_MARKETS = [
  { value: 'moneyline', label: 'Moneyline' },
  { value: 'spread', label: 'Spread' },
  { value: 'total', label: 'Total' },
  { value: '1x2', label: '1X2' }
];

const JURISDICTIONS = [
  'US-CO', 'US-NJ', 'US-PA', 'US-OH', 'US-VA', 
  'US-NY', 'US-MI', 'US-AZ', 'US-MD'
];

const ScanControls: React.FC<ScanControlsProps> = ({
  onScan,
  loading,
  bankroll,
  onBankrollChange
}) => {
  const [selectedBooks, setSelectedBooks] = useState<string[]>(['DraftKings', 'FanDuel']);
  const [selectedMarkets, setSelectedMarkets] = useState<string[]>(['moneyline']);
  const [selectedJurisdictions, setSelectedJurisdictions] = useState<string[]>(['US-NY']);

  const handleBookToggle = (book: string) => {
    setSelectedBooks(prev => 
      prev.includes(book) 
        ? prev.filter(b => b !== book)
        : [...prev, book]
    );
  };

  const handleMarketToggle = (market: string) => {
    setSelectedMarkets(prev => 
      prev.includes(market) 
        ? prev.filter(m => m !== market)
        : [...prev, market]
    );
  };

  const handleJurisdictionToggle = (jurisdiction: string) => {
    setSelectedJurisdictions(prev => 
      prev.includes(jurisdiction) 
        ? prev.filter(j => j !== jurisdiction)
        : [...prev, jurisdiction]
    );
  };

  const handleScan = () => {
    if (selectedBooks.length === 0 || selectedMarkets.length === 0 || selectedJurisdictions.length === 0) {
      alert('Please select at least one book, market, and jurisdiction');
      return;
    }

    onScan({
      books: selectedBooks,
      markets: selectedMarkets as any,
      jurisdictions: selectedJurisdictions
    });
  };

  return (
    <div className="scan-controls">
      <div className="control-group">
        <h3>Bankroll</h3>
        <input
          type="number"
          value={bankroll}
          onChange={(e) => onBankrollChange(Number(e.target.value))}
          min="100"
          max="100000"
          step="100"
        />
        <span className="currency">USD</span>
      </div>

      <div className="control-group">
        <h3>Sportsbooks</h3>
        <div className="checkbox-group">
          {AVAILABLE_BOOKS.map(book => (
            <label key={book} className="checkbox-label">
              <input
                type="checkbox"
                checked={selectedBooks.includes(book)}
                onChange={() => handleBookToggle(book)}
              />
              <span>{book}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="control-group">
        <h3>Markets</h3>
        <div className="checkbox-group">
          {AVAILABLE_MARKETS.map(market => (
            <label key={market.value} className="checkbox-label">
              <input
                type="checkbox"
                checked={selectedMarkets.includes(market.value)}
                onChange={() => handleMarketToggle(market.value)}
              />
              <span>{market.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="control-group">
        <h3>Jurisdictions</h3>
        <div className="checkbox-group">
          {JURISDICTIONS.map(jurisdiction => (
            <label key={jurisdiction} className="checkbox-label">
              <input
                type="checkbox"
                checked={selectedJurisdictions.includes(jurisdiction)}
                onChange={() => handleJurisdictionToggle(jurisdiction)}
              />
              <span>{jurisdiction}</span>
            </label>
          ))}
        </div>
      </div>

      <button
        className="scan-button"
        onClick={handleScan}
        disabled={loading || selectedBooks.length === 0 || selectedMarkets.length === 0}
      >
        {loading ? 'Scanning...' : 'Scan for Arbitrage'}
      </button>
    </div>
  );
};

export default ScanControls;