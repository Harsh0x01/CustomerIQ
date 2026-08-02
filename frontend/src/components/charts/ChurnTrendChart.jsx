import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

function TooltipContent({ active, payload, label }) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div className="rounded-lg border border-white/10 bg-[#10121a] px-3 py-2 shadow-cyan">
      <p className="font-mono text-xs text-muted">{label}</p>
      {payload.map((item) => (
        <p key={item.dataKey} className="mt-1 font-mono text-xs" style={{ color: item.color }}>
          {item.name}: {Number(item.value).toFixed(1)}%
        </p>
      ))}
    </div>
  );
}

export default function ChurnTrendChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart data={data} margin={{ top: 16, right: 12, bottom: 0, left: -18 }}>
        <defs>
          <linearGradient id="churnGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#00d4ff" stopOpacity={0.38} />
            <stop offset="100%" stopColor="#00d4ff" stopOpacity={0.02} />
          </linearGradient>
          <linearGradient id="retainedGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#7c3aed" stopOpacity={0.24} />
            <stop offset="100%" stopColor="#7c3aed" stopOpacity={0.01} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
        <XAxis
          dataKey="month"
          tick={{ fill: "#8b92a5", fontSize: 12, fontFamily: "Consolas, monospace" }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: "#8b92a5", fontSize: 12, fontFamily: "Consolas, monospace" }}
          axisLine={false}
          tickLine={false}
          tickFormatter={(value) => `${value}%`}
        />
        <Tooltip content={<TooltipContent />} cursor={{ stroke: "rgba(0,212,255,0.35)" }} />
        <Area
          type="monotone"
          dataKey="retained"
          name="Retained"
          stroke="#7c3aed"
          strokeWidth={2}
          fill="url(#retainedGradient)"
        />
        <Area
          type="monotone"
          dataKey="churn"
          name="Churn"
          stroke="#00d4ff"
          strokeWidth={2.4}
          fill="url(#churnGradient)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
