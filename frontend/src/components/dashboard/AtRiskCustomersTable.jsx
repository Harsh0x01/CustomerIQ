import StatusPill from "../common/StatusPill.jsx";

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0
});

export default function AtRiskCustomersTable({ customers }) {
  return (
    <div className="overflow-hidden rounded-lg border border-white/10">
      <div className="max-h-[360px] overflow-auto">
        <table className="w-full min-w-[760px] border-collapse text-left">
          <thead className="sticky top-0 z-10 bg-[#11121a]">
            <tr className="border-b border-white/10 font-mono text-xs uppercase text-muted">
              <th className="px-4 py-3 font-medium">Customer</th>
              <th className="px-4 py-3 font-medium">Risk</th>
              <th className="px-4 py-3 font-medium">Probability</th>
              <th className="px-4 py-3 font-medium">Balance</th>
              <th className="px-4 py-3 font-medium">Salary</th>
              <th className="px-4 py-3 font-medium">SHAP drivers</th>
            </tr>
          </thead>
          <tbody>
            {customers.map((customer) => {
              const probability = Number(customer.churn_probability || 0);
              const risk = customer.risk_level?.toLowerCase() || "neutral";

              return (
                <tr
                  key={customer.customer_id}
                  className="border-b border-white/[0.06] bg-white/[0.015] transition hover:bg-white/[0.04]"
                >
                  <td className="px-4 py-3">
                    <span className="data-number text-sm text-ink">{customer.customer_id}</span>
                  </td>
                  <td className="px-4 py-3">
                    <StatusPill tone={risk}>{customer.risk_level}</StatusPill>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <span className="data-number w-12 text-sm text-ink">
                        {(probability * 100).toFixed(1)}%
                      </span>
                      <div className="h-1.5 w-24 overflow-hidden rounded bg-white/10">
                        <div
                          className="h-full rounded bg-danger"
                          style={{ width: `${Math.min(100, probability * 100)}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="data-number px-4 py-3 text-sm text-muted">
                    {currencyFormatter.format(customer.balance || 0)}
                  </td>
                  <td className="data-number px-4 py-3 text-sm text-muted">
                    {currencyFormatter.format(customer.estimated_salary || 0)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="group relative inline-flex max-w-[240px] flex-wrap gap-1">
                      {(customer.drivers || []).slice(0, 3).map((driver) => (
                        <span
                          key={driver}
                          className="rounded border border-purple/30 bg-purple/10 px-2 py-1 font-mono text-[11px] text-purple"
                        >
                          {driver}
                        </span>
                      ))}
                      <div className="pointer-events-none absolute bottom-full left-0 z-20 mb-2 hidden w-72 rounded-lg border border-white/10 bg-[#10121a] p-3 text-xs leading-5 text-muted shadow-purple group-hover:block">
                        Feature contribution summary from local or global SHAP drivers.
                      </div>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
