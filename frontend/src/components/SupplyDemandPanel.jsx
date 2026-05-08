import { Factory, TrendingUp, TrendingDown } from "lucide-react";

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
