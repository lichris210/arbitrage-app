# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Git

## Installation Steps

### 1. Clone and Navigate
```bash
cd /mnt/okcomputer/output/arbitrage-app
```

### 2. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
cd ..
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your sportsbook cookies (optional for demo)
```

### 5. Run Tests (Optional)
```bash
python run_tests.py
```

### 6. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 7. Access the Application

- **Frontend**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Demo Mode

The application includes mock data for demonstration purposes. No real sportsbook authentication is required to see the arbitrage detection in action.

## What You Get

✅ **Complete arbitrage betting web application**  
✅ **FastAPI backend with 3 core endpoints**  
✅ **React frontend with dark theme**  
✅ **Real-time arbitrage detection engine**  
✅ **Odds conversion utilities**  
✅ **Sportsbook adapters with rate limiting**  
✅ **Comprehensive test suite**  
✅ **Full documentation and setup guides**  

## Next Steps

1. **Configure Real Sportsbook Access**: Add your session cookies to `.env`
2. **Customize Settings**: Adjust minimum ROI, bankroll, and stake policies
3. **Add More Sportsbooks**: Implement additional book adapters
4. **Deploy**: Use Docker or cloud deployment for production

## Support

- Check `/docs` endpoint for API documentation
- Review `README.md` for detailed usage instructions
- Run tests with `python run_tests.py`