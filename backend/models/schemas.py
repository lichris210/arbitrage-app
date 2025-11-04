from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any, Literal
from datetime import datetime
from enum import Enum

class MarketType(str, Enum):
    MONEYLINE = "moneyline"
    SPREAD = "spread"
    TOTAL = "total"
    ONE_X_TWO = "1x2"

class StakePolicyType(str, Enum):
    EQUAL_PROFIT = "equal_profit"
    KELLY = "kelly"

class BankrollPolicy(BaseModel):
    type: str
    budget: float

class StakePolicy(BaseModel):
    type: StakePolicyType
    min_bet: float = 1.0
    max_bet_per_book: float = 500.0

class ScanRequest(BaseModel):
    books: List[str]
    markets: List[MarketType]
    jurisdictions: List[str]
    bankroll: Optional[float] = 1000.0

class ArbRequest(BaseModel):
    books: List[str]
    markets: List[MarketType]
    jurisdictions: List[str]
    min_roi: float = 0.006
    max_slippage: float = 0.004
    bankroll: float = 1000.0
    stake_policy: StakePolicy = StakePolicy(type=StakePolicyType.EQUAL_PROFIT)

class QuoteRequest(BaseModel):
    odds_data: List[Dict[str, Any]]
    bankroll: float
    stake_policy: StakePolicy = StakePolicy(type=StakePolicyType.EQUAL_PROFIT)
    max_slippage: float = 0.004

class ArbLeg(BaseModel):
    book: str
    outcome: str
    odds_decimal: float = Field(gt=1.0)
    odds_display: str
    stake: float = Field(ge=0)
    max_bet: float = Field(ge=0)
    notes: Optional[str] = None

class ArbitrageOpportunity(BaseModel):
    event_id: str
    league: Optional[str] = None
    event_label: Optional[str] = None
    start_time: Optional[str] = Field(None, format="date-time")
    market: MarketType
    roi: float
    total_stake: float = Field(ge=0)
    expected_profit: float
    legs: List[ArbLeg]

class ArbQuoteSchema(BaseModel):
    generated_at: str = Field(format="date-time")
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    bankroll_input: float = Field(ge=0)
    opportunities: List[ArbitrageOpportunity]

    @validator('opportunities')
    def validate_opportunities(cls, v):
        for opp in v:
            if len(opp.legs) < 2:
                raise ValueError("Each opportunity must have at least 2 legs")
        return v