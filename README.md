# Arbitrage Betting Scanner

A comprehensive web application for scanning multiple sportsbooks to find risk-free arbitrage betting opportunities. Built with FastAPI backend and React frontend.

## Features

- **Multi-Book Scanning**: Supports DraftKings, FanDuel, BetMGM, Caesars, bet365, BetRivers, and Fanatics Sportsbook
- **Arbitrage Detection**: Automatically identifies risk-free betting opportunities across different sportsbooks
- **Stake Calculation**: Calculates optimal stake amounts for equalized profit
- **Rate Limiting**: Respects sportsbook API limits with intelligent rate limiting
- **Real-time Updates**: Live scanning and updating of odds data
- **Dark Theme UI**: Modern, responsive interface optimized for extended use

## Architecture

```
├── backend/                 # FastAPI backend service
│   ├── app.py              # Main FastAPI application
│   ├── core/               # Core business logic
│   │   ├── arb_engine.py   # Arbitrage detection engine
│   │   └── odds_converter.py # Odds conversion utilities
│   ├── adapters/           # Sportsbook API adapters
│   │   ├── base_adapter.py # Base adapter class
│   │   ├── draftkings_adapter.py # DraftKings adapter
│   │   └── fanduel_adapter.py    # FanDuel adapter
│   ├── models/             # Pydantic models and schemas
│   └── utils/              # Utility functions
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── types.ts        # TypeScript type definitions
│   │   └── App.tsx         # Main React application
│   └── package.json        # Frontend dependencies
├── tests/                  # Comprehensive test suite
└── docs/                   # Documentation
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Redis (optional, for rate limiting)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd arbitrage-app
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install -r ../requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your sportsbook credentials
   ```

5. **Run the application**
   
   Backend:
   ```bash
   cd backend
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```
   
   Frontend:
   ```bash
   cd frontend
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure the following:

```bash
# Sportsbook Session Cookies (required for live data)
DK_COOKIE=your_draftkings_session_cookie
FD_COOKIE=your_fanduel_session_cookie
# ... add other sportsbook cookies

# Application Settings
LOG_LEVEL=INFO
REDIS_URL=redis://localhost:6379

# Security (always keep these true for safety)
DISABLE_AUTO_BET=true
ALLOW_ONLY_READ=true
```

### Sportsbook Setup

**Important**: This application requires active session cookies from each sportsbook. To obtain these:

1. Log in to each sportsbook website
2. Open browser developer tools (F12)
3. Navigate to the Application/Storage tab
4. Find Cookies section and copy the session cookie
5. Add to your `.env` file

**Note**: Cookies expire periodically and will need to be refreshed.

## API Endpoints

### Health Check
```http
GET /health
```

### Scan for Arbitrage Opportunities
```http
POST /arbs
Content-Type: application/json

{
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
```

### Calculate Stakes for Given Odds
```http
POST /quote
Content-Type: application/json

{
  "odds_data": [...],
  "bankroll": 1000,
  "stake_policy": {...},
  "max_slippage": 0.004
}
```

## Usage Guide

### Finding Arbitrage Opportunities

1. **Set your bankroll**: Enter the total amount you want to invest
2. **Select sportsbooks**: Choose which books to scan (minimum 2)
3. **Choose markets**: Select which betting markets to analyze
4. **Pick jurisdictions**: Select your legal betting jurisdiction
5. **Click "Scan for Arbitrage"**: The system will analyze odds and find opportunities

### Understanding the Results

The results table shows:
- **Event**: The sporting event with arbitrage opportunity
- **Market**: Type of bet (moneyline, spread, total, etc.)
- **ROI**: Return on investment percentage
- **Total Stake**: Total amount to bet across all books
- **Expected Profit**: Guaranteed profit amount

Click "Show Details" to see:
- Specific betting instructions for each book
- Individual stake amounts
- Potential payouts
- Maximum bet limits

### Example Arbitrage Calculation

Given two-way market with decimal odds 2.10 and 1.95, with $100 total stake:

- Payout = $100 / (1/2.10 + 1/1.95) = $101.11
- Stake on 2.10 odds = $101.11 / 2.10 = $48.15
- Stake on 1.95 odds = $101.11 / 1.95 = $51.86
- Profit = $101.11 - $100 = $1.11

## Testing

Run the comprehensive test suite:

```bash
# Backend tests
cd backend
pytest ../tests -v --cov=core --cov=adapters --cov=models

# Frontend tests (if available)
cd frontend
npm test
```

## Adding New Sportsbooks

To add a new sportsbook adapter:

1. Create a new adapter in `backend/adapters/`:
```python
from .base_adapter import BaseBookAdapter

class NewBookAdapter(BaseBookAdapter):
    def __init__(self, cookie: str = None):
        super().__init__(
            name="NewBook",
            base_url="https://sportsbook.newbook.com",
            rate_limit={"rps": 0.33, "burst": 1}
        )
        self.cookie = cookie or os.getenv("NEWBOOK_COOKIE", "")
    
    async def authenticate(self) -> bool:
        return bool(self.cookie)
    
    async def get_odds(self, markets: List[str], jurisdictions: List[str]) -> List[Dict[str, Any]]:
        # Implement odds fetching logic
        pass
```

2. Register the adapter in `backend/adapters/book_factory.py`

3. Add environment variable to `.env.example`

## Compliance and Safety

### Important Legal Notice

- **Educational Purpose**: This software is for educational and research purposes only
- **Terms of Service**: Users must comply with each sportsbook's terms of service
- **Legal Compliance**: Only use in jurisdictions where sports betting is legal
- **Age Restrictions**: Users must be of legal gambling age in their jurisdiction

### Safety Features

- **Read-Only Mode**: Default configuration prevents automatic betting
- **Rate Limiting**: Respects sportsbook API limits to avoid bans
- **Session Management**: Secure handling of authentication cookies
- **No Auto-Betting**: Manual confirmation required for all bets

### Best Practices

1. **Start Small**: Begin with small stakes to test the system
2. **Monitor Limits**: Be aware of betting limits at each sportsbook
3. **Act Quickly**: Arbitrage opportunities disappear as odds change
4. **Track Performance**: Keep detailed records of all transactions
5. **Stay Informed**: Monitor changes in sportsbook terms and conditions

## Troubleshooting

### Common Issues

**No opportunities found**: 
- Check that sportsbook cookies are valid
- Try different markets or sportsbooks
- Lower minimum ROI threshold

**Authentication failures**:
- Verify sportsbook cookies are current
- Check that accounts are active and verified
- Ensure cookies haven't expired

**Rate limiting errors**:
- Reduce scan frequency
- Check sportsbook API limits
- Verify Redis is running (if using Redis rate limiting)

### Getting Help

- Check the API documentation at `/docs`
- Review logs for specific error messages
- Test individual components with unit tests
- Verify environment configuration

## Development

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy

# Run code formatting
black backend/

# Run type checking
mypy backend/

# Run linting
flake8 backend/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is provided "as is" without warranty of any kind. Users assume all responsibility for compliance with local laws and regulations. The authors are not responsible for any financial losses or legal issues resulting from the use of this software.

**Always gamble responsibly and within your means.**