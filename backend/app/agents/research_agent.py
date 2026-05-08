import json
import uuid
from datetime import datetime
from typing import Optional
from openai import AsyncOpenAI

from ..models.schemas import ResearchReport
from ..config import get_settings

settings = get_settings()

RESEARCH_SYSTEM_PROMPT = """You are SilverSage, the world's most advanced silver market research AI. 
You have deep expertise in:
- Silver as a precious metal and industrial commodity
- Global macroeconomic factors affecting silver
- India's silver market (MCX, import duties, local demand patterns)
- Technical and fundamental analysis
- Silver's role in the energy transition (solar panels, EVs, electronics)
- Historical silver price patterns and monetary history
- Geopolitical factors affecting precious metals

You provide data-driven, nuanced analysis. You cite specific price levels, trends, and catalysts.
You are honest about uncertainty and risks. You think in terms of probabilities, not certainties.

When discussing India specifically:
- Note that India is the world's largest silver consumer
- MCX is the primary exchange for silver futures
- Import duties significantly affect domestic prices
- Rural demand and monsoon seasons impact jewelry demand
- Silver has deep cultural significance in Indian weddings and festivals"""


class ResearchAgent:
    """AI agent that performs deep research on silver markets."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def generate_report(self, topic: str = "comprehensive",
                               market_data: Optional[dict] = None,
                               news_items: Optional[list] = None) -> ResearchReport:
        """Generate a deep research report on silver."""

        topic_prompts = {
            "comprehensive": "Provide a comprehensive analysis of the silver market. Cover price action, technical analysis, fundamental drivers, supply-demand dynamics, macroeconomic factors, and the outlook for the next 3-6 months. Include both global and India-specific analysis.",
            "india": "Provide a deep-dive analysis of India's silver market. Cover MCX price action, import trends, local demand drivers, festival/wedding season impact, government policies, and the outlook for Indian silver prices. Compare with global prices and explain the premium/discount dynamics.",
            "technical": "Provide a detailed technical analysis of silver prices. Cover key support and resistance levels, moving averages, RSI, MACD, chart patterns, volume analysis, and potential price targets. Include both short-term (weeks) and medium-term (months) outlook.",
            "fundamental": "Provide a fundamental analysis of silver. Cover supply-demand balance, mine production trends, industrial demand (especially solar/EV), investment demand, ETF flows, central bank activity, and how these factors may drive prices.",
            "macro": "Analyze how macroeconomic factors are affecting silver. Cover USD strength, interest rate expectations, inflation trends, geopolitical risks, bond yields, and how these interplay with silver's dual role as precious and industrial metal.",
            "predictions": "Provide silver price predictions for the next 6-12 months. Give specific price targets with probability assessments. Cover bullish and bearish scenarios. Include key catalysts to watch and risk factors that could change the outlook."
        }

        prompt = topic_prompts.get(topic, topic_prompts["comprehensive"])

        # Build context from market data
        context = ""
        if market_data:
            context += f"\n\nCurrent Market Data:\n{json.dumps(market_data, indent=2, default=str)}"
        if news_items:
            context += f"\n\nRecent News:\n{json.dumps(news_items[:10], indent=2, default=str)}"

        full_prompt = f"{prompt}\n{context}\n\nGenerate your response as a structured JSON with these fields:\n- title: string\n- summary: string (2-3 sentence executive summary)\n- sections: list of {{heading, content}} objects\n- key_findings: list of strings (5-8 key takeaways)\n- sentiment: 'bullish' | 'bearish' | 'neutral'\n- price_targets: {{short_term: {{low, high, timeframe}}, medium_term: {{low, high, timeframe}}}}\n- risk_factors: list of strings (key risks to the outlook)\n- data_sources: list of strings (types of data used)"

        if self.client:
            try:
                response = await self.client.chat.completions.create(
                    model=settings.research_model,
                    messages=[
                        {"role": "system", "content": RESEARCH_SYSTEM_PROMPT},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=4000,
                    response_format={"type": "json_object"}
                )
                content = json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"OpenAI API error: {e}")
                content = self._fallback_report(topic)
        else:
            content = self._fallback_report(topic)

        return ResearchReport(
            id=str(uuid.uuid4())[:8],
            title=content.get("title", f"Silver Market Analysis: {topic.title()}"),
            summary=content.get("summary", ""),
            sections=content.get("sections", []),
            key_findings=content.get("key_findings", []),
            sentiment=content.get("sentiment", "neutral"),
            price_targets=content.get("price_targets", {}),
            risk_factors=content.get("risk_factors", []),
            generated_at=datetime.now(),
            data_sources=content.get("data_sources", ["Market data", "News aggregation"])
        )

    async def answer_query(self, query: str, context: Optional[dict] = None) -> dict:
        """Answer a specific user query about silver."""
        if not self.client:
            return {"answer": "AI agent not configured. Set OPENAI_API_KEY in .env"}

        ctx_str = json.dumps(context, indent=2, default=str) if context else ""

        response = await self.client.chat.completions.create(
            model=settings.research_model,
            messages=[
                {"role": "system", "content": RESEARCH_SYSTEM_PROMPT},
                {"role": "user", "content": f"Context data:\n{ctx_str}\n\nUser question: {query}\n\nProvide a thorough, data-driven answer."}
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    def _fallback_report(self, topic: str) -> dict:
        """Fallback report when AI is not configured."""
        return {
            "title": f"Silver Market Analysis: {topic.title()}",
            "summary": "AI-powered analysis requires OpenAI API key configuration. Set OPENAI_API_KEY in your .env file to enable deep research reports. In the meantime, you can view live prices, charts, and technical indicators on the dashboard.",
            "sections": [
                {"heading": "Setup Required", "content": "To unlock AI-powered deep research, add your OpenAI API key to the .env file. The agent will then analyze silver markets using real-time data, news, and advanced reasoning."},
                {"heading": "Available Features", "content": "Even without AI, you have access to: live silver prices (XAG/USD, COMEX, INR), historical charts, technical indicators (RSI, MACD, moving averages), India-specific pricing, supply-demand fundamentals, and news aggregation."}
            ],
            "key_findings": [
                "Configure OpenAI API key for AI-powered research",
                "Live price tracking is fully operational",
                "India-specific silver data available on dashboard",
                "Technical indicators and charts are live"
            ],
            "sentiment": "neutral",
            "price_targets": {},
            "risk_factors": ["AI analysis unavailable without API key"],
            "data_sources": ["Local data only"]
        }
