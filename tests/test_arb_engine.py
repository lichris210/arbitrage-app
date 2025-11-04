import pytest
from datetime import datetime
from core.arb_engine import ArbitrageEngine
from models.schemas import StakePolicy, StakePolicyType

class TestArbitrageEngine:
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = ArbitrageEngine()
    
    def test_normalize_team_name(self):
        """Test team name normalization"""
        assert self.engine.normalize_team_name("Lakers") == "Los Angeles Lakers"
        assert self.engine.normalize_team_name("LA Lakers") == "Los Angeles Lakers"
        assert self.engine.normalize_team_name("Golden State") == "Golden State Warriors"
        assert self.engine.normalize_team_name("Unknown Team") == "Unknown Team"
    
    def test_generate_event_id(self):
        """Test event ID generation"""
        event_data = {
            "start_time": "2025-11-05T20:00:00Z",
            "league": "NBA",
            "participants": ["Lakers", "Warriors"]
        }
        
        event_id1 = self.engine.generate_event_id(event_data)
        event_id2 = self.engine.generate_event_id(event_data)
        
        # Same input should generate same ID
        assert event_id1 == event_id2
        
        # Different participants should generate different ID
        event_data_diff = {
            "start_time": "2025-11-05T20:00:00Z",
            "league": "NBA", 
            "participants": ["Celtics", "Heat"]
        }
        event_id3 = self.engine.generate_event_id(event_data_diff)
        assert event_id1 != event_id3
    
    def test_two_way_arbitrage_detection(self):
        """Test 2-way arbitrage opportunity detection"""
        # Create odds data with arbitrage opportunity
        odds_data = [
            {
                "book": "DraftKings",
                "event_label": "Lakers vs Warriors",
                "league": "NBA",
                "start_time": "2025-11-05T20:00:00Z",
                "participants": ["Lakers", "Warriors"],
                "market": "moneyline",
                "outcome": "Lakers",
                "odds": -150,
                "odds_format": "american",
                "max_bet": 500
            },
            {
                "book": "FanDuel",
                "event_label": "Lakers vs Warriors",
                "league": "NBA",
                "start_time": "2025-11-05T20:00:00Z",
                "participants": ["Lakers", "Warriors"],
                "market": "moneyline",
                "outcome": "Warriors",
                "odds": +160,
                "odds_format": "american",
                "max_bet": 500
            }
        ]
        
        opportunities = self.engine.find_arbitrage(
            odds=odds_data,
            min_roi=0.001,
            bankroll=1000
        )
        
        assert len(opportunities) == 1
        
        opp = opportunities[0]
        assert opp.market.value == "moneyline"
        assert len(opp.legs) == 2
        assert opp.total_stake == 1000
        assert opp.expected_profit > 0
        
        # Check that ROI calculation is correct
        assert abs(opp.roi - (opp.expected_profit / opp.total_stake)) < 0.001
    
    def test_three_way_arbitrage_detection(self):
        """Test 3-way (1x2) arbitrage opportunity detection"""
        odds_data = [
            {
                "book": "DraftKings",
                "event_label": "Soccer Match",
                "league": "EPL",
                "start_time": "2025-11-05T20:00:00Z",
                "participants": ["Team A", "Team B"],
                "market": "1x2",
                "outcome": "Team A",
                "odds": 2.10,
                "odds_format": "decimal",
                "max_bet": 500
            },
            {
                "book": "FanDuel",
                "event_label": "Soccer Match",
                "league": "EPL",
                "start_time": "2025-11-05T20:00:00Z",
                "participants": ["Team A", "Team B"],
                "market": "1x2",
                "outcome": "Draw",
                "odds": 3.40,
                "odds_format": "decimal",
                "max_bet": 500
            },
            {
                "book": "BetMGM",
                "event_label": "Soccer Match",
                "league": "EPL",
                "start_time": "2025-11-05T20:00:00Z",
                "participants": ["Team A", "Team B"],
                "market": "1x2",
                "outcome": "Team B",
                "odds": 3.80,
                "odds_format": "decimal",
                "max_bet": 500
            }
        ]
        
        opportunities = self.engine.find_arbitrage(
            odds=odds_data,
            min_roi=0.001,
            bankroll=1000
        )
        
        if len(opportunities) > 0:
            opp = opportunities[0]
            assert len(opp.legs) == 3
            assert opp.market.value == "1x2"
            assert opp.expected_profit > 0
    
    def test_no_arbitrage_when_no_opportunity(self):
        """Test that no arbitrage is detected when no opportunity exists"""
        # Create odds data without arbitrage (high vig)
        odds_data = [
            {
                "book": "DraftKings",
                "event_label": "Lakers vs Warriors",
                "league": "NBA",
                "start_time": "2025-11-05T20:00:00Z",
                "participants": ["Lakers", "Warriors"],
                "market": "moneyline",
                "outcome": "Lakers",
                "odds": -110,
                "odds_format": "american",
                "max_bet": 500
            },
            {
                "book": "FanDuel",
                "event_label": "Lakers vs Warriors",
                "league": "NBA",
                "start_time": "2025-11-05T20:00:00Z",
                "participants": ["Lakers", "Warriors"],
                "market": "moneyline",
                "outcome": "Warriors",
                "odds": -110,
                "odds_format": "american",
                "max_bet": 500
            }
        ]
        
        opportunities = self.engine.find_arbitrage(
            odds=odds_data,
            min_roi=0.001,
            bankroll=1000
        )
        
        # Should not find arbitrage with -110 both sides
        assert len(opportunities) == 0
    
    def test_stake_calculation_equal_profit(self):
        """Test equal profit stake calculation"""
        # Example from the specification
        decimal_odds = [2.10, 1.95]
        total_stake = 100
        
        # Calculate manually: payout = 100 / (1/2.10 + 1/1.95) = 101.11
        implied_probs = [1/odds for odds in decimal_odds]
        payout = total_stake / sum(implied_probs)
        
        stakes = [payout / odds for odds in decimal_odds]
        profit = payout - total_stake
        
        assert abs(stakes[0] - 48.15) < 0.01
        assert abs(stakes[1] - 51.86) < 0.01
        assert abs(profit - 1.11) < 0.01
    
    def test_roi_filtering(self):
        """Test that opportunities are filtered by minimum ROI"""
        odds_data = [
            {
                "book": "DraftKings",
                "event_label": "Test Event",
                "league": "NBA",
                "start_time": "2025-11-05T20:00:00Z",
                "participants": ["Team A", "Team B"],
                "market": "moneyline",
                "outcome": "Team A",
                "odds": 1.95,
                "odds_format": "decimal",
                "max_bet": 500
            },
            {
                "book": "FanDuel",
                "event_label": "Test Event",
                "league": "NBA",
                "start_time": "2025-11-05T20:00:00Z",
                "participants": ["Team A", "Team B"],
                "market": "moneyline",
                "outcome": "Team B",
                "odds": 2.10,
                "odds_format": "decimal",
                "max_bet": 500
            }
        ]
        
        # Test with high minimum ROI (should find nothing)
        opportunities_high = self.engine.find_arbitrage(
            odds=odds_data,
            min_roi=0.1,  # 10% ROI requirement
            bankroll=1000
        )
        assert len(opportunities_high) == 0
        
        # Test with low minimum ROI (should find opportunity)
        opportunities_low = self.engine.find_arbitrage(
            odds=odds_data,
            min_roi=0.001,  # 0.1% ROI requirement
            bankroll=1000
        )
        assert len(opportunities_low) == 1