import React, { useState } from 'react';
import { ArbitrageOpportunity } from '../types';
import './ArbitrageTable.css';

interface ArbitrageTableProps {
  opportunities: ArbitrageOpportunity[];
  loading: boolean;
  bankroll: number;
}

const ArbitrageTable: React.FC<ArbitrageTableProps> = ({
  opportunities,
  loading,
  bankroll
}) => {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());

  const toggleRowExpansion = (eventId: string) => {
    setExpandedRows(prev => {
      const newSet = new Set(prev);
      if (newSet.has(eventId)) {
        newSet.delete(eventId);
      } else {
        newSet.add(eventId);
      }
      return newSet;
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const formatDateTime = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      timeZoneName: 'short'
    });
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Scanning for arbitrage opportunities...</p>
      </div>
    );
  }

  if (opportunities.length === 0) {
    return (
      <div className="no-results">
        <p>No arbitrage opportunities found.</p>
        <p>Try adjusting your scan parameters or check back later.</p>
      </div>
    );
  }

  return (
    <div className="arbitrage-table-container">
      <h2>Arbitrage Opportunities ({opportunities.length} found)</h2>
      
      <div className="table-wrapper">
        <table className="arbitrage-table">
          <thead>
            <tr>
              <th>Event</th>
              <th>Market</th>
              <th>ROI</th>
              <th>Total Stake</th>
              <th>Expected Profit</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {opportunities.map((opportunity) => {
              const isExpanded = expandedRows.has(opportunity.event_id);
              
              return (
                <React.Fragment key={opportunity.event_id}>
                  <tr className={`main-row ${isExpanded ? 'expanded' : ''}`}>
                    <td>
                      <div className="event-info">
                        <strong>{opportunity.event_label || opportunity.event_id}</strong>
                        {opportunity.league && (
                          <span className="league">{opportunity.league}</span>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className="market-tag">{opportunity.market}</span>
                    </td>
                    <td>
                      <span className={`roi ${opportunity.roi >= 0.01 ? 'high' : opportunity.roi >= 0.005 ? 'medium' : 'low'}`}>
                        {formatPercentage(opportunity.roi)}
                      </span>
                    </td>
                    <td>{formatCurrency(opportunity.total_stake)}</td>
                    <td>
                      <span className="profit">
                        {formatCurrency(opportunity.expected_profit)}
                      </span>
                    </td>
                    <td>
                      <button
                        className="expand-button"
                        onClick={() => toggleRowExpansion(opportunity.event_id)}
                      >
                        {isExpanded ? 'Hide Details' : 'Show Details'}
                      </button>
                    </td>
                  </tr>
                  
                  {isExpanded && (
                    <tr className="details-row">
                      <td colSpan={6}>
                        <div className="opportunity-details">
                          <div className="details-header">
                            <h4>Betting Instructions</h4>
                            {opportunity.start_time && (
                              <span className="start-time">
                                Event starts: {formatDateTime(opportunity.start_time)}
                              </span>
                            )}
                          </div>
                          
                          <div className="legs-table">
                            <table>
                              <thead>
                                <tr>
                                  <th>Book</th>
                                  <th>Outcome</th>
                                  <th>Odds</th>
                                  <th>Stake</th>
                                  <th>Max Bet</th>
                                  <th>Potential Payout</th>
                                </tr>
                              </thead>
                              <tbody>
                                {opportunity.legs.map((leg, index) => {
                                  const payout = leg.stake * leg.odds_decimal;
                                  
                                  return (
                                    <tr key={index}>
                                      <td>
                                        <span className="book-name">{leg.book}</span>
                                      </td>
                                      <td>{leg.outcome}</td>
                                      <td>{leg.odds_display}</td>
                                      <td>
                                        <span className="stake-amount">
                                          {formatCurrency(leg.stake)}
                                        </span>
                                      </td>
                                      <td>{formatCurrency(leg.max_bet)}</td>
                                      <td>
                                        <span className="payout">
                                          {formatCurrency(payout)}
                                        </span>
                                      </td>
                                    </tr>
                                  );
                                })}
                              </tbody>
                            </table>
                          </div>
                          
                          <div className="summary-stats">
                            <div className="stat">
                              <span className="label">Total Investment:</span>
                              <span className="value">{formatCurrency(opportunity.total_stake)}</span>
                            </div>
                            <div className="stat">
                              <span className="label">Guaranteed Profit:</span>
                              <span className="value profit">
                                {formatCurrency(opportunity.expected_profit)}
                              </span>
                            </div>
                            <div className="stat">
                              <span className="label">ROI:</span>
                              <span className={`value roi ${opportunity.roi >= 0.01 ? 'high' : opportunity.roi >= 0.005 ? 'medium' : 'low'}`}>
                                {formatPercentage(opportunity.roi)}
                              </span>
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ArbitrageTable;