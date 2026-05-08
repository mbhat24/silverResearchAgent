# SilverSage - AI-Powered Silver Research Agent

A comprehensive full-stack application for tracking silver markets worldwide and in India, featuring AI-powered research, real-time pricing, technical analysis, and news aggregation.

## Features

### Backend API (FastAPI)
- **Live Price Tracking**: XAG/USD, COMEX futures, INR prices
- **India-Specific Data**: MCX futures, local premiums, import duties
- **Technical Indicators**: RSI, MACD, SMA, trend analysis, support/resistance
- **Historical Data**: Price charts with multiple timeframes (1W to 5Y)
- **AI Research Agent**: GPT-4o powered market analysis (6 report types)
- **News Aggregation**: Global and Indian silver news sources
- **Supply-Demand Fundamentals**: Global production, recycling, demand metrics

### Frontend Dashboard (React)
- **Professional Dark Theme**: Glassmorphism design with TailwindCSS
- **5 Tabbed Views**: Overview, India Market, AI Research, News, Fundamentals
- **Interactive Charts**: Recharts-powered price visualizations
- **Real-Time Updates**: Auto-refresh every 30 seconds
- **Responsive Design**: Mobile-friendly interface
- **Live Price Ticker**: Scrolling price display

## Architecture

```
silver-research-agent/
├── backend/
│   ├── app/
│   │   ├── api/routes.py          # API endpoints
│   │   ├── agents/research_agent.py # AI research engine
│   │   ├── services/
│   │   │   ├── silver_data.py      # Price/technical data
│   │   │   └── news_service.py     # News aggregation
│   │   ├── models/schemas.py       # Pydantic models
│   │   ├── config.py               # Settings
│   │   └── main.py                 # FastAPI app
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── App.jsx                 # Main app
│   │   ├── main.jsx                # Entry point
│   │   └── index.css               # Tailwind styles
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── render.yaml                     # Render deployment config
└── README.md
```

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key (optional, for AI reports)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
uvicorn app.main:app --reload
```

API runs on `http://localhost:8000`
- Interactive docs: `http://localhost:8000/api/docs`
- Health check: `http://localhost:8000/api/health`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` (proxies API to backend)

## Deployment on Render

### Quick Deploy

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click "New +" → "New Web Service"
3. Connect GitHub repo: `mbhat24/silverResearchAgent`
4. Render auto-detects `render.yaml` and configures both services
5. Add environment variable for API service:
   - `OPENAI_API_KEY` = your OpenAI key (optional)
6. Deploy

### Render Services

After deployment, you'll have two services:

| Service | URL | Purpose |
|---------|-----|---------|
| API | `https://silver-research-agent-api.onrender.com` | Backend API |
| Frontend | `https://silver-research-agent-frontend.onrender.com` | React dashboard |

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Optional | OpenAI API key for AI research reports |
| `PYTHON_VERSION` | Auto | Python version (3.11) |

**Note**: The app works without `OPENAI_API_KEY` — AI reports will show a setup message, but all other features (live prices, charts, news, technicals) work fully.

## API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard` | All dashboard data in one call |
| GET | `/api/prices/live` | Live silver prices (all sources) |
| GET | `/api/prices/india` | India-specific silver prices |
| GET | `/api/prices/historical?symbol=XAGUSD=X&period=1y` | Historical price data |
| GET | `/api/technical` | Technical indicators |
| GET | `/api/supply-demand` | Supply-demand fundamentals |
| GET | `/api/news?limit=20` | Latest silver news |
| GET | `/api/research/report?topic=comprehensive` | AI research report |
| POST | `/api/research/ask` | Ask specific question |
| GET | `/api/health` | Health check |

### Research Report Topics

- `comprehensive` — Full market analysis
- `india` — India-specific analysis
- `technical` — Technical analysis
- `fundamental` — Fundamental analysis
- `macro` — Macroeconomic factors
- `predictions` — Price predictions

## Data Sources

### Price Data
- Yahoo Finance (XAG/USD, COMEX futures)
- MCX India (estimates)
- Derived INR prices

### News Sources
- Kitco
- BullionVault
- SilverDoctors
- Investing.com
- Economic Times (India)
- Moneycontrol (India)

### Supply-Demand
- Silver Institute estimates
- Compiled annual data

## Troubleshooting

### Backend Issues

**CORS errors**: Ensure frontend proxy is configured in `vite.config.js`

**Missing data**: Check `yfinance` is installed and network access is available

**AI reports failing**: Verify `OPENAI_API_KEY` is set correctly in `.env`

### Frontend Issues

**Build errors**: Run `npm install` to ensure dependencies are installed

**API connection**: Ensure backend is running on port 8000 or update API_BASE in `App.jsx`

**Charts not rendering**: Verify `recharts` is installed

### Render Issues

**Build failures**: Check build logs in Render dashboard

**Environment variables**: Ensure `OPENAI_API_KEY` is set for the API service

**Service not starting**: Verify start command in `render.yaml`

## Development

### Adding New Components

```bash
cd frontend/src/components
# Create new component
# Import and use in App.jsx
```

### Adding New API Endpoints

```python
# backend/app/api/routes.py
@router.get("/your-endpoint")
async def your_endpoint():
    # Your logic
    return {"data": "result"}
```

## License

MIT

## Credits

- Built with FastAPI, React, TailwindCSS
- Data from Yahoo Finance, Silver Institute, news aggregators
- AI powered by OpenAI GPT-4o