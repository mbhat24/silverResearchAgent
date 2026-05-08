import { Newspaper, Clock, ExternalLink } from "lucide-react";

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
