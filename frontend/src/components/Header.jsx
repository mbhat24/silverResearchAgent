import { Sparkles } from "lucide-react";

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
