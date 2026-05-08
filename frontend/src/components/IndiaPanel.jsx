import { TrendingUp, IndianRupee, Percent } from "lucide-react";

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
