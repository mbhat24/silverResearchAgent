from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from ..services.silver_data import SilverDataService
from ..services.news_service import NewsService
from ..agents.research_agent import ResearchAgent
from ..models.schemas import DashboardData

router = APIRouter(prefix="/api")

silver_service = SilverDataService()
news_service = NewsService()
research_agent = ResearchAgent()


@router.get("/dashboard")
async def get_dashboard() -> DashboardData:
    """Get all dashboard data in one call."""
    live_prices = await silver_service.get_live_prices()
    india_prices = await silver_service.get_india_prices()
    news = await news_service.fetch_news(limit=10)
    supply_demand = await silver_service.get_supply_demand()
    technical = await silver_service.get_technical_indicators()

    return DashboardData(
        live_prices=live_prices,
        india_prices=india_prices,
        recent_news=news,
        latest_report=None,
        supply_demand=supply_demand,
        technical_summary=technical
    )


@router.get("/prices/live")
async def get_live_prices():
    """Get live silver prices from all sources."""
    return await silver_service.get_live_prices()


@router.get("/prices/india")
async def get_india_prices():
    """Get India-specific silver prices."""
    return await silver_service.get_india_prices()


@router.get("/prices/historical")
async def get_historical(
    symbol: str = Query("XAGUSD=X", description="Ticker symbol"),
    period: str = Query("1y", description="Period: 1mo, 3mo, 6mo, 1y, 2y, 5y, max")
):
    """Get historical silver price data."""
    return await silver_service.get_historical_data(symbol, period)


@router.get("/technical")
async def get_technical(symbol: str = "XAGUSD=X"):
    """Get technical indicators for silver."""
    return await silver_service.get_technical_indicators(symbol)


@router.get("/supply-demand")
async def get_supply_demand():
    """Get silver supply-demand fundamentals."""
    return await silver_service.get_supply_demand()


@router.get("/news")
async def get_news(limit: int = 20, query: Optional[str] = None):
    """Get latest silver news."""
    if query:
        return await news_service.search_news(query)
    return await news_service.fetch_news(limit)


@router.get("/research/report")
async def generate_report(
    topic: str = Query("comprehensive",
                       description="comprehensive, india, technical, fundamental, macro, predictions")
):
    """Generate an AI-powered research report."""
    valid_topics = ["comprehensive", "india", "technical", "fundamental", "macro", "predictions"]
    if topic not in valid_topics:
        raise HTTPException(400, f"Invalid topic. Choose from: {valid_topics}")

    market_data = {
        "prices": [p.model_dump() for p in await silver_service.get_live_prices()],
        "india": (await silver_service.get_india_prices()).model_dump(),
        "technical": await silver_service.get_technical_indicators(),
        "supply_demand": (await silver_service.get_supply_demand()).model_dump()
    }

    news = await news_service.fetch_news(limit=15)
    news_data = [n.model_dump() for n in news]

    return await research_agent.generate_report(topic, market_data, news_data)


@router.post("/research/ask")
async def ask_question(query: str):
    """Ask a specific question about silver markets."""
    market_data = {
        "prices": [p.model_dump() for p in await silver_service.get_live_prices()],
        "technical": await silver_service.get_technical_indicators()
    }
    return await research_agent.answer_query(query, market_data)


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "Silver Research Agent"}
