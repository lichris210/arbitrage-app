from typing import Union, Literal
import logging

logger = logging.getLogger(__name__)

class OddsConverter:
    """Convert between different odds formats"""
    
    @staticmethod
    def to_decimal(odds: Union[float, int, str], 
                   format_type: Literal["american", "fractional", "decimal"] = "american") -> float:
        """Convert any odds format to decimal"""
        
        if format_type == "decimal":
            return float(odds)
        
        elif format_type == "american":
            odds_val = int(odds)
            if odds_val > 0:
                return (odds_val / 100) + 1
            else:
                return (100 / abs(odds_val)) + 1
        
        elif format_type == "fractional":
            if isinstance(odds, str):
                numerator, denominator = map(float, odds.split("/"))
                return (numerator / denominator) + 1
            else:
                return float(odds) + 1
        
        else:
            raise ValueError(f"Unsupported odds format: {format_type}")
    
    @staticmethod
    def to_american(decimal_odds: float) -> int:
        """Convert decimal odds to American format"""
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))
    
    @staticmethod
    def to_fractional(decimal_odds: float) -> str:
        """Convert decimal odds to fractional format"""
        fractional = decimal_odds - 1
        
        # Simplify fraction
        def gcd(a, b):
            while b:
                a, b = b, a % b
            return a
        
        # Convert to fraction
        if fractional == 0:
            return "0/1"
        
        # Handle common fractional odds
        if abs(fractional - 0.5) < 0.01:
            return "1/2"
        elif abs(fractional - 1.0) < 0.01:
            return "1/1"
        elif abs(fractional - 1.5) < 0.01:
            return "3/2"
        elif abs(fractional - 2.0) < 0.01:
            return "2/1"
        elif abs(fractional - 3.0) < 0.01:
            return "3/1"
        else:
            # For other values, find closest simple fraction
            for denominator in range(1, 21):
                numerator = round(fractional * denominator)
                if abs((numerator / denominator) - fractional) < 0.01:
                    common_divisor = gcd(numerator, denominator)
                    return f"{numerator // common_divisor}/{denominator // common_divisor}"
        
        return f"{fractional:.2f}/1"
    
    @staticmethod
    def format_odds(decimal_odds: float, 
                   format_type: Literal["american", "fractional", "decimal"] = "decimal") -> str:
        """Format decimal odds to specified format"""
        
        if format_type == "decimal":
            return f"{decimal_odds:.2f}"
        
        elif format_type == "american":
            american = OddsConverter.to_american(decimal_odds)
            return f"{american:+d}"
        
        elif format_type == "fractional":
            return OddsConverter.to_fractional(decimal_odds)
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    @staticmethod
    def calculate_implied_probability(decimal_odds: float) -> float:
        """Calculate implied probability from decimal odds"""
        return 1.0 / decimal_odds
    
    @staticmethod
    def remove_vig(decimal_odds: List[float]) -> List[float]:
        """Remove vigorish from odds to get true probabilities"""
        implied_probs = [1.0 / odds for odds in decimal_odds]
        total_prob = sum(implied_probs)
        
        # Normalize probabilities
        true_probs = [prob / total_prob for prob in implied_probs]
        
        # Convert back to decimal odds
        return [1.0 / prob for prob in true_probs]