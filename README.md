# RaceIQ F1 Dashboard

A premium Formula 1 race intelligence dashboard built with React, Vite, FastAPI, Pydantic, and FastF1.

The app is designed around one rule: current/live screens use current FastF1 data, while past race data is reserved for prediction and historical analysis.

## What It Does

- Shows current-season race calendar from FastF1.
- Shows current driver standings and constructor summaries.
- Shows a Race Center that checks whether a race is currently live.
- Displays "uh oh you are early by" with a countdown when no race is happening.
- Loads FastF1 race-session packets for live telemetry/track data when a race is active.
- Keeps historical/past data for prediction logic and previous race analysis.
- Includes premium frontend pages for Race Center, driver profiles, constructor garage, predictions, telemetry, standings, calendar, and news.

## Tech Stack

### Frontend

- React 18
- Vite
- JSX
- CSS animations and responsive layouts

### Backend

- Python
- FastAPI
- Pydantic
- FastF1
- httpx
- Uvicorn

## Project Structure

```text
f1-dashboard-source/
  backend/
    app/
      lib/
        fastf1_provider.py      # FastF1 current/live data provider
        demo_data.py            # Prediction/demo fallback helpers
        f1_api.py               # Jolpica/Ergast helper used by prediction flow
      routes/
        live.py                 # /live/track
        races.py                # /races and /races/previous-results
        standings.py            # /standings
        drivers.py              # /drivers
        profiles.py             # /drivers/profiles
        constructors.py          # /constructors/specs
        telemetry.py            # /telemetry
        predictions.py           # /predictions/winner
        news.py                  # /news
        health.py                # /healthz
      main.py
      models.py
    requirements.txt
    run.py

  frontend/
    src/
      pages/
        Home.jsx
        RaceCenter.jsx
        DriverProfiles.jsx
        Garage.jsx
        Predict.jsx
        Telemetry.jsx
        Standings.jsx
        Calendar.jsx
        RaceDetail.jsx
        NewsHub.jsx
      components/
        Layout.jsx
      lib/
        liveData.js
      styles/
        index.css
        layout.css
        pages.css
    package.json
    vite.config.js
```

## Pages

- `/#home` - dashboard overview
- `/#race-center` - current race state, live track data, or next-race countdown
- `/#drivers` - current driver profiles and form
- `/#garage` - constructor specs, standings-derived team cards, and 3D-style car upgrade viewer
- `/#predict` - race winner prediction model
- `/#telemetry` - current live telemetry when a race is active
- `/#standings` - current driver standings
- `/#calendar` - current race calendar
- `/#news` - F1 update links and dashboard update cards

## Data Behavior

### Current/Live Data

These routes use FastF1 current-season/session data:

- `/races`
- `/standings`
- `/drivers`
- `/drivers/profiles`
- `/constructors/specs`
- `/telemetry`
- `/live/track`

When no race is active, `/live/track` returns:

```json
{
  "mode": "no-live-race",
  "provider": "fastf1",
  "is_live": false,
  "provider_warning": "FastF1 current schedule shows no active race session."
}
```

The frontend then shows:

```text
uh oh you are early by
[countdown to next race]
```

### Historical Data

Past data is used for:

- `/races/previous-results`
- `/predictions/winner`
- prediction factors such as form, circuit history, race results, qualifying, safety car probability, and weather assumptions

## API Endpoints

```text
GET  /healthz
GET  /races
GET  /races/previous-results
GET  /standings
GET  /drivers
GET  /drivers/profiles
GET  /constructors/specs
GET  /telemetry
GET  /live/track
GET  /seasons
GET  /news
POST /predictions/winner
```

FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

## Setup

### 1. Backend

From the project root:

```powershell
cd C:\Users\KIIT0001\Desktop\f1-dashboard-source
.\.venv\Scripts\activate
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
cd backend
python run.py
```

Backend runs on:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/healthz
```

### 2. Frontend

Open a second terminal:

```powershell
cd C:\Users\KIIT0001\Desktop\f1-dashboard-source\frontend
npm install
npm run dev -- --host 127.0.0.1
```

Frontend runs on:

```text
http://127.0.0.1:4173/
```

## Build

```powershell
cd C:\Users\KIIT0001\Desktop\f1-dashboard-source\frontend
npm run build
```

The production output is written to:

```text
frontend/dist/
```

## Environment Variables

Optional `.env` values:

```env
LOG_LEVEL=INFO
F1_API_VERIFY_SSL=false
API_TIMEOUT=15
MAX_RETRIES=3
```

`F1_API_VERIFY_SSL=false` is useful on Windows systems where FastF1/Jolpica requests fail because the local certificate store cannot validate the provider certificate chain.

## FastF1 Notes

- FastF1 can load current race schedule, standings, race results, telemetry, weather, race-control messages, and session data.
- Live track data is only available when a race session is actually active and FastF1 has current packets.
- If no race is active, Race Center intentionally shows the next-race countdown instead of fake live cars.
- FastF1 may cache data under `backend/.fastf1-cache/`.

## Verification Commands

```powershell
python -m compileall backend
cd frontend
npm run build
```

Useful endpoint checks:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/healthz
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/races
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/standings
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/live/track
```

## Resume Highlights

- Built a full-stack Formula 1 race intelligence platform with React, Vite, FastAPI, and FastF1.
- Implemented current-season schedule, standings, constructor summaries, driver profiles, race-state detection, telemetry gating, and prediction endpoints.
- Designed a premium F1-style frontend with animated dashboard panels, Race Center countdown, driver cards, constructor garage, and 3D-style car upgrade viewer.
- Separated current/live data from historical prediction data to avoid showing stale race results as live information.

