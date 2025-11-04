from typing import List, Dict, Any
import asyncio
import logging
import os
from datetime import datetime

from .base_adapter import BaseBookAdapter

logger = logging.getLogger(__name__)

class FanDuelAdapter(BaseBookAdapter):
    """FanDuel sportsbook adapter"""
    
    def __init__(self, cookie: str = None):
        super().__init__(
            name="FanDuel",
            base_url="https://sportsbook.fanduel.com",
            rate_limit={"rps": 0.33, "burst": 1}
        )
        self.cookie = cookie or os.getenv("FD_COOKIE", "")
        
    async def authenticate(self) -> bool:
        """Authenticate with FanDuel"""
        return bool(self.cookie)
    
    async def get_odds(self, markets: List[str], jurisdictions: List[str]) -> List[Dict[str, Any]]:
        """Fetch odds from FanDuel"""
        
        await asyncio.sleep(0.5)  # Rate limiting
        
        mock_odds = self._generate_mock_odds(markets)
        return mock_odds
    
    def _generate_mock_odds(self, markets: List[str]) -> List[Dict[str, Any]]:
        """Generate mock odds data for FanDuel"""
        
        mock_events = [
            {
                "event_id": "nba_001",
                "event_label": "Lakers vs Warriors",
                "league": "NBA",
                "start_time": "2025-11-05T20:00:00Z",
                "participants": ["Los Angeles Lakers", "Golden State Warriors"]
            },
            {
                "event_id": "nfl_001",
                "event_label": "Cowboys vs Chiefs", 
                "league": "NFL",
                "start_time": "2025-11-06T18:00:00Z",
                "participants": ["Dallas Cowboys", "Kansas City Chiefs"]
            }
        ]
        
        odds_data = []
        
        for event in mock_events:
            if "moneyline" in markets:
                if event["league"] == "NBA":
                    # Slightly different odds to create arbitrage opportunities
                    odds_data.append(self.create_odds_item(
                        event, "moneyline", event["participants"][0], -145, "american", 750.0
                    ))
                    odds_data.append(self.create_odds_item(
                        event, "moneyline", event["participants"][1], +125, "american", 750.0
                    ))
                elif event["league"] == "NFL":
                    odds_data.append(self.create_odds_item(
                        event, "moneyline", event["participants"][0], +110, "american", 1200.0
                    ))
                    odds_data.append(self.create_odds_item(
                        event, "moneyline", event["participants"][1], -130, "american", 1200.0
                    ))
            
            if "spread" in markets:
                if event["league"] == "NBA":
                    odds_data.append(self.create_odds_item(
                        event, "spread", f"{event['participants'][0]} -3.5", -105, "american", 750.0
                    ))
                    odds_data.append(self.create_odds_item(
                        event, "spread", f"{event['participants'][1]} +3.5", -115, "american", 750.0
                    ))
        
        return odds_data