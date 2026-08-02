import { useEffect, useMemo, useState } from "react";
import DashboardShell from "../components/layout/DashboardShell.jsx";
import SectionHeader from "../components/common/SectionHeader.jsx";
import StatusPill from "../components/common/StatusPill.jsx";
import SegmentScatter from "../components/three/SegmentScatter.jsx";
import api from "../services/api.js";
import { mockSegments } from "../data/mockData.js";
import usePageIntro from "../hooks/usePageIntro.js";

const segmentNames = ["Prime Loyalists", "Balance Builders", "Dormant High Value", "Price Sensitive", "New Growth"];

function normalizeSegments(response) {
  if (!response?.segments?.length) {
    return mockSegments;
  }

  const points = response.segments.slice(0, 260).map((customer, index) => {
    const cluster = Number(customer.cluster ?? customer.segment ?? index % 4);
    return {
      id: customer.customer_id || `CUST-${index}`,
      cluster,
      x: (Number(customer.balance || 0) / 60000 - 1.5) + Math.sin(index) * 0.16,
      y: (Number(customer.estimated_salary || 0) / 90000 - 1.3) + Math.cos(index) * 0.16,
      z: (Number(customer.tenure || 0) / 3 - 1.5) + Math.sin(index * 0.7) * 0.16
    };
  });

  const byCluster = points.reduce((acc, point) => {
    acc[point.cluster] = (acc[point.cluster] || 0) + 1;
    return acc;
  }, {});

  return {
    points,
    summary: Object.entries(byCluster).map(([cluster, size]) => ({
      name: segmentNames[Number(cluster)] || `Segment ${Number(cluster) + 1}`,
      size,
      churnRate: 8 + Number(cluster) * 5.7,
      clv: 86000 + Number(cluster) * 32000
    }))
  };
}

export default function SegmentsPage() {
  const scope = usePageIntro([]);
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [data, setData] = useState(mockSegments);
  const [source, setSource] = useState("demo");

  useEffect(() => {
    let cancelled = false;

    api.segments
      .list({ n_clusters: 4 })
      .then((response) => {
        if (!cancelled) {
          setData(normalizeSegments(response));
          setSource("live");
        }
      })
      .catch(() => {
        if (!cancelled) {
          setData(mockSegments);
          setSource("demo");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const selectedProfile = useMemo(() => {
    if (selectedCluster === null) {
      return null;
    }

    return data.summary[selectedCluster] || null;
  }, [data.summary, selectedCluster]);

  return (
    <DashboardShell>
      <div ref={scope} className="px-5 py-6 sm:px-8">
        <header data-reveal className="mb-6">
          <StatusPill tone={source === "live" ? "live" : "demo"}>
            {source === "live" ? "Live clusters" : "Demo clusters"}
          </StatusPill>
          <h1 className="mt-3 text-3xl font-semibold text-ink">Customer segments</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
            KMeans cluster topology across balance, salary, tenure, and behavioral signals.
          </p>
        </header>

        <div className="grid gap-5 xl:grid-cols-[minmax(0,1.35fr)_360px]">
          <section data-reveal className="glass-panel rounded-lg p-5">
            <SectionHeader eyebrow="3D cluster map" title="Behavioral topology" />
            <div className="mt-5">
              <SegmentScatter
                points={data.points}
                selectedCluster={selectedCluster}
                onSelectCluster={setSelectedCluster}
              />
            </div>
          </section>

          <aside data-reveal className="glass-panel rounded-lg p-5">
            <SectionHeader eyebrow="Segment profile" title={selectedProfile?.name || "All segments"} />
            <div className="mt-5 space-y-3">
              {(selectedProfile ? [selectedProfile] : data.summary).map((segment, index) => (
                <div key={segment.name} className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-sm font-semibold text-ink">{segment.name}</span>
                    <span className="data-number text-sm text-cyan">{segment.size.toLocaleString()}</span>
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <p className="font-mono text-[11px] uppercase text-muted">Churn</p>
                      <p className="data-number mt-1 text-warning">{segment.churnRate.toFixed(1)}%</p>
                    </div>
                    <div>
                      <p className="font-mono text-[11px] uppercase text-muted">CLV</p>
                      <p className="data-number mt-1 text-purple">${Math.round(segment.clv / 1000)}K</p>
                    </div>
                  </div>
                  {selectedCluster === null ? (
                    <button
                      type="button"
                      className="focus-ring mt-3 rounded border border-white/10 px-3 py-1.5 text-xs text-muted transition hover:border-cyan/40 hover:text-cyan"
                      onClick={() => setSelectedCluster(index)}
                    >
                      Inspect
                    </button>
                  ) : null}
                </div>
              ))}
            </div>
          </aside>
        </div>
      </div>
    </DashboardShell>
  );
}
