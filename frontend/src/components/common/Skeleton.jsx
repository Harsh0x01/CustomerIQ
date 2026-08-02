import clsx from "clsx";

export default function Skeleton({ className }) {
  return (
    <div
      className={clsx(
        "animate-pulse rounded-lg border border-white/5 bg-white/[0.06]",
        className
      )}
      aria-hidden="true"
    />
  );
}

export function PanelSkeleton({ rows = 4, className }) {
  return (
    <div className={clsx("glass-panel rounded-lg p-5", className)}>
      <Skeleton className="h-4 w-28" />
      <Skeleton className="mt-5 h-8 w-44" />
      <div className="mt-6 space-y-3">
        {Array.from({ length: rows }).map((_, index) => (
          <Skeleton key={index} className="h-3 w-full" />
        ))}
      </div>
    </div>
  );
}
