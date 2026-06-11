# F1 Dashboard Project

A modern Formula 1 Dashboard built with React (JSX), Python FastAPI, and advanced F1 analytics.

## Project Structure

```
├── frontend/                    # React JSX + CSS frontend
│   ├── src/
│   │   ├── components/         # Reusable React components
│   │   ├── pages/              # Page components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── styles/             # CSS stylesheets
│   │   ├── App.jsx             # Main app component
│   │   └── main.jsx            # Entry point
│   ├── package.json            # Frontend dependencies
│   ├── vite.config.js          # Vite configuration
│   └── index.html              # HTML template
│
├── backend/                     # Python FastAPI backend
│   ├── app/
│   │   ├── routes/             # API endpoints
│   │   ├── lib/                # Utility libraries
│   │   ├── models.py           # Pydantic models
│   │   └── main.py             # FastAPI app
│   ├── utils/                  # Data processing utilities
│   ├── requirements.txt         # Python dependencies
│   └── run.py                  # Backend startup script
│
└── .env.example                # Environment variables template
```

## Features

### Frontend (JSX + CSS)
- **Responsive Design**: Mobile-first CSS with media queries
- **Pages**:
  - Home: Driver overview and stats
  - Standings: Championship standings table
  - Calendar: Race calendar with dates
  - Predictions: AI-powered race winner predictions
  - Telemetry: Live driver telemetry data
- **Components**:
  - Layout with navigation
  - Driver cards with stats
  - Interactive forms
  - Data tables

### Backend (Python FastAPI)
- **REST API Endpoints**:
  - `/healthz` - Health check
  - `/drivers` - Get drivers list
  - `/standings` - Championship standings
  - `/races` - Race calendar
  - `/predictions/winner` - Race winner predictions
  - `/seasons` - Available seasons
  - `/telemetry` - Driver telemetry data

### Utilities (Python)
- **Data Analytics**: Driver performance analysis
- **ML Models**: Prediction algorithms
- **Statistics**: Race insights and probabilities
- **Weather Analysis**: Weather impact predictions

## Setup

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000` (or `5173` with Vite)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python run.py
```

Backend runs on `http://localhost:8000`

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
LOG_LEVEL=INFO
```

## API Documentation

FastAPI automatically generates OpenAPI docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Technologies

- **Frontend**: React 18, JSX, CSS3, Vite
- **Backend**: Python 3.9+, FastAPI, Pydantic
- **Data Source**: Ergast F1 API
- **Styling**: Modern CSS with gradients and animations

## Development

### Frontend
- Single Page Application (SPA) routing
- Component-based architecture
- Responsive CSS Grid/Flexbox layouts
- API integration with fetch

### Backend
- Async/await with Python asyncio
- Type hints with Pydantic models
- RESTful API design
- CORS enabled for frontend

## License

MIT License
