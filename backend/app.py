from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import os
import logging
from contextlib import asynccontextmanager

from core.arb_engine import ArbitrageEngine
from core.odds_converter import OddsConverter
from adapters.book_factory import BookAdapterFactory
from models.schemas import ArbQuoteSchema, ScanRequest, ArbRequest, QuoteRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
arb_engine = None
book_factory = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global arb_engine, book_factory
    arb_engine = ArbitrageEngine()
    book_factory = BookAdapterFactory()
    yield
    # Cleanup
    if book_factory:
        await book_factory.cleanup()

app = FastAPI(
    title="Arbitrage Betting API",
    description="Sports betting arbitrage detection and stake calculation service",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.post("/scan", response_model=ArbQuoteSchema)
async def scan_odds(request: ScanRequest):
    """Scan sportsbooks for current odds"""
    try:
        books = await book_factory.get_adapters(request.books)
        all_odds = []
        
        for book in books:
            try:
                odds = await book.get_odds(request.markets, request.jurisdictions)
                all_odds.extend(odds)
            except Exception as e:
                logger.error(f"Error fetching odds from {book.name}: {e}")
                continue
        
        # Normalize and deduplicate events
        normalized_odds = arb_engine.normalize_events(all_odds)
        
        return ArbQuoteSchema(
            generated_at=datetime.utcnow().isoformat(),
            currency="USD",
            bankroll_input=request.bankroll or 1000,
            opportunities=[]  # Raw scan doesn't compute arbs
        )
    
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        raise HTTPException(status_code=500, detail="Scan failed")

@app.post("/arbs", response_model=ArbQuoteSchema)
async def find_arbitrage(request: ArbRequest):
    """Find arbitrage opportunities and calculate stakes"""
    try:
        # Get odds from specified books
        books = await book_factory.get_adapters(request.books)
        all_odds = []
        
        for book in books:
            try:
                odds = await book.get_odds(request.markets, request.jurisdictions)
                all_odds.extend(odds)
            except Exception as e:
                logger.error(f"Error fetching odds from {book.name}: {e}")
                continue
        
        # Find arbitrage opportunities
        opportunities = arb_engine.find_arbitrage(
            odds=all_odds,
            min_roi=request.min_roi,
            max_slippage=request.max_slippage,
            bankroll=request.bankroll,
            stake_policy=request.stake_policy
        )
        
        return ArbQuoteSchema(
            generated_at=datetime.utcnow().isoformat(),
            currency="USD",
            bankroll_input=request.bankroll,
            opportunities=opportunities
        )
    
    except Exception as e:
        logger.error(f"Arbitrage calculation failed: {e}")
        raise HTTPException(status_code=500, detail="Arbitrage calculation failed")

@app.post("/quote", response_model=ArbQuoteSchema)
async def calculate_stakes(request: QuoteRequest):
    """Recalculate stakes for given odds and budget"""
    try:
        opportunities = arb_engine.calculate_stakes_for_odds(
            odds_data=request.odds_data,
            bankroll=request.bankroll,
            stake_policy=request.stake_policy,
            max_slippage=request.max_slippage
        )
        
        return ArbQuoteSchema(
            generated_at=datetime.utcnow().isoformat(),
            currency="USD",
            bankroll_input=request.bankroll,
            opportunities=opportunities
        )
    
    except Exception as e:
        logger.error(f"Quote calculation failed: {e}")
        raise HTTPException(status_code=500, detail="Quote calculation failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)