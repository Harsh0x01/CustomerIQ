import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

function TooltipContent({ active, payload }) {
  if (!active || !payload?.length) {
    return null;
  }

  const item = payload[0].payload;

  return (
    <div className="rounded-lg border border-white/10 bg-[#10121a] px-3 py-2 shadow-purple">
      <p className="text-sm font-medium text-ink">{item.name}</p>
      <p className="mt-1 font-mono text-xs text-muted">{item.value.toLocaleString()} customers</p>
    </div>
  );
}

export default function SegmentDonut({ data }) {
  const total = data.reduce((sum, item) => sum + Number(item.value || 0), 0);

  return (
    <div className="grid gap-4 md:grid-cols-[minmax(0,1fr)_180px] md:items-center">
      <div className="relative h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius="60%"
              outerRadius="84%"
              paddingAngle={3}
              stroke="rgba(10,10,15,0.9)"
              strokeWidth={3}
            >
              {data.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<TooltipContent />} />
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="data-number text-3xl font-semibold text-ink">
            {total.toLocaleString()}
          </span>
          <span className="mt-1 font-mono text-xs uppercase text-muted">Profiled</span>
        </div>
      </div>
      <div className="space-y-3">
        {data.map((item) => (
          <div key={item.name} className="flex items-center justify-between gap-3 text-sm">
            <span className="flex min-w-0 items-center gap-2 text-muted">
              <span className="h-2.5 w-2.5 rounded-sm" style={{ background: item.color }} />
              <span className="truncate">{item.name}</span>
            </span>
            <span className="data-number text-ink">
              {total ? Math.round((item.value / total) * 100) : 0}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
