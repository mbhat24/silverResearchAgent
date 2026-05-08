import { useState } from "react";
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
