from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaseBookAdapter(ABC):
    """Base class for sportsbook adapters"""
    
    def __init__(self, name: str, base_url: str, rate_limit: Dict[str, float]):
        self.name = name
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.session = None
        
    @abstractmethod
    async def get_odds(self, markets: List[str], jurisdictions: List[str]) -> List[Dict[str, Any]]:
        """Fetch odds data from the sportsbook"""
        pass
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the sportsbook"""
        pass
    
    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
    
    def create_odds_item(self, event_data: Dict[str, Any], market: str, 
                        outcome: str, odds: float, odds_format: str = "american",
                        max_bet: float = 500.0) -> Dict[str, Any]:
        """Create standardized odds item"""
        return {
            "book": self.name,
            "event_id": event_data.get("event_id", ""),
            "event_label": event_data.get("event_label", ""),
            "league": event_data.get("league", ""),
            "start_time": event_data.get("start_time", ""),
            "participants": event_data.get("participants", []),
            "market": market,
            "outcome": outcome,
            "odds": odds,
            "odds_format": odds_format,
            "max_bet": max_bet,
            "timestamp": datetime.utcnow().isoformat()
        }