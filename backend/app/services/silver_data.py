import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import numpy as np
from functools import lru_cache
import time
import json
import sys

from fastapi import HTTPException

from ..models.schemas import SilverPrice, SilverPriceIndia, HistoricalData, SupplyDemand
from ..config import get_settings

settings = get_settings()

KG_TO_TROY_OZ = 32.1507


def _yf_fetch_sync(symbol: str, period: str = "2d", interval: str = "1d") -> dict:
    """Fetch from Yahoo Finance using curl_cffi browser impersonation."""
    from curl_cffi import requests as curl_requests
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={period}&includePrePost=false"
    resp = curl_requests.get(url, impersonate="chrome120")
    resp.raise_for_status()
    result = resp.json()
    return result["chart"]["result"][0]


class SilverDataService:
    """Fetches silver data from multiple sources worldwide and India-specific."""

    _cached_prices = None
    _cache_time = None
    _cache_duration = 300
    _usd_inr_rate = None

    async def _get_usd_inr_rate(self) -> float:
        """Fetch live USD/INR exchange rate."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://api.exchangerate-api.com/v4/latest/USD",
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                data = resp.json()
                rate = data.get("rates", {}).get("INR")
                if rate:
                    self._usd_inr_rate = rate
                    return rate
        except Exception as e:
            print(f"Error fetching USD/INR: {e}", file=sys.stderr)
        if self._usd_inr_rate:
            return self._usd_inr_rate
        print("WARNING: No USD/INR rate available, using fallback 86.5", file=sys.stderr)
        self._usd_inr_rate = 86.5
        return 86.5

    async def get_live_prices(self) -> list[SilverPrice]:
        """Fetch live silver prices via Yahoo Finance with browser impersonation."""
        prices = []

        fallback_prices = None
        if self._cached_prices:
            cache_age = time.time() - self._cache_time if self._cache_time else 999999
            if cache_age < self._cache_duration:
                return self._cached_prices
            fallback_prices = self._cached_prices

        usd_inr = await self._get_usd_inr_rate()

        try:
            chart = await asyncio.to_thread(_yf_fetch_sync, "XAGUSD=X", "2d")
            quote = chart["indicators"]["quote"][0]
            closes = [x for x in quote["close"] if x is not None]
            highs = [x for x in quote["high"] if x is not None]
            lows = [x for x in quote["low"] if x is not None]

            if closes:
                price_usd = closes[-1]
                prev = closes[-2] if len(closes) > 1 else price_usd
                change = price_usd - prev
                change_pct = (change / prev) * 100 if prev != 0 else 0

                prices.append(SilverPrice(
                    symbol="XAG/USD",
                    price=round(price_usd, 2),
                    currency="USD",
                    unit="troy_oz",
                    change_24h=round(change, 2),
                    change_pct_24h=round(change_pct, 2),
                    high_24h=round(highs[-1], 2) if highs else round(price_usd * 1.01, 2),
                    low_24h=round(lows[-1], 2) if lows else round(price_usd * 0.99, 2),
                    timestamp=datetime.now(),
                    source="Yahoo Finance"
                ))
        except Exception as e:
            print(f"Error fetching XAG/USD: {e}", file=sys.stderr)

        if not prices and fallback_prices:
            return fallback_prices

        if not prices:
            return []

        xag_usd = prices[0].price
        prices.append(SilverPrice(
            symbol="XAG/INR",
            price=round(xag_usd * usd_inr, 2),
            currency="INR",
            unit="troy_oz",
            change_24h=round(prices[0].change_24h * usd_inr, 2),
            change_pct_24h=prices[0].change_pct_24h,
            high_24h=round(prices[0].high_24h * usd_inr, 2),
            low_24h=round(prices[0].low_24h * usd_inr, 2),
            timestamp=datetime.now(),
            source="Derived from XAG/USD"
        ))

        self._cached_prices = prices
        self._cache_time = time.time()
        return prices

    async def get_india_prices(self) -> SilverPriceIndia:
        """Get India-specific silver prices with import duty, GST, and local premium."""
        usd_inr = await self._get_usd_inr_rate()

        try:
            prices = await self.get_live_prices()
            if prices and prices[0].price > 0:
                xag_usd = prices[0].price
            else:
                raise ValueError("No live prices available")
        except Exception as e:
            print(f"ERROR: Cannot fetch XAG/USD for India pricing: {e}", file=sys.stderr)
            raise HTTPException(status_code=502, detail="Unable to fetch live silver prices. Please try again.")

        # International price per kg in INR
        intl_price_per_kg_inr = xag_usd * usd_inr * KG_TO_TROY_OZ

        # India pricing: intl price + 15% import duty + 3% GST + 3.5% local premium
        import_duty_pct = 15.0
        gst_pct = 3.0
        local_premium_pct = 3.5

        price_with_duty = intl_price_per_kg_inr * (1 + import_duty_pct / 100)
        price_with_gst = price_with_duty * (1 + gst_pct / 100)
        final_price_per_kg = price_with_gst * (1 + local_premium_pct / 100)
        final_price_per_gram = final_price_per_kg / 1000

        mcx_price = final_price_per_kg * 1.005

        return SilverPriceIndia(
            price_per_gram=round(final_price_per_gram, 2),
            price_per_kg=round(final_price_per_kg, 2),
            mcx_future_price=round(mcx_price, 2),
            mcx_expiry="Near Month",
            local_premium_pct=local_premium_pct,
            import_duty_pct=import_duty_pct,
            currency="INR",
            timestamp=datetime.now(),
            source=f"XAG/USD ${xag_usd} × INR {usd_inr} + {import_duty_pct}% duty + {gst_pct}% GST + {local_premium_pct}% premium"
        )

    async def get_historical_data(self, symbol: str = "XAGUSD=X",
                                   period: str = "1y") -> HistoricalData:
        """Fetch historical price data via Yahoo Finance."""
        try:
            period_map = {"5d": "5d", "1w": "5d", "1mo": "1mo", "3mo": "3mo", "6mo": "6mo", "1y": "1y", "2y": "2y", "5y": "5y"}
            yf_period = period_map.get(period, period)
            chart = await asyncio.to_thread(_yf_fetch_sync, symbol, yf_period)
            timestamps = chart["timestamp"]
            quote = chart["indicators"]["quote"][0]

            data = []
            for i, ts in enumerate(timestamps):
                c = quote["close"][i]
                if c is not None:
                    data.append({
                        "date": datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                        "open": round(quote["open"][i], 2) if quote["open"][i] else 0,
                        "high": round(quote["high"][i], 2) if quote["high"][i] else 0,
                        "low": round(quote["low"][i], 2) if quote["low"][i] else 0,
                        "close": round(c, 2),
                        "volume": int(quote["volume"][i]) if quote["volume"][i] else 0
                    })

            return HistoricalData(symbol=symbol, data=data, period=period)
        except Exception as e:
            print(f"Error fetching historical data: {e}", file=sys.stderr)
            return HistoricalData(symbol=symbol, data=[], period=period)

    async def get_technical_indicators(self, symbol: str = "XAGUSD=X") -> dict:
        """Calculate technical indicators from historical data."""
        try:
            hist_data = await self.get_historical_data(symbol, "6mo")
            if not hist_data.data:
                return {"error": "No data available"}

            closes = pd.Series([d["close"] for d in hist_data.data])
            highs = pd.Series([d["high"] for d in hist_data.data])
            lows = pd.Series([d["low"] for d in hist_data.data])

            if len(closes) < 50:
                return {"error": "Insufficient data"}

            sma_20 = closes.rolling(20).mean().iloc[-1]
            sma_50 = closes.rolling(50).mean().iloc[-1]
            sma_200 = closes.rolling(min(200, len(closes))).mean().iloc[-1]
            current = closes.iloc[-1]

            delta = closes.diff()
            gain = delta.where(delta > 0, 0.0)
            loss = -delta.where(delta < 0, 0.0)
            avg_gain = gain.rolling(14).mean().iloc[-1]
            avg_loss = loss.rolling(14).mean().iloc[-1]
            rs = avg_gain / avg_loss if avg_loss != 0 else 100
            rsi = 100 - (100 / (1 + rs))

            ema_12 = closes.ewm(span=12).mean()
            ema_26 = closes.ewm(span=26).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9).mean()

            recent_high = highs.max()
            recent_low = lows.min()

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
            print(f"Error calculating technical indicators: {e}", file=sys.stderr)
            return {"error": "Unable to calculate indicators. Try again later."}

    async def get_supply_demand(self) -> SupplyDemand:
        """Get silver supply-demand fundamentals with deficit analysis.
        Data from Silver Institute World Silver Survey 2025 (2024 actuals)."""
        # 2024 actuals in tonnes (converted from Moz: 1 Moz = 31.1035 tonnes)
        mine_production = 25500    # 819.7 Moz
        recycling = 6000           # 193.9 Moz (12-year high)
        industrial = 21800         # ~700 Moz (record year: PV, automotive, AI, grid)
        jewelry = 6500             # 208.7 Moz
        investment = 6200          # physical investment + ETFs (declined y/y)
        india_imports = 6000
        india_demand = 6800

        total_supply = mine_production + recycling
        total_demand = industrial + jewelry + investment
        deficit = total_demand - total_supply
        deficit_pct = round((deficit / total_demand) * 100, 1)

        analysis = (
            f"Silver market recorded a structural deficit of {deficit:,} tonnes ({deficit_pct}% of demand) in 2024, "
            f"marking the 4th consecutive year of shortfall. "
            f"Industrial demand hit a record {industrial:,}t, driven by solar PV manufacturing, "
            f"AI-related applications, 5G infrastructure, and EV adoption. "
            f"Mine production rose just 0.9% to {mine_production:,}t, while recycling reached a 12-year high of {recycling:,}t. "
            f"Physical investment declined y/y but ETF inflows remained supportive. "
            f"India imported ~{india_imports:,} tonnes, remaining the 2nd largest consumer globally."
        )

        return SupplyDemand(
            global_mine_production=mine_production,
            global_recycling=recycling,
            industrial_demand=industrial,
            jewelry_demand=jewelry,
            investment_demand=investment,
            india_imports=india_imports,
            india_demand=india_demand,
            total_supply=total_supply,
            total_demand=total_demand,
            deficit=deficit,
            deficit_pct=deficit_pct,
            deficit_analysis=analysis,
            year=2024,
            source="Silver Institute World Silver Survey 2025"
        )
