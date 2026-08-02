import {
  Bar,
  BarChart,
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
    <div className="rounded-lg border border-white/10 bg-[#10121a] px-3 py-2 shadow-purple">
      <p className="font-mono text-xs text-muted">{label}</p>
      <p className="mt-1 font-mono text-xs text-purple">
        Contribution: {Number(payload[0].value).toFixed(2)}
      </p>
    </div>
  );
}

export default function FeatureImportanceBars({ data }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 8, right: 20, bottom: 8, left: 20 }}
      >
        <CartesianGrid stroke="rgba(255,255,255,0.06)" horizontal={false} />
        <XAxis
          type="number"
          tick={{ fill: "#8b92a5", fontSize: 12, fontFamily: "Consolas, monospace" }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          dataKey="name"
          type="category"
          width={120}
          tick={{ fill: "#8b92a5", fontSize: 12 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip content={<TooltipContent />} cursor={{ fill: "rgba(124,58,237,0.08)" }} />
        <Bar dataKey="value" fill="#7c3aed" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
