import { Activity, TrendingUp, TrendingDown, Gauge } from "lucide-react";

export default function TechnicalPanel({ data }) {
  if (!data || data.error) {
    return (
      <div className="glass p-5">
        <div className="flex items-center gap-2 mb-3">
          <Activity size={18} className="text-slate-400" />
          <h3 className="text-sm font-semibold text-slate-300">Technical Indicators</h3>
        </div>
        <p className="text-slate-500 text-sm">Loading indicators...</p>
      </div>
    );
  }

  const trendColor = data.trend === "bullish" ? "text-emerald-400" : data.trend === "bearish" ? "text-red-400" : "text-slate-400";
  const TrendIcon = data.trend === "bullish" ? TrendingUp : data.trend === "bearish" ? TrendingDown : Gauge;

  const indicators = [
    { label: "SMA 20", value: "$" + data.sma_20?.toFixed(2), relation: data.current_price > data.sma_20 ? "above" : "below" },
    { label: "SMA 50", value: "$" + data.sma_50?.toFixed(2), relation: data.current_price > data.sma_50 ? "above" : "below" },
    { label: "RSI (14)", value: data.rsi_14?.toFixed(1), relation: data.rsi_14 > 70 ? "overbought" : data.rsi_14 < 30 ? "oversold" : "neutral" },
    { label: "MACD", value: data.macd?.toFixed(3), relation: data.macd > data.macd_signal ? "bullish" : "bearish" },
  ];

  return (
    <div className="glass glass-hover p-5 slide-up">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity size={18} className="text-slate-400" />
          <h3 className="text-sm font-semibold text-slate-300">Technical Indicators</h3>
        </div>
        <div className={"flex items-center gap-1.5 text-xs font-medium " + trendColor}>
          <TrendIcon size={14} />
          {data.trend.toUpperCase()}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {indicators.map((ind) => (
          <div key={ind.label} className="bg-gray-800/50 rounded-lg p-3">
            <span className="text-xs text-slate-500">{ind.label}</span>
            <p className="text-sm font-bold text-white mt-1">{ind.value}</p>
            <span className={"text-[10px] " + (ind.relation === "above" || ind.relation === "bullish" || ind.relation === "overbought" ? "text-emerald-400" : ind.relation === "below" || ind.relation === "bearish" || ind.relation === "oversold" ? "text-red-400" : "text-slate-500")}>
              {ind.relation}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-800 grid grid-cols-3 gap-4">
        <div>
          <span className="text-xs text-slate-500">Support</span>
          <p className="text-sm font-bold text-white">${data.support?.toFixed(2)}</p>
        </div>
        <div>
          <span className="text-xs text-slate-500">Resistance</span>
          <p className="text-sm font-bold text-white">${data.resistance?.toFixed(2)}</p>
        </div>
        <div>
          <span className="text-xs text-slate-500">30D Volatility</span>
          <p className="text-sm font-bold text-white">{data.volatility_30d?.toFixed(2)}%</p>
        </div>
      </div>
    </div>
  );
}
