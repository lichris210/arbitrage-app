from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import hashlib
import json

from models.schemas import ArbitrageOpportunity, ArbLeg, MarketType, StakePolicy
from core.odds_converter import OddsConverter

logger = logging.getLogger(__name__)

class ArbitrageEngine:
    def __init__(self):
        self.odds_converter = OddsConverter()
        self.team_aliases = self._load_team_aliases()
        
    def _load_team_aliases(self) -> Dict[str, List[str]]:
        """Load team name aliases for normalization"""
        return {
            "Los Angeles Lakers": ["Lakers", "LA Lakers", "LAL"],
            "Golden State Warriors": ["Warriors", "Golden State", "GSW"],
            "Brooklyn Nets": ["Nets", "Brooklyn", "BKN"],
            "New York Knicks": ["Knicks", "New York", "NYK"],
            "Boston Celtics": ["Celtics", "Boston", "BOS"],
            "Miami Heat": ["Heat", "Miami", "MIA"],
            "Dallas Cowboys": ["Cowboys", "Dallas", "DAL"],
            "Kansas City Chiefs": ["Chiefs", "Kansas City", "KC"],
            "Philadelphia Eagles": ["Eagles", "Philadelphia", "PHI"],
            "San Francisco 49ers": ["49ers", "San Francisco", "SF"],
            "New York Yankees": ["Yankees", "NY Yankees", "NYY"],
            "Los Angeles Dodgers": ["Dodgers", "LA Dodgers", "LAD"],
        }
    
    def normalize_team_name(self, team_name: str) -> str:
        """Normalize team names across different sportsbooks"""
        team_name = team_name.strip()
        
        for canonical, aliases in self.team_aliases.items():
            if team_name == canonical or team_name in aliases:
                return canonical
        
        return team_name
    
    def generate_event_id(self, event_data: Dict[str, Any]) -> str:
        """Generate unique event ID based on participants and start time"""
        key_data = {
            "start_time": event_data.get("start_time"),
            "league": event_data.get("league", ""),
            "participants": sorted([
                self.normalize_team_name(p) 
                for p in event_data.get("participants", [])
            ])
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()[:12]
    
    def normalize_events(self, odds_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize and deduplicate events across sportsbooks"""
        events_map = {}
        
        for odds_item in odds_data:
            event_id = self.generate_event_id(odds_item)
            
            if event_id not in events_map:
                events_map[event_id] = {
                    "event_id": event_id,
                    "event_label": odds_item.get("event_label", ""),
                    "league": odds_item.get("league", ""),
                    "start_time": odds_item.get("start_time"),
                    "participants": [self.normalize_team_name(p) for p in odds_item.get("participants", [])],
                    "markets": {}
                }
            
            market = odds_item.get("market")
            book = odds_item.get("book")
            
            if market not in events_map[event_id]["markets"]:
                events_map[event_id]["markets"][market] = []
            
            # Convert odds to decimal format
            odds_decimal = self.odds_converter.to_decimal(odds_item.get("odds"), odds_item.get("odds_format", "american"))
            
            events_map[event_id]["markets"][market].append({
                "book": book,
                "outcome": odds_item.get("outcome"),
                "odds": odds_decimal,
                "odds_display": self.odds_converter.format_odds(odds_decimal, "decimal"),
                "max_bet": odds_item.get("max_bet", 500.0)
            })
        
        return list(events_map.values())
    
    def find_arbitrage(self, odds: List[Dict[str, Any]], min_roi: float = 0.006, 
                      max_slippage: float = 0.004, bankroll: float = 1000.0,
                      stake_policy: Optional[StakePolicy] = None) -> List[ArbitrageOpportunity]:
        """Find arbitrage opportunities in the odds data"""
        
        normalized_events = self.normalize_events(odds)
        opportunities = []
        
        for event in normalized_events:
            for market, market_odds in event["markets"].items():
                arb_opportunity = self._check_market_arbitrage(
                    event, market, market_odds, min_roi, max_slippage, 
                    bankroll, stake_policy
                )
                
                if arb_opportunity:
                    opportunities.append(arb_opportunity)
        
        # Sort by ROI descending
        opportunities.sort(key=lambda x: x.roi, reverse=True)
        return opportunities
    
    def _check_market_arbitrage(self, event: Dict[str, Any], market: str, 
                               market_odds: List[Dict[str, Any]], min_roi: float,
                               max_slippage: float, bankroll: float, 
                               stake_policy: Optional[StakePolicy]) -> Optional[ArbitrageOpportunity]:
        """Check if a specific market has arbitrage opportunity"""
        
        # Group by outcome
        outcomes = {}
        for odds_item in market_odds:
            outcome = odds_item["outcome"]
            if outcome not in outcomes:
                outcomes[outcome] = []
            outcomes[outcome].append(odds_item)
        
        # Find best odds for each outcome
        best_odds = {}
        for outcome, odds_list in outcomes.items():
            best_odds[outcome] = max(odds_list, key=lambda x: x["odds"])
        
        # Calculate arbitrage condition
        if len(best_odds) < 2:
            return None
        
        implied_prob_sum = sum(1.0 / odds["odds"] for odds in best_odds.values())
        
        if implied_prob_sum >= (1.0 - min_roi):
            return None
        
        # Calculate stakes and profit
        total_stake = bankroll
        payout = total_stake / implied_prob_sum
        profit = payout - total_stake
        roi = profit / total_stake
        
        if roi < min_roi:
            return None
        
        # Create legs with calculated stakes
        legs = []
        for outcome, odds_item in best_odds.items():
            stake = payout / odds_item["odds"]
            
            legs.append(ArbLeg(
                book=odds_item["book"],
                outcome=outcome,
                odds_decimal=odds_item["odds"],
                odds_display=odds_item["odds_display"],
                stake=stake,
                max_bet=odds_item.get("max_bet", 500.0),
                notes="Arbitrage opportunity detected"
            ))
        
        return ArbitrageOpportunity(
            event_id=event["event_id"],
            league=event.get("league"),
            event_label=event.get("event_label"),
            start_time=event.get("start_time"),
            market=MarketType(market),
            roi=roi,
            total_stake=total_stake,
            expected_profit=profit,
            legs=legs
        )
    
    def calculate_stakes_for_odds(self, odds_data: List[Dict[str, Any]], 
                                 bankroll: float, stake_policy: Optional[StakePolicy] = None,
                                 max_slippage: float = 0.004) -> List[ArbitrageOpportunity]:
        """Calculate stakes for given odds data"""
        
        # This is a simplified version - in production, you'd implement
        # more sophisticated stake calculation including Kelly criterion
        return self.find_arbitrage(
            odds=odds_data,
            bankroll=bankroll,
            stake_policy=stake_policy,
            max_slippage=max_slippage
        )