import { RefreshCcw } from "lucide-react";
import DashboardShell from "../components/layout/DashboardShell.jsx";
import KpiCard from "../components/ui/KpiCard.jsx";
import ChurnTrendChart from "../components/charts/ChurnTrendChart.jsx";
import SegmentDonut from "../components/charts/SegmentDonut.jsx";
import AtRiskCustomersTable from "../components/dashboard/AtRiskCustomersTable.jsx";
import ErrorBoundary from "../components/common/ErrorBoundary.jsx";
import SectionHeader from "../components/common/SectionHeader.jsx";
import StatusPill from "../components/common/StatusPill.jsx";
import { PanelSkeleton } from "../components/common/Skeleton.jsx";
import useDashboardData from "../hooks/useDashboardData.js";
import usePageIntro from "../hooks/usePageIntro.js";

const compactCurrency = new Intl.NumberFormat("en-US", {
  notation: "compact",
  compactDisplay: "short",
  maximumFractionDigits: 1
});

function DashboardLoading() {
  return (
    <DashboardShell>
      <div className="px-5 py-6 sm:px-8">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <PanelSkeleton rows={2} />
          <PanelSkeleton rows={2} />
          <PanelSkeleton rows={2} />
          <PanelSkeleton rows={2} />
        </div>
        <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1.55fr)_minmax(360px,0.9fr)]">
          <PanelSkeleton rows={7} className="min-h-[420px]" />
          <PanelSkeleton rows={7} className="min-h-[420px]" />
        </div>
      </div>
    </DashboardShell>
  );
}

export default function DashboardPage() {
  const { loading, error, data } = useDashboardData();
  const scope = usePageIntro([loading]);

  if (loading || !data) {
    return <DashboardLoading />;
  }

  const { stats, trend, segments, atRisk, source } = data;

  return (
    <DashboardShell>
      <div ref={scope} className="px-5 py-6 sm:px-8">
        <header data-reveal className="mb-6 flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <StatusPill tone={source === "live" ? "live" : "demo"}>
                {source === "live" ? "Live API" : "Demo fallback"}
              </StatusPill>
              {error ? <StatusPill tone="medium">API degraded</StatusPill> : null}
            </div>
            <h1 className="text-3xl font-semibold text-ink">Executive intelligence</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
              Churn exposure, segment shape, and highest-priority retention targets from the active customer base.
            </p>
          </div>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="focus-ring inline-flex items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/[0.04] px-4 py-2.5 text-sm font-medium text-ink transition hover:border-cyan/40 hover:text-cyan"
          >
            <RefreshCcw size={16} aria-hidden="true" />
            Refresh
          </button>
        </header>

        <section data-reveal className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <KpiCard
            label="Customers"
            value={stats.total_customers}
            delta={5.8}
            tone="cyan"
          />
          <KpiCard
            label="Churn rate"
            value={stats.churn_rate}
            suffix="%"
            delta={-1.7}
            tone="danger"
            formatter={(next) => `${next.toFixed(1)}%`}
          />
          <KpiCard
            label="Active accounts"
            value={stats.active}
            delta={3.2}
            tone="purple"
          />
          <KpiCard
            label="Avg balance"
            value={stats.avg_balance}
            prefix="$"
            delta={4.1}
            tone="cyan"
            formatter={(next) => `$${compactCurrency.format(next)}`}
          />
        </section>

        <section className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1.55fr)_minmax(360px,0.9fr)]">
          <ErrorBoundary>
            <article data-reveal className="glass-panel rounded-lg p-5">
              <SectionHeader eyebrow="Predictive risk" title="Churn probability trend" />
              <div className="mt-5">
                <ChurnTrendChart data={trend} />
              </div>
            </article>
          </ErrorBoundary>

          <ErrorBoundary>
            <article data-reveal className="glass-panel rounded-lg p-5">
              <SectionHeader eyebrow="Segmentation" title="Customer distribution" />
              <div className="mt-5">
                <SegmentDonut data={segments} />
              </div>
            </article>
          </ErrorBoundary>
        </section>

        <ErrorBoundary>
          <section data-reveal className="glass-panel mt-5 rounded-lg p-5">
            <SectionHeader eyebrow="Explainability" title="Top at-risk customers" />
            <div className="mt-5">
              <AtRiskCustomersTable customers={atRisk} />
            </div>
          </section>
        </ErrorBoundary>
      </div>
    </DashboardShell>
  );
}
