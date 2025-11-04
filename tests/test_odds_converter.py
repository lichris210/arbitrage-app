import pytest
from core.odds_converter import OddsConverter

class TestOddsConverter:
    
    def test_american_to_decimal_positive(self):
        """Test conversion of positive American odds to decimal"""
        assert OddsConverter.to_decimal(150, "american") == 2.50
        assert OddsConverter.to_decimal(200, "american") == 3.00
        assert OddsConverter.to_decimal(100, "american") == 2.00
        
    def test_american_to_decimal_negative(self):
        """Test conversion of negative American odds to decimal"""
        assert OddsConverter.to_decimal(-150, "american") == 1.6666666666666667
        assert OddsConverter.to_decimal(-200, "american") == 1.50
        assert OddsConverter.to_decimal(-100, "american") == 2.00
    
    def test_decimal_to_american(self):
        """Test conversion of decimal odds to American"""
        assert OddsConverter.to_american(2.50) == 150
        assert OddsConverter.to_american(3.00) == 200
        assert OddsConverter.to_american(1.6666666666666667) == -150
        assert OddsConverter.to_american(1.50) == -200
    
    def test_fractional_to_decimal(self):
        """Test conversion of fractional odds to decimal"""
        assert OddsConverter.to_decimal("1/2", "fractional") == 1.50
        assert OddsConverter.to_decimal("1/1", "fractional") == 2.00
        assert OddsConverter.to_decimal("3/1", "fractional") == 4.00
        assert OddsConverter.to_decimal("5/2", "fractional") == 3.50
    
    def test_decimal_to_fractional(self):
        """Test conversion of decimal odds to fractional"""
        assert OddsConverter.to_fractional(1.50) == "1/2"
        assert OddsConverter.to_fractional(2.00) == "1/1"
        assert OddsConverter.to_fractional(4.00) == "3/1"
        assert OddsConverter.to_fractional(3.50) == "5/2"
    
    def test_implied_probability(self):
        """Test implied probability calculation"""
        assert OddsConverter.calculate_implied_probability(2.00) == 0.50
        assert OddsConverter.calculate_implied_probability(1.50) == 0.6666666666666666
        assert OddsConverter.calculate_implied_probability(3.00) == 0.3333333333333333
    
    def test_remove_vig(self):
        """Test vigorish removal from odds"""
        # Test case: Two-way market with 4.5% vig
        odds = [1.91, 1.91]  # Standard -110 odds
        true_odds = OddsConverter.remove_vig(odds)
        
        # Sum of implied probabilities should be 1.0 after vig removal
        implied_probs = [OddsConverter.calculate_implied_probability(odd) for odd in true_odds]
        assert abs(sum(implied_probs) - 1.0) < 0.001
    
    def test_format_odds(self):
        """Test odds formatting in different formats"""
        decimal_odds = 2.50
        
        assert OddsConverter.format_odds(decimal_odds, "decimal") == "2.50"
        assert OddsConverter.format_odds(decimal_odds, "american") == "+150"
        assert OddsConverter.format_odds(decimal_odds, "fractional") == "3/2"
        
        # Test negative American odds
        assert OddsConverter.format_odds(1.6666666666666667, "american") == "-150"
    
    def test_round_trip_conversion(self):
        """Test that American -> Decimal -> American conversion is accurate"""
        test_odds = [150, -150, 200, -200, 100, -100]
        
        for american_odds in test_odds:
            decimal = OddsConverter.to_decimal(american_odds, "american")
            back_to_american = OddsConverter.to_american(decimal)
            assert back_to_american == american_odds