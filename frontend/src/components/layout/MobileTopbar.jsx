import { Link, useLocation } from "react-router-dom";
import { Activity, BarChart3, BrainCircuit, Gauge, Layers3 } from "lucide-react";
import clsx from "clsx";

const navItems = [
  { label: "Overview", path: "/dashboard", icon: BarChart3 },
  { label: "Predict", path: "/predict", icon: Gauge },
  { label: "Segments", path: "/segments", icon: Layers3 },
  { label: "Intel", path: "/intelligence", icon: BrainCircuit }
];

export default function MobileTopbar() {
  const location = useLocation();

  return (
    <header className="glass-panel sticky top-0 z-30 border-x-0 border-t-0 lg:hidden">
      <div className="flex h-14 items-center justify-between px-4">
        <Link to="/" className="focus-ring flex items-center gap-2 rounded-lg text-sm font-semibold">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg border border-cyan/40 bg-cyan/10 text-cyan">
            <Activity size={16} aria-hidden="true" />
          </span>
          CustomerIQ
        </Link>
      </div>
      <nav className="flex gap-2 overflow-x-auto border-t border-white/10 px-3 py-2" aria-label="Mobile navigation">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = location.pathname === item.path;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={clsx(
                "focus-ring flex min-w-max items-center gap-2 rounded-lg border px-3 py-2 text-xs",
                active
                  ? "border-cyan/40 bg-cyan/10 text-cyan"
                  : "border-white/10 bg-white/[0.03] text-muted"
              )}
            >
              <Icon size={15} aria-hidden="true" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
