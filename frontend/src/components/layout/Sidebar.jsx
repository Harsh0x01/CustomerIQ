import { Link, useLocation } from "react-router-dom";
import { useState } from "react";
import clsx from "clsx";
import {
  Activity,
  BarChart3,
  BrainCircuit,
  ChevronLeft,
  ChevronRight,
  Gauge,
  Home,
  Layers3,
  Search
} from "lucide-react";

const navItems = [
  { label: "Overview", path: "/dashboard", icon: BarChart3 },
  { label: "Predict", path: "/predict", icon: Gauge },
  { label: "Segments", path: "/segments", icon: Layers3 },
  { label: "Intelligence", path: "/intelligence", icon: BrainCircuit }
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <aside
      className={clsx(
        "glass-panel sticky top-0 hidden h-screen shrink-0 border-y-0 border-l-0 transition-all duration-300 lg:block",
        collapsed ? "w-[76px]" : "w-[264px]"
      )}
    >
      <div className="flex h-full flex-col">
        <div className="flex h-16 items-center justify-between border-b border-white/10 px-4">
          <Link to="/" className="focus-ring flex items-center gap-3 rounded-lg">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg border border-cyan/40 bg-cyan/10 text-cyan shadow-cyan">
              <Activity size={18} aria-hidden="true" />
            </span>
            {!collapsed ? (
              <span>
                <span className="block text-sm font-semibold text-ink">CustomerIQ</span>
                <span className="block font-mono text-[11px] text-muted">INTEL OS</span>
              </span>
            ) : null}
          </Link>
          <button
            type="button"
            className="focus-ring rounded-lg border border-white/10 p-2 text-muted transition hover:border-cyan/40 hover:text-cyan"
            onClick={() => setCollapsed((value) => !value)}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        </div>

        <nav className="flex-1 space-y-2 px-3 py-5" aria-label="Primary navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                title={collapsed ? item.label : undefined}
                className={clsx(
                  "focus-ring flex items-center gap-3 rounded-lg border px-3 py-3 text-sm transition",
                  active
                    ? "border-cyan/40 bg-cyan/10 text-cyan"
                    : "border-transparent text-muted hover:border-white/10 hover:bg-white/[0.04] hover:text-ink"
                )}
              >
                <Icon size={18} aria-hidden="true" />
                {!collapsed ? <span>{item.label}</span> : null}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-white/10 p-3">
          <Link
            to="/"
            className="focus-ring flex items-center gap-3 rounded-lg border border-white/10 px-3 py-3 text-sm text-muted transition hover:border-purple/40 hover:text-purple"
            title={collapsed ? "Landing" : undefined}
          >
            <Home size={18} aria-hidden="true" />
            {!collapsed ? <span>Landing</span> : null}
          </Link>
          {!collapsed ? (
            <div className="mt-3 rounded-lg border border-white/10 bg-white/[0.03] p-3">
              <div className="flex items-center gap-2 font-mono text-[11px] uppercase text-muted">
                <Search size={13} aria-hidden="true" />
                Model monitor
              </div>
              <div className="mt-3 h-1.5 overflow-hidden rounded bg-white/10">
                <div className="h-full w-[78%] bg-cyan" />
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </aside>
  );
}
