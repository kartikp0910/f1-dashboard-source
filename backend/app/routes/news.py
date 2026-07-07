"""Formula 1 news and technical update feed."""
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get("/news")
async def get_news() -> list[dict[str, Any]]:
    """Return a lightweight update feed for the news hub."""
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "id": "official-latest",
            "type": "News",
            "source": "Formula1.com",
            "title": "Latest Formula 1 news",
            "summary": "Official race previews, driver quotes, analysis, features, and paddock updates.",
            "url": "https://www.formula1.com/en/latest",
            "published_at": now,
            "accent": "#E10600",
        },
        {
            "id": "fia-documents",
            "type": "Race control",
            "source": "FIA documents",
            "title": "Official session documents and decisions",
            "summary": "Stewards decisions, event notes, timing sheets, technical documents, and race-control notices.",
            "url": "https://www.fia.com/documents",
            "published_at": now,
            "accent": "#FFFFFF",
        },
        {
            "id": "technical-tracker",
            "type": "Technical",
            "source": "RaceIQ tracker",
            "title": "Car development watchlist",
            "summary": "Track new front-wing, floor, sidepod, rear-wing, and cooling packages by race weekend.",
            "url": "#garage",
            "published_at": now,
            "accent": "#62D5E8",
        },
        {
            "id": "strategy-brief",
            "type": "Strategy",
            "source": "RaceIQ model",
            "title": "Weekend strategy dashboard",
            "summary": "Combine tyre stints, weather, intervals, and safety-car probability to estimate race windows.",
            "url": "#predict",
            "published_at": now,
            "accent": "#43D17D",
        },
    ]
