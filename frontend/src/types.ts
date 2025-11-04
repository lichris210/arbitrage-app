export interface ArbLeg {
  book: string;
  outcome: string;
  odds_decimal: number;
  odds_display: string;
  stake: number;
  max_bet: number;
  notes?: string;
}

export interface ArbitrageOpportunity {
  event_id: string;
  league?: string;
  event_label?: string;
  start_time?: string;
  market: 'moneyline' | 'spread' | 'total' | '1x2';
  roi: number;
  total_stake: number;
  expected_profit: number;
  legs: ArbLeg[];
}

export interface ScanRequest {
  books: string[];
  markets: ('moneyline' | 'spread' | 'total' | '1x2')[];
  jurisdictions: string[];
}

export interface ArbQuoteSchema {
  generated_at: string;
  currency: string;
  bankroll_input: number;
  opportunities: ArbitrageOpportunity[];
}