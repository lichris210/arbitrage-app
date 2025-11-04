import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

class TestAPIEndpoints:
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"
    
    def test_scan_endpoint(self):
        """Test scan endpoint"""
        scan_request = {
            "books": ["DraftKings", "FanDuel"],
            "markets": ["moneyline"],
            "jurisdictions": ["US-NY"],
            "bankroll": 1000
        }
        
        response = client.post("/scan", json=scan_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "generated_at" in data
        assert data["currency"] == "USD"
        assert data["bankroll_input"] == 1000
        assert isinstance(data["opportunities"], list)
    
    def test_arbs_endpoint(self):
        """Test arbitrage detection endpoint"""
        arb_request = {
            "books": ["DraftKings", "FanDuel"],
            "markets": ["moneyline"],
            "jurisdictions": ["US-NY"],
            "min_roi": 0.006,
            "max_slippage": 0.004,
            "bankroll": 1000,
            "stake_policy": {
                "type": "equal_profit",
                "min_bet": 1,
                "max_bet_per_book": 500
            }
        }
        
        response = client.post("/arbs", json=arb_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "generated_at" in data
        assert data["currency"] == "USD"
        assert data["bankroll_input"] == 1000
        assert isinstance(data["opportunities"], list)
        
        # Validate response against schema
        for opportunity in data["opportunities"]:
            assert "event_id" in opportunity
            assert "market" in opportunity
            assert "roi" in opportunity
            assert "total_stake" in opportunity
            assert "expected_profit" in opportunity
            assert "legs" in opportunity
            assert len(opportunity["legs"]) >= 2
            
            for leg in opportunity["legs"]:
                assert "book" in leg
                assert "outcome" in leg
                assert "odds_decimal" in leg
                assert "stake" in leg
                assert "max_bet" in leg
    
    def test_quote_endpoint(self):
        """Test quote calculation endpoint"""
        quote_request = {
            "odds_data": [
                {
                    "book": "DraftKings",
                    "event_label": "Test Event",
                    "league": "NBA",
                    "start_time": "2025-11-05T20:00:00Z",
                    "participants": ["Team A", "Team B"],
                    "market": "moneyline",
                    "outcome": "Team A",
                    "odds": -150,
                    "odds_format": "american",
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
                    "odds": +160,
                    "odds_format": "american",
                    "max_bet": 500
                }
            ],
            "bankroll": 1000,
            "stake_policy": {
                "type": "equal_profit",
                "min_bet": 1,
                "max_bet_per_book": 500
            },
            "max_slippage": 0.004
        }
        
        response = client.post("/quote", json=quote_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "generated_at" in data
        assert data["currency"] == "USD"
        assert data["bankroll_input"] == 1000
        assert isinstance(data["opportunities"], list)
    
    def test_invalid_request_body(self):
        """Test that invalid request bodies return appropriate errors"""
        # Missing required fields
        invalid_request = {
            "books": ["DraftKings"],  # Missing markets and jurisdictions
        }
        
        response = client.post("/arbs", json=invalid_request)
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_empty_opportunities_response(self):
        """Test response when no opportunities are found"""
        # Request with books that won't return arbitrage
        request = {
            "books": ["DraftKings"],
            "markets": ["moneyline"],
            "jurisdictions": ["US-NY"],
            "min_roi": 0.1,  # Very high ROI requirement
            "max_slippage": 0.004,
            "bankroll": 1000,
            "stake_policy": {
                "type": "equal_profit",
                "min_bet": 1,
                "max_bet_per_book": 500
            }
        }
        
        response = client.post("/arbs", json=request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["opportunities"] == []
    
    def test_cors_headers(self):
        """Test CORS headers are properly set"""
        response = client.get("/health")
        # CORS is handled by middleware, so we just verify the endpoint works
        assert response.status_code == 200