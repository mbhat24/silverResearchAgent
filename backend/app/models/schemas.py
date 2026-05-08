from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SilverPrice(BaseModel):
    symbol: str
    price: float
    currency: str
    unit: str
    change_24h: float
    change_pct_24h: float
    high_24h: float
    low_24h: float
    timestamp: datetime
    source: str


class SilverPriceIndia(BaseModel):
    price_per_gram: float
    price_per_kg: float
    mcx_future_price: Optional[float] = None
    mcx_expiry: Optional[str] = None
    local_premium_pct: Optional[float] = None
    import_duty_pct: float = 15.0
    currency: str = "INR"
    timestamp: datetime
    source: str


class HistoricalData(BaseModel):
    symbol: str
    data: list[dict]  # [{date, open, high, low, close, volume}]
    period: str


class ResearchReport(BaseModel):
    id: str
    title: str
    summary: str
    sections: list[dict]
    key_findings: list[str]
    sentiment: str  # bullish, bearish, neutral
    price_targets: dict
    risk_factors: list[str]
    generated_at: datetime
    data_sources: list[str]


class NewsItem(BaseModel):
    title: str
    source: str
    url: str
    published_at: datetime
    summary: str
    sentiment: Optional[str] = None
    relevance_score: float = 1.0


class SupplyDemand(BaseModel):
    global_mine_production: Optional[float] = None  # tonnes
    global_recycling: Optional[float] = None
    industrial_demand: Optional[float] = None
    jewelry_demand: Optional[float] = None
    investment_demand: Optional[float] = None
    india_imports: Optional[float] = None  # tonnes
    india_demand: Optional[float] = None
    year: int
    source: str


class DashboardData(BaseModel):
    live_prices: list[SilverPrice]
    india_prices: SilverPriceIndia
    recent_news: list[NewsItem]
    latest_report: Optional[ResearchReport] = None
    supply_demand: Optional[SupplyDemand] = None
    technical_summary: dict
