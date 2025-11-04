import pytest
from pydantic import ValidationError
from models.schemas import (
    ArbQuoteSchema, ArbitrageOpportunity, ArbLeg, 
    MarketType, StakePolicy, StakePolicyType
)

class TestSchemas:
    
    def test_valid_arb_leg(self):
        """Test valid arbitrage leg creation"""
        leg = ArbLeg(
            book="DraftKings",
            outcome="Lakers",
            odds_decimal=2.50,
            odds_display="+150",
            stake=100.0,
            max_bet=500.0
        )
        
        assert leg.book == "DraftKings"
        assert leg.odds_decimal == 2.50
        assert leg.stake == 100.0
    
    def test_invalid_arb_leg_odds(self):
        """Test that odds must be greater than 1"""
        with pytest.raises(ValidationError):
            ArbLeg(
                book="DraftKings",
                outcome="Lakers",
                odds_decimal=0.5,  # Invalid odds
                odds_display="Invalid",
                stake=100.0,
                max_bet=500.0
            )
    
    def test_invalid_arb_leg_stake(self):
        """Test that stake cannot be negative"""
        with pytest.raises(ValidationError):
            ArbLeg(
                book="DraftKings",
                outcome="Lakers",
                odds_decimal=2.50,
                odds_display="+150",
                stake=-100.0,  # Invalid stake
                max_bet=500.0
            )
    
    def test_valid_arbitrage_opportunity(self):
        """Test valid arbitrage opportunity creation"""
        legs = [
            ArbLeg(
                book="DraftKings",
                outcome="Lakers",
                odds_decimal=2.50,
                odds_display="+150",
                stake=400.0,
                max_bet=500.0
            ),
            ArbLeg(
                book="FanDuel",
                outcome="Warriors",
                odds_decimal=1.95,
                odds_display="-105",
                stake=600.0,
                max_bet=500.0
            )
        ]
        
        opportunity = ArbitrageOpportunity(
            event_id="test_event_001",
            market=MarketType.MONEYLINE,
            roi=0.006,
            total_stake=1000.0,
            expected_profit=6.0,
            legs=legs
        )
        
        assert opportunity.event_id == "test_event_001"
        assert opportunity.market == MarketType.MONEYLINE
        assert len(opportunity.legs) == 2
        assert opportunity.total_stake == 1000.0
    
    def test_arbitrage_opportunity_insufficient_legs(self):
        """Test that arbitrage opportunity requires at least 2 legs"""
        with pytest.raises(ValidationError):
            ArbitrageOpportunity(
                event_id="test_event_001",
                market=MarketType.MONEYLINE,
                roi=0.006,
                total_stake=1000.0,
                expected_profit=6.0,
                legs=[  # Only 1 leg
                    ArbLeg(
                        book="DraftKings",
                        outcome="Lakers",
                        odds_decimal=2.50,
                        odds_display="+150",
                        stake=1000.0,
                        max_bet=500.0
                    )
                ]
            )
    
    def test_valid_arb_quote_schema(self):
        """Test valid arbitrage quote schema"""
        legs = [
            ArbLeg(
                book="DraftKings",
                outcome="Lakers",
                odds_decimal=2.50,
                odds_display="+150",
                stake=400.0,
                max_bet=500.0
            ),
            ArbLeg(
                book="FanDuel",
                outcome="Warriors",
                odds_decimal=1.95,
                odds_display="-105",
                stake=600.0,
                max_bet=500.0
            )
        ]
        
        opportunity = ArbitrageOpportunity(
            event_id="test_event_001",
            market=MarketType.MONEYLINE,
            roi=0.006,
            total_stake=1000.0,
            expected_profit=6.0,
            legs=legs
        )
        
        quote = ArbQuoteSchema(
            generated_at="2025-11-05T20:00:00Z",
            currency="USD",
            bankroll_input=1000.0,
            opportunities=[opportunity]
        )
        
        assert quote.currency == "USD"
        assert quote.bankroll_input == 1000.0
        assert len(quote.opportunities) == 1
    
    def test_invalid_currency_format(self):
        """Test that currency must be 3 uppercase letters"""
        with pytest.raises(ValidationError):
            ArbQuoteSchema(
                generated_at="2025-11-05T20:00:00Z",
                currency="US",  # Invalid - only 2 letters
                bankroll_input=1000.0,
                opportunities=[]
            )
        
        with pytest.raises(ValidationError):
            ArbQuoteSchema(
                generated_at="2025-11-05T20:00:00Z",
                currency="usd",  # Invalid - lowercase
                bankroll_input=1000.0,
                opportunities=[]
            )
    
    def test_stake_policy_creation(self):
        """Test stake policy creation"""
        policy = StakePolicy(
            type=StakePolicyType.EQUAL_PROFIT,
            min_bet=10.0,
            max_bet_per_book=1000.0
        )
        
        assert policy.type == StakePolicyType.EQUAL_PROFIT
        assert policy.min_bet == 10.0
        assert policy.max_bet_per_book == 1000.0
    
    def test_market_type_validation(self):
        """Test market type validation"""
        # Valid market types
        assert MarketType.MONEYLINE.value == "moneyline"
        assert MarketType.SPREAD.value == "spread"
        assert MarketType.TOTAL.value == "total"
        assert MarketType.ONE_X_TWO.value == "1x2"
        
        # Invalid market type should raise error
        with pytest.raises(ValueError):
            MarketType("invalid_market")