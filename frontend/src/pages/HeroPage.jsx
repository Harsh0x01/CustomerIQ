import { Link } from "react-router-dom";
import {
  Activity,
  ArrowRight,
  BarChart3,
  DatabaseZap,
  ShieldCheck,
  TrendingDown
} from "lucide-react";
import usePageIntro from "../hooks/usePageIntro.js";
import useGsapCounter from "../hooks/useGsapCounter.js";

function FloatingKpi({ label, value, suffix, tone, icon: Icon, delayClass }) {
  const counterRef = useGsapCounter(value, (next) => `${next.toFixed(value < 100 ? 1 : 0)}${suffix}`);

  return (
    <article
      data-reveal
      className={`glass-panel rounded-lg p-4 shadow-cyan ${delayClass || ""}`}
    >
      <div className="flex items-center justify-between gap-4">
        <span className="font-mono text-xs uppercase text-muted">{label}</span>
        <Icon size={17} className={tone === "purple" ? "text-purple" : "text-cyan"} aria-hidden="true" />
      </div>
      <div ref={counterRef} className="data-number mt-4 text-3xl font-semibold text-ink">
        0{suffix}
      </div>
    </article>
  );
}

export default function HeroPage() {
  const scope = usePageIntro([]);

  return (
    <div ref={scope} className="relative overflow-hidden">
      <section className="flex min-h-[88vh] items-center px-5 py-20 sm:px-8 lg:px-12">
        <div className="mx-auto grid w-full max-w-7xl gap-10 lg:grid-cols-[minmax(0,1fr)_360px] lg:items-center">
          <div className="max-w-4xl">
            <div
              data-reveal
              className="mb-5 inline-flex items-center gap-2 rounded border border-cyan/30 bg-cyan/10 px-3 py-2 font-mono text-xs uppercase text-cyan"
            >
              <Activity size={14} aria-hidden="true" />
              AI customer intelligence
            </div>
            <h1
              data-reveal
              className="max-w-3xl text-6xl font-semibold leading-none text-ink sm:text-7xl lg:text-8xl"
            >
              CustomerIQ
            </h1>
            <p
              data-reveal
              className="mt-7 max-w-2xl text-base leading-7 text-muted sm:text-lg"
            >
              Churn prediction, behavioral segmentation, and explainable retention actions in a dense command center built for customer teams that live inside the numbers.
            </p>
            <div data-reveal className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link
                to="/dashboard"
                className="focus-ring inline-flex items-center justify-center gap-2 rounded-lg border border-cyan/40 bg-cyan px-5 py-3 text-sm font-semibold text-[#041014] shadow-cyan transition hover:bg-[#4ee6ff]"
              >
                Enter dashboard
                <ArrowRight size={17} aria-hidden="true" />
              </Link>
              <Link
                to="/segments"
                className="focus-ring inline-flex items-center justify-center gap-2 rounded-lg border border-white/12 bg-white/[0.04] px-5 py-3 text-sm font-semibold text-ink transition hover:border-purple/50 hover:text-purple"
              >
                View segments
                <BarChart3 size={17} aria-hidden="true" />
              </Link>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
            <FloatingKpi
              label="Churn rate"
              value={14.5}
              suffix="%"
              icon={TrendingDown}
              tone="cyan"
            />
            <FloatingKpi
              label="At risk"
              value={1809}
              suffix=""
              icon={ShieldCheck}
              tone="purple"
            />
            <FloatingKpi
              label="Revenue impact"
              value={4.8}
              suffix="M"
              icon={DatabaseZap}
              tone="cyan"
            />
          </div>
        </div>
      </section>

      <section className="border-t border-white/10 bg-void/82 px-5 py-8 backdrop-blur-md sm:px-8 lg:px-12">
        <div className="mx-auto grid max-w-7xl gap-4 sm:grid-cols-3">
          {[
            ["XGBoost", "Calibrated churn scoring"],
            ["KMeans", "Behavioral clusters"],
            ["SHAP", "Reason codes for action"]
          ].map(([label, value]) => (
            <div key={label} data-reveal className="flex items-center justify-between rounded-lg border border-white/10 bg-white/[0.03] px-4 py-3">
              <span className="font-mono text-xs uppercase text-muted">{label}</span>
              <span className="text-sm text-ink">{value}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
