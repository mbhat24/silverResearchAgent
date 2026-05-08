import { useState, useEffect } from "react";
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
