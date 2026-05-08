import { useState, useEffect, useCallback } from "react";
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
