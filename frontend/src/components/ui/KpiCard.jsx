import clsx from "clsx";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import useGsapCounter from "../../hooks/useGsapCounter.js";

export default function KpiCard({
  label,
  value,
  suffix = "",
  prefix = "",
  delta,
  tone = "cyan",
  formatter
}) {
  const counterRef = useGsapCounter(
    value,
    formatter ||
      ((next) => `${prefix}${Math.round(next).toLocaleString()}${suffix}`)
  );
  const positive = Number(delta) >= 0;

  return (
    <article className="glass-panel rounded-lg p-5 shadow-cyan">
      <div className="flex items-start justify-between gap-4">
        <p className="font-mono text-xs uppercase text-muted">{label}</p>
        {delta !== undefined ? (
          <span
            className={clsx(
              "inline-flex items-center gap-1 rounded border px-2 py-1 font-mono text-[11px]",
              positive
                ? "border-success/40 bg-success/10 text-success"
                : "border-danger/40 bg-danger/10 text-danger"
            )}
          >
            {positive ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}
            {Math.abs(Number(delta)).toFixed(1)}%
          </span>
        ) : null}
      </div>
      <div
        ref={counterRef}
        className={clsx(
          "data-number mt-5 text-3xl font-semibold",
          tone === "purple" ? "text-purple" : tone === "danger" ? "text-danger" : "text-cyan"
        )}
      >
        {prefix}0{suffix}
      </div>
      <div className="mt-5 h-1.5 overflow-hidden rounded bg-white/10">
        <div
          className={clsx(
            "h-full rounded",
            tone === "purple" ? "bg-purple" : tone === "danger" ? "bg-danger" : "bg-cyan"
          )}
          style={{ width: `${Math.min(100, Math.max(18, Number(value) % 100 || 68))}%` }}
        />
      </div>
    </article>
  );
}
