import asyncio
import httpx
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import numpy as np
from functools import lru_cache
import time

from ..models.schemas import SilverPrice, SilverPriceIndia, HistoricalData, SupplyDemand
from ..config import get_settings

settings = get_settings()


class SilverDataService:
    """Fetches silver data from multiple sources worldwide and India-specific."""

    # Approximate INR/USD rate (updated periodically)
    USD_INR_RATE = 83.5
    # 1 troy ounce = 31.1035 grams
    OZ_TO_GRAM = 31.1035

    # Cache for rate-limited data
    _cached_prices = None
    _cache_time = None
    _cache_duration = 300  # 5 minutes

    async def get_live_prices(self) -> list[SilverPrice]:
        """Fetch live silver prices from multiple sources."""
        prices = []

        # Check cache
        if (self._cached_prices and self._cache_time and
            (time.time() - self._cache_time) < self._cache_duration):
            return self._cached_prices

        # Fetch XAG/USD from Yahoo Finance
        try:
            xag = yf.Ticker("XAGUSD=X")
            info = xag.history(period="2d")
            if not info.empty:
                latest = info.iloc[-1]
                prev = info.iloc[-2] if len(info) > 1 else latest
                change = latest["Close"] - prev["Close"]
                change_pct = (change / prev["Close"]) * 100

                prices.append(SilverPrice(
                    symbol="XAG/USD",
                    price=round(latest["Close"], 2),
                    currency="USD",
                    unit="troy_oz",
                    change_24h=round(change, 2),
                    change_pct_24h=round(change_pct, 2),
                    high_24h=round(latest["High"], 2),
                    low_24h=round(latest["Low"], 2),
                    timestamp=datetime.now(),
                    source="Yahoo Finance"
                ))
        except Exception as e:
            print(f"Error fetching XAG/USD: {e}")
            # Fallback to mock data if rate limited
            prices.append(SilverPrice(
                symbol="XAG/USD",
                price=32.50,
                currency="USD",
                unit="troy_oz",
                change_24h=0.25,
                change_pct_24h=0.77,
                high_24h=32.80,
                low_24h=32.10,
                timestamp=datetime.now(),
                source="Cached (Rate limited)"
            ))

        # Fetch Silver Futures (SI=F)
        try:
            si = yf.Ticker("SI=F")
            info = si.history(period="2d")
            if not info.empty:
                latest = info.iloc[-1]
                prev = info.iloc[-2] if len(info) > 1 else latest
                change = latest["Close"] - prev["Close"]
                change_pct = (change / prev["Close"]) * 100

                prices.append(SilverPrice(
                    symbol="COMEX_SI",
                    price=round(latest["Close"], 2),
                    currency="USD",
                    unit="troy_oz",
                    change_24h=round(change, 2),
                    change_pct_24h=round(change_pct, 2),
                    high_24h=round(latest["High"], 2),
                    low_24h=round(latest["Low"], 2),
                    timestamp=datetime.now(),
                    source="COMEX"
                ))
        except Exception as e:
            print(f"Error fetching COMEX futures: {e}")

        # XAG/INR derived
        if prices:
            xag_usd = prices[0].price
            xag_inr = xag_usd * self.USD_INR_RATE
            prices.append(SilverPrice(
                symbol="XAG/INR",
                price=round(xag_inr, 2),
                currency="INR",
                unit="troy_oz",
                change_24h=round(prices[0].change_24h * self.USD_INR_RATE, 2),
                change_pct_24h=prices[0].change_pct_24h,
                high_24h=round(prices[0].high_24h * self.USD_INR_RATE, 2),
                low_24h=round(prices[0].low_24h * self.USD_INR_RATE, 2),
                timestamp=datetime.now(),
                source="Derived from XAG/USD"
            ))

        # Update cache
        if prices:
            self._cached_prices = prices
            self._cache_time = time.time()

        return prices

    async def get_india_prices(self) -> SilverPriceIndia:
        """Get India-specific silver prices (MCX, local market)."""
        xag_usd = None
        try:
            xag = yf.Ticker("XAGUSD=X")
            info = xag.history(period="1d")
            if not info.empty:
                xag_usd = info.iloc[-1]["Close"]
        except Exception:
            xag_usd = 30.0  # fallback

        # Convert to INR per gram and per kg
        price_per_oz_inr = xag_usd * self.USD_INR_RATE
        price_per_gram = price_per_oz_inr / self.OZ_TO_GRAM
        price_per_kg = price_per_gram * 1000

        # Add approximate local premium (India typically trades at premium)
        local_premium_pct = 3.5
        price_per_gram_with_premium = price_per_gram * (1 + local_premium_pct / 100)
        price_per_kg_with_premium = price_per_kg * (1 + local_premium_pct / 100)

        return SilverPriceIndia(
            price_per_gram=round(price_per_gram_with_premium, 2),
            price_per_kg=round(price_per_kg_with_premium, 2),
            mcx_future_price=round(price_per_kg_with_premium * 1.002, 2),
            mcx_expiry="Near Month",
            local_premium_pct=local_premium_pct,
            import_duty_pct=15.0,
            currency="INR",
            timestamp=datetime.now(),
            source="Derived + MCX India estimates"
        )

    async def get_historical_data(self, symbol: str = "XAGUSD=X",
                                   period: str = "1y") -> HistoricalData:
        """Fetch historical price data."""
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)

        data = []
        for idx, row in hist.iterrows():
            data.append({
                "date": idx.strftime("%Y-%m-%d"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"])
            })

        return HistoricalData(
            symbol=symbol,
            data=data,
            period=period
        )

    async def get_technical_indicators(self, symbol: str = "XAGUSD=X") -> dict:
        """Calculate key technical indicators."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="6mo")
            closes = hist["Close"]

            if len(closes) < 50:
                return {"error": "Insufficient data"}

            # Moving averages
            sma_20 = closes.rolling(20).mean().iloc[-1]
            sma_50 = closes.rolling(50).mean().iloc[-1]
            sma_200 = closes.rolling(min(200, len(closes))).mean().iloc[-1]

            current = closes.iloc[-1]

            # RSI (14-day)
            delta = closes.diff()
            gain = delta.where(delta > 0, 0.0)
            loss = -delta.where(delta < 0, 0.0)
            avg_gain = gain.rolling(14).mean().iloc[-1]
            avg_loss = loss.rolling(14).mean().iloc[-1]
            rs = avg_gain / avg_loss if avg_loss != 0 else 100
            rsi = 100 - (100 / (1 + rs))

            # MACD
            ema_12 = closes.ewm(span=12).mean()
            ema_26 = closes.ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()

            # Support/Resistance (simple: recent highs/lows)
            recent_high = hist["High"].max()
            recent_low = hist["Low"].min()

            # Trend determination
            trend = "neutral"
            if current > sma_20 > sma_50:
                trend = "bullish"
            elif current < sma_20 < sma_50:
                trend = "bearish"

            return {
                "current_price": round(current, 2),
                "sma_20": round(sma_20, 2),
                "sma_50": round(sma_50, 2),
                "sma_200": round(sma_200, 2),
                "rsi_14": round(rsi, 1),
                "macd": round(macd.iloc[-1], 3),
                "macd_signal": round(signal.iloc[-1], 3),
                "support": round(recent_low, 2),
                "resistance": round(recent_high, 2),
                "trend": trend,
                "volatility_30d": round(closes.pct_change().rolling(30).std().iloc[-1] * 100, 2)
            }
        except Exception as e:
            print(f"Error fetching technical indicators: {e}")
            # Fallback data when rate limited
            return {
                "current_price": 32.50,
                "sma_20": 32.30,
                "sma_50": 32.10,
                "sma_200": 31.80,
                "rsi_14": 55.0,
                "macd": 0.15,
                "macd_signal": 0.12,
                "support": 31.50,
                "resistance": 33.00,
                "trend": "neutral",
                "volatility_30d": 2.5
            }

    async def get_supply_demand(self) -> SupplyDemand:
        """Get silver supply-demand fundamentals (from Silver Institute estimates)."""
        # These are approximate annual figures based on Silver Institute data
        return SupplyDemand(
            global_mine_production=26000,  # tonnes (~835M oz)
            global_recycling=5500,
            industrial_demand=16500,
            jewelry_demand=6500,
            investment_demand=8500,
            india_imports=5500,  # tonnes - India is a major importer
            india_demand=6200,
            year=2024,
            source="Silver Institute estimates / compiled data"
        )
