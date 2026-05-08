import { ArrowUp, ArrowDown, Minus } from "lucide-react";

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
