import clsx from "clsx";

const toneClass = {
  live: "border-success/40 bg-success/10 text-success",
  demo: "border-warning/40 bg-warning/10 text-warning",
  high: "border-danger/40 bg-danger/10 text-danger",
  medium: "border-warning/40 bg-warning/10 text-warning",
  low: "border-success/40 bg-success/10 text-success",
  neutral: "border-white/15 bg-white/[0.04] text-muted"
};

export default function StatusPill({ tone = "neutral", children }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded border px-2 py-1 font-mono text-[11px] uppercase",
        toneClass[tone] || toneClass.neutral
      )}
    >
      {children}
    </span>
  );
}
