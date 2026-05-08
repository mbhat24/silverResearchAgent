#!/usr/bin/env python3
"""Generate React frontend files for SilverSage dashboard."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
FRONTEND = os.path.join(os.path.dirname(BASE), "frontend")
SRC = os.path.join(FRONTEND, "src")
COMP = os.path.join(SRC, "components")

os.makedirs(COMP, exist_ok=True)

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)
    print(f"  {os.path.relpath(path, FRONTEND)}")

# index.html
write_file(os.path.join(FRONTEND, "index.html"), """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SilverSage - AI Silver Research Agent</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E🥈%3C/text%3E%3C/svg%3E">
</head>
<body class="bg-gray-950 text-white antialiased">
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
""")

# src/main.jsx
write_file(os.path.join(SRC, "main.jsx"), """import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
""")

# src/index.css
write_file(os.path.join(SRC, "index.css"), """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Inter', system-ui, -apple-system, sans-serif; }
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #0f172a; }
  ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
}

@layer components {
  .glass {
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(71, 85, 105, 0.3);
    border-radius: 16px;
  }
  .glass-hover { transition: all 0.2s ease; }
  .glass-hover:hover { border-color: rgba(148, 163, 184, 0.5); background: rgba(30, 41, 59, 0.7); }
  .gradient-text {
    background: linear-gradient(135deg, #e2e8f0 0%, #94a3b8 50%, #c0c0c0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .silver-gradient {
    background: linear-gradient(135deg, #475569 0%, #94a3b8 50%, #cbd5e1 100%);
  }
  .pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  .slide-up { animation: slideUp 0.3s ease-out; }
  @keyframes slideUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
}
""")

print("Base files created.")

# src/components/Header.jsx
write_file(os.path.join(COMP, "Header.jsx"), """import { Sparkles } from "lucide-react";

export default function Header() {
  return (
    <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl silver-gradient flex items-center justify-center text-lg shadow-lg shadow-slate-500/20">
            🥈
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">
              <span className="gradient-text">SilverSage</span>
            </h1>
            <p className="text-xs text-slate-500 -mt-0.5">AI-Powered Silver Intelligence</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 text-xs text-slate-400 bg-gray-800 px-3 py-1.5 rounded-full">
            <Sparkles size={12} className="text-slate-400" />
            Live Data
          </span>
        </div>
      </div>
    </header>
  );
}
""")

# src/components/PriceTicker.jsx
write_file(os.path.join(COMP, "PriceTicker.jsx"), """import { ArrowUp, ArrowDown, Minus } from "lucide-react";

export default function PriceTicker({ prices }) {
  if (!prices || prices.length === 0) return null;

  return (
    <div className="bg-gray-900 border-b border-gray-800">
      <div className="max-w-7xl mx-auto px-4 py-2.5 flex gap-6 overflow-x-auto">
        {prices.map((p) => {
          const isUp = p.change_24h > 0;
          const isFlat = p.change_24h === 0;
          const Icon = isUp ? ArrowUp : isFlat ? Minus : ArrowDown;
          const colorClass = isUp ? "text-emerald-400" : isFlat ? "text-slate-400" : "text-red-400";

          return (
            <div key={p.symbol} className="flex items-center gap-2 whitespace-nowrap shrink-0">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{p.symbol}</span>
              <span className="text-sm font-bold text-white">
                {p.currency === "USD" ? "$" : "₹"}{p.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
              <span className={"flex items-center gap-0.5 text-xs font-medium " + colorClass}>
                <Icon size={12} />
                {p.change_pct_24h > 0 ? "+" : ""}{p.change_pct_24h.toFixed(2)}%
              </span>
              <span className="text-[10px] text-slate-600">{p.source}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
""")

print("Components created.")

# src/components/PriceChart.jsx
write_file(os.path.join(COMP, "PriceChart.jsx"), """import { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";
import { TrendingUp, Clock } from "lucide-react";

const PERIODS = [
  { label: "1W", value: "5d" },
  { label: "1M", value: "1mo" },
  { label: "3M", value: "3mo" },
  { label: "6M", value: "6mo" },
  { label: "1Y", value: "1y" },
];

export default function PriceChart() {
  const [period, setPeriod] = useState("1mo");
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const res = await fetch("/api/prices/historical?symbol=XAGUSD=X&period=" + period);
        const json = await res.json();
        const chartData = json.data.map((d) => ({
          date: d.date,
          price: d.close,
          high: d.high,
          low: d.low,
        }));
        setData(chartData);

        if (chartData.length > 1) {
          const first = chartData[0].price;
          const last = chartData[chartData.length - 1].price;
          const change = last - first;
          const changePct = ((change / first) * 100);
          const high = Math.max(...chartData.map((d) => d.high));
          const low = Math.min(...chartData.map((d) => d.low));
          setStats({ first, last, change, changePct, high, low });
        }
      } catch (e) {
        console.error("Chart fetch error:", e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [period]);

  const isUp = stats?.change >= 0;

  return (
    <div className="glass glass-hover p-5 slide-up">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp size={18} className="text-slate-400" />
          <h3 className="text-sm font-semibold text-slate-300">XAG/USD Price</h3>
        </div>
        <div className="flex gap-1 bg-gray-800 rounded-lg p-0.5">
          {PERIODS.map((p) => (
            <button
              key={p.value}
              onClick={() => setPeriod(p.value)}
              className={"px-2.5 py-1 text-xs font-medium rounded-md transition-all " +
                (period === p.value ? "bg-gray-700 text-white" : "text-slate-500 hover:text-slate-300")}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {stats && (
        <div className="flex gap-6 mb-4">
          <div>
            <span className="text-xs text-slate-500">Current</span>
            <p className="text-lg font-bold text-white">${stats.last.toFixed(2)}</p>
          </div>
          <div>
            <span className="text-xs text-slate-500">Change</span>
            <p className={"text-lg font-bold " + (isUp ? "text-emerald-400" : "text-red-400")}>
              {isUp ? "+" : ""}{stats.change.toFixed(2)} ({isUp ? "+" : ""}{stats.changePct.toFixed(2)}%)
            </p>
          </div>
          <div>
            <span className="text-xs text-slate-500">High / Low</span>
            <p className="text-lg font-bold text-white">${stats.high.toFixed(2)} / ${stats.low.toFixed(2)}</p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="h-64 flex items-center justify-center">
          <div className="w-6 h-6 border-2 border-slate-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="silverGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={isUp ? "#34d399" : "#f87171"} stopOpacity={0.2} />
                <stop offset="100%" stopColor={isUp ? "#34d399" : "#f87171"} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 11 }} tickLine={false} axisLine={false} />
            <YAxis domain={["auto", "auto"]} tick={{ fill: "#64748b", fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => "$" + v.toFixed(0)} />
            <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "8px", color: "#fff" }} formatter={(value) => ["$" + Number(value).toFixed(2), "Price"]} />
            <Area type="monotone" dataKey="price" stroke={isUp ? "#34d399" : "#f87171"} strokeWidth={2} fill="url(#silverGradient)" />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
""")

# src/components/IndiaPanel.jsx
write_file(os.path.join(COMP, "IndiaPanel.jsx"), """import { TrendingUp, IndianRupee, Percent } from "lucide-react";

export default function IndiaPanel({ data, expanded = false }) {
  if (!data) return (
    <div className="glass p-5">
      <div className="flex items-center gap-2 mb-3">
        <IndianRupee size={18} className="text-slate-400" />
        <h3 className="text-sm font-semibold text-slate-300">India Silver Prices</h3>
      </div>
      <p className="text-slate-500 text-sm">Loading...</p>
    </div>
  );

  return (
    <div className={"glass glass-hover p-5 slide-up " + (expanded ? "col-span-2" : "")}>
      <div className="flex items-center gap-2 mb-4">
        <IndianRupee size={18} className="text-slate-400" />
        <h3 className="text-sm font-semibold text-slate-300">India Silver Market</h3>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div>
          <span className="text-xs text-slate-500">Per Gram</span>
          <p className="text-lg font-bold text-white">₹{data.price_per_gram.toFixed(2)}</p>
        </div>
        <div>
          <span className="text-xs text-slate-500">Per Kg</span>
          <p className="text-lg font-bold text-white">₹{data.price_per_kg.toLocaleString()}</p>
        </div>
        <div>
          <span className="text-xs text-slate-500 flex items-center gap-1"><Percent size={10} />Local Premium</span>
          <p className="text-lg font-bold text-emerald-400">+{data.local_premium_pct}%</p>
        </div>
        <div>
          <span className="text-xs text-slate-500 flex items-center gap-1"><Percent size={10} />Import Duty</span>
          <p className="text-lg font-bold text-amber-400">{data.import_duty_pct}%</p>
        </div>
      </div>

      {expanded && (
        <div className="mt-4 pt-4 border-t border-gray-800">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={16} className="text-slate-400" />
            <span className="text-xs text-slate-500">MCX Futures (Near Month)</span>
          </div>
          <p className="text-2xl font-bold text-white">₹{data.mcx_future_price?.toLocaleString() || "N/A"}</p>
          <p className="text-xs text-slate-500 mt-1">Source: {data.source}</p>
        </div>
      )}
    </div>
  );
}
""")

# src/components/TechnicalPanel.jsx
write_file(os.path.join(COMP, "TechnicalPanel.jsx"), """import { Activity, TrendingUp, TrendingDown, Gauge } from "lucide-react";

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
""")

print("More components created.")

# src/components/ResearchPanel.jsx
write_file(os.path.join(COMP, "ResearchPanel.jsx"), """import { useState } from "react";
import { Brain, Sparkles, AlertCircle, TrendingUp, TrendingDown, Minus } from "lucide-react";

export default function ResearchPanel() {
  const [topic, setTopic] = useState("comprehensive");
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const topics = [
    { id: "comprehensive", label: "Comprehensive" },
    { id: "india", label: "India Market" },
    { id: "technical", label: "Technical" },
    { id: "fundamental", label: "Fundamental" },
    { id: "macro", label: "Macro" },
    { id: "predictions", label: "Predictions" },
  ];

  const generateReport = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/research/report?topic=" + topic);
      const data = await res.json();
      setReport(data);
    } catch (e) {
      console.error("Report error:", e);
    } finally {
      setLoading(false);
    }
  };

  const sentimentIcon = report?.sentiment === "bullish" ? TrendingUp : report?.sentiment === "bearish" ? TrendingDown : Minus;
  const sentimentColor = report?.sentiment === "bullish" ? "text-emerald-400" : report?.sentiment === "bearish" ? "text-red-400" : "text-slate-400";

  return (
    <div className="space-y-4">
      <div className="glass glass-hover p-5">
        <div className="flex items-center gap-2 mb-4">
          <Brain size={18} className="text-slate-400" />
          <h3 className="text-sm font-semibold text-slate-300">AI Research Reports</h3>
        </div>

        <div className="flex gap-2 mb-4 flex-wrap">
          {topics.map((t) => (
            <button
              key={t.id}
              onClick={() => setTopic(t.id)}
              className={"px-3 py-1.5 text-xs font-medium rounded-lg transition-all " +
                (topic === t.id ? "bg-blue-600 text-white" : "bg-gray-800 text-slate-400 hover:text-slate-200")}
            >
              {t.label}
            </button>
          ))}
        </div>

        <button
          onClick={generateReport}
          disabled={loading}
          className="w-full px-4 py-2.5 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Sparkles size={16} />
              Generate Report
            </>
          )}
        </button>
      </div>

      {report && (
        <div className="glass glass-hover p-5 slide-up">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-bold text-white">{report.title}</h4>
            <div className={"flex items-center gap-1.5 text-xs font-medium " + sentimentColor}>
              {sentimentIcon && <sentimentIcon size={14} />}
              {report.sentiment.toUpperCase()}
            </div>
          </div>

          <p className="text-slate-300 text-sm mb-4">{report.summary}</p>

          {report.key_findings && report.key_findings.length > 0 && (
            <div className="mb-4">
              <h5 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Key Findings</h5>
              <ul className="space-y-1">
                {report.key_findings.map((f, i) => (
                  <li key={i} className="text-xs text-slate-400 flex items-start gap-2">
                    <span className="text-emerald-400">•</span>
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {report.risk_factors && report.risk_factors.length > 0 && (
            <div className="mb-4">
              <h5 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                <AlertCircle size={12} /> Risk Factors
              </h5>
              <ul className="space-y-1">
                {report.risk_factors.map((r, i) => (
                  <li key={i} className="text-xs text-slate-400 flex items-start gap-2">
                    <span className="text-red-400">•</span>
                    {r}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <p className="text-[10px] text-slate-600">Generated at {new Date(report.generated_at).toLocaleString()}</p>
        </div>
      )}
    </div>
  );
}
""")

# src/components/NewsFeed.jsx
write_file(os.path.join(COMP, "NewsFeed.jsx"), """import { Newspaper, Clock, ExternalLink } from "lucide-react";

export default function NewsFeed({ items }) {
  if (!items || items.length === 0) {
    return (
      <div className="glass p-5">
        <div className="flex items-center gap-2 mb-3">
          <Newspaper size={18} className="text-slate-400" />
          <h3 className="text-sm font-semibold text-slate-300">Silver News</h3>
        </div>
        <p className="text-slate-500 text-sm">Loading news...</p>
      </div>
    );
  }

  return (
    <div className="glass glass-hover p-5 slide-up">
      <div className="flex items-center gap-2 mb-4">
        <Newspaper size={18} className="text-slate-400" />
        <h3 className="text-sm font-semibold text-slate-300">Latest News</h3>
      </div>

      <div className="space-y-3">
        {items.slice(0, 10).map((item, i) => (
          <a
            key={i}
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors"
          >
            <div className="flex items-start justify-between gap-2 mb-1">
              <h4 className="text-sm font-medium text-white line-clamp-2">{item.title}</h4>
              <ExternalLink size={12} className="text-slate-500 shrink-0" />
            </div>
            <p className="text-xs text-slate-400 line-clamp-2 mb-2">{item.summary}</p>
            <div className="flex items-center gap-2 text-[10px] text-slate-600">
              <span>{item.source}</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Clock size={10} />
                {new Date(item.published_at).toLocaleDateString()}
              </span>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
""")

# src/components/SupplyDemandPanel.jsx
write_file(os.path.join(COMP, "SupplyDemandPanel.jsx"), """import { Factory, TrendingUp, TrendingDown } from "lucide-react";

export default function SupplyDemandPanel({ data, expanded = false }) {
  if (!data) {
    return (
      <div className="glass p-5">
        <div className="flex items-center gap-2 mb-3">
          <Factory size={18} className="text-slate-400" />
          <h3 className="text-sm font-semibold text-slate-300">Supply & Demand</h3>
        </div>
        <p className="text-slate-500 text-sm">Loading...</p>
      </div>
    );
  }

  const metrics = [
    { label: "Global Mine Production", value: data.global_mine_production, unit: "tonnes", icon: TrendingUp },
    { label: "Global Recycling", value: data.global_recycling, unit: "tonnes", icon: TrendingUp },
    { label: "Industrial Demand", value: data.industrial_demand, unit: "tonnes", icon: TrendingUp },
    { label: "Jewelry Demand", value: data.jewelry_demand, unit: "tonnes", icon: TrendingUp },
    { label: "Investment Demand", value: data.investment_demand, unit: "tonnes", icon: TrendingUp },
    { label: "India Imports", value: data.india_imports, unit: "tonnes", icon: TrendingDown },
  ];

  return (
    <div className={"glass glass-hover p-5 slide-up " + (expanded ? "col-span-2" : "")}>
      <div className="flex items-center gap-2 mb-4">
        <Factory size={18} className="text-slate-400" />
        <h3 className="text-sm font-semibold text-slate-300">Supply & Demand Fundamentals</h3>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {metrics.map((m) => {
          const Icon = m.icon;
          return (
            <div key={m.label} className="bg-gray-800/50 rounded-lg p-3">
              <div className="flex items-center gap-1 mb-1">
                <Icon size={12} className="text-slate-500" />
                <span className="text-[10px] text-slate-500">{m.label}</span>
              </div>
              <p className="text-sm font-bold text-white">{m.value?.toLocaleString()}</p>
              <span className="text-[10px] text-slate-600">{m.unit}</span>
            </div>
          );
        })}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-800 text-xs text-slate-600">
        Data year: {data.year} • Source: {data.source}
      </div>
    </div>
  );
}
""")

print("All components created.")

# src/App.jsx
write_file(os.path.join(SRC, "App.jsx"), """import { useState, useEffect, useCallback } from "react";
import Header from "./components/Header";
import PriceTicker from "./components/PriceTicker";
import PriceChart from "./components/PriceChart";
import IndiaPanel from "./components/IndiaPanel";
import TechnicalPanel from "./components/TechnicalPanel";
import ResearchPanel from "./components/ResearchPanel";
import NewsFeed from "./components/NewsFeed";
import SupplyDemandPanel from "./components/SupplyDemandPanel";
import { BarChart3, Newspaper, Brain, TrendingUp, Factory } from "lucide-react";

const API_BASE = "/api";

export default function App() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [error, setError] = useState(null);

  const fetchDashboard = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch(API_BASE + "/dashboard");
      if (!res.ok) throw new Error("Failed to fetch");
      const data = await res.json();
      setDashboard(data);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 30000);
    return () => clearInterval(interval);
  }, [fetchDashboard]);

  if (loading && !dashboard) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-slate-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400 text-lg">Loading SilverSage...</p>
        </div>
      </div>
    );
  }

  if (error && !dashboard) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center glass p-8 max-w-md">
          <p className="text-red-400 text-lg mb-2">Connection Error</p>
          <p className="text-slate-400">Make sure the backend is running on port 8000</p>
          <button onClick={fetchDashboard} className="mt-4 px-4 py-2 bg-slate-700 rounded-lg hover:bg-slate-600 transition">
            Retry
          </button>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: "overview", label: "Overview", icon: BarChart3 },
    { id: "india", label: "India Market", icon: TrendingUp },
    { id: "research", label: "AI Research", icon: Brain },
    { id: "news", label: "News", icon: Newspaper },
    { id: "fundamentals", label: "Fundamentals", icon: Factory },
  ];

  return (
    <div className="min-h-screen bg-gray-950">
      <Header />
      <PriceTicker prices={dashboard?.live_prices || []} />

      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 mt-4">
        <div className="flex gap-1 bg-gray-900 rounded-xl p-1 border border-gray-800">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={"flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all " +
                  (isActive ? "bg-gray-800 text-white shadow-lg" : "text-slate-400 hover:text-slate-200")}
              >
                <Icon size={16} />
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div className="max-w-7xl mx-auto px-4 pb-8 mt-4">
        {activeTab === "overview" && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <PriceChart />
              <TechnicalPanel data={dashboard?.technical_summary} />
            </div>
            <IndiaPanel data={dashboard?.india_prices} />
          </div>
        )}

        {activeTab === "india" && (
          <div className="space-y-4">
            <IndiaPanel data={dashboard?.india_prices} expanded />
            <SupplyDemandPanel data={dashboard?.supply_demand} />
          </div>
        )}

        {activeTab === "research" && (
          <ResearchPanel />
        )}

        {activeTab === "news" && (
          <NewsFeed items={dashboard?.recent_news || []} />
        )}

        {activeTab === "fundamentals" && (
          <div className="space-y-4">
            <SupplyDemandPanel data={dashboard?.supply_demand} expanded />
            <TechnicalPanel data={dashboard?.technical_summary} />
          </div>
        )}
      </div>
    </div>
  );
}
""")

print("App.jsx created. Frontend complete!")
