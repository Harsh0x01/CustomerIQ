export default function SectionHeader({ eyebrow, title, action }) {
  return (
    <div className="flex flex-col gap-3 border-b border-white/10 pb-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        {eyebrow ? <p className="font-mono text-xs uppercase text-cyan">{eyebrow}</p> : null}
        <h2 className="mt-1 text-lg font-semibold text-ink">{title}</h2>
      </div>
      {action ? <div>{action}</div> : null}
    </div>
  );
}
