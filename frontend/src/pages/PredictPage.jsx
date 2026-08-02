import { useMemo, useState } from "react";
import { Upload, Wand2 } from "lucide-react";
import DashboardShell from "../components/layout/DashboardShell.jsx";
import SectionHeader from "../components/common/SectionHeader.jsx";
import StatusPill from "../components/common/StatusPill.jsx";
import PredictionGauge from "../components/predict/PredictionGauge.jsx";
import FeatureImportanceBars from "../components/charts/FeatureImportanceBars.jsx";
import api from "../services/api.js";
import usePageIntro from "../hooks/usePageIntro.js";

const initialForm = {
  age: 42,
  gender: "Female",
  tenure: 5,
  balance: 87500,
  num_products: 2,
  has_credit_card: 1,
  is_active_member: 0,
  estimated_salary: 118000
};

const fallbackImportance = [
  { name: "is active member", value: 0.42 },
  { name: "balance", value: 0.31 },
  { name: "num products", value: 0.24 },
  { name: "tenure", value: 0.16 },
  { name: "age", value: 0.12 }
];

function coercePayload(form) {
  return {
    age: Number(form.age),
    gender: form.gender,
    tenure: Number(form.tenure),
    balance: Number(form.balance),
    num_products: Number(form.num_products),
    has_credit_card: Number(form.has_credit_card),
    is_active_member: Number(form.is_active_member),
    estimated_salary: Number(form.estimated_salary)
  };
}

function recommendationFor(probability) {
  if (probability >= 0.7) {
    return "Escalate to retention pod, offer fee relief, and assign a high-touch outreach sequence within 24 hours.";
  }

  if (probability >= 0.42) {
    return "Trigger product-depth campaign and monitor engagement over the next two billing cycles.";
  }

  return "Maintain standard success cadence and watch for activity decay or balance movement.";
}

export default function PredictPage() {
  const scope = usePageIntro([]);
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [batchResult, setBatchResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const probability = Number(result?.churn_probability || result?.probability || 0);
  const featureImportance = useMemo(() => {
    if (result?.feature_importance) {
      return Object.entries(result.feature_importance)
        .map(([name, value]) => ({ name: name.replaceAll("_", " "), value: Math.abs(Number(value)) }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 6);
    }

    return fallbackImportance;
  }, [result]);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await api.predict.single(coercePayload(form));
      setResult(response);
    } catch (requestError) {
      setError(requestError.message);
      setResult({
        churn_probability: 0.68,
        risk_level: "Medium",
        feature_importance: Object.fromEntries(fallbackImportance.map((item) => [item.name, item.value]))
      });
    } finally {
      setLoading(false);
    }
  }

  async function handleFileUpload(event) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.predict.batch(file);
      setBatchResult(Array.isArray(response) ? response.slice(0, 5) : response);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
      event.target.value = "";
    }
  }

  return (
    <DashboardShell>
      <div ref={scope} className="px-5 py-6 sm:px-8">
        <header data-reveal className="mb-6">
          <StatusPill tone="neutral">Inference workbench</StatusPill>
          <h1 className="mt-3 text-3xl font-semibold text-ink">Predict churn</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
            Score a customer profile or upload a CSV batch against the active FastAPI model.
          </p>
        </header>

        <div className="grid gap-5 xl:grid-cols-[420px_minmax(0,1fr)]">
          <form data-reveal onSubmit={handleSubmit} className="glass-panel rounded-lg p-5">
            <SectionHeader eyebrow="Customer vector" title="Profile input" />
            <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
              {[
                ["age", "Age", "number"],
                ["tenure", "Tenure", "number"],
                ["balance", "Balance", "number"],
                ["num_products", "Products", "number"],
                ["estimated_salary", "Estimated salary", "number"]
              ].map(([name, label, type]) => (
                <label key={name} className="block">
                  <span className="font-mono text-xs uppercase text-muted">{label}</span>
                  <input
                    className="focus-ring mt-2 w-full rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2.5 text-sm text-ink"
                    type={type}
                    value={form[name]}
                    onChange={(event) => setForm((current) => ({ ...current, [name]: event.target.value }))}
                  />
                </label>
              ))}
              <label className="block">
                <span className="font-mono text-xs uppercase text-muted">Gender</span>
                <select
                  className="focus-ring mt-2 w-full rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2.5 text-sm text-ink"
                  value={form.gender}
                  onChange={(event) => setForm((current) => ({ ...current, gender: event.target.value }))}
                >
                  <option>Female</option>
                  <option>Male</option>
                  <option>Other</option>
                </select>
              </label>
              <label className="flex items-center justify-between rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2.5">
                <span className="font-mono text-xs uppercase text-muted">Credit card</span>
                <input
                  type="checkbox"
                  checked={Boolean(Number(form.has_credit_card))}
                  onChange={(event) => setForm((current) => ({ ...current, has_credit_card: event.target.checked ? 1 : 0 }))}
                />
              </label>
              <label className="flex items-center justify-between rounded-lg border border-white/10 bg-white/[0.03] px-3 py-2.5">
                <span className="font-mono text-xs uppercase text-muted">Active member</span>
                <input
                  type="checkbox"
                  checked={Boolean(Number(form.is_active_member))}
                  onChange={(event) => setForm((current) => ({ ...current, is_active_member: event.target.checked ? 1 : 0 }))}
                />
              </label>
            </div>

            <div className="mt-5 flex flex-col gap-3 sm:flex-row xl:flex-col">
              <button
                type="submit"
                disabled={loading}
                className="focus-ring inline-flex items-center justify-center gap-2 rounded-lg border border-cyan/40 bg-cyan px-4 py-2.5 text-sm font-semibold text-[#041014] transition hover:bg-[#4ee6ff] disabled:cursor-wait disabled:opacity-60"
              >
                <Wand2 size={16} aria-hidden="true" />
                {loading ? "Scoring" : "Run prediction"}
              </button>
              <label className="focus-ring inline-flex cursor-pointer items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/[0.04] px-4 py-2.5 text-sm font-semibold text-ink transition hover:border-purple/50 hover:text-purple">
                <Upload size={16} aria-hidden="true" />
                Upload CSV
                <input type="file" accept=".csv" className="sr-only" onChange={handleFileUpload} />
              </label>
            </div>
          </form>

          <section data-reveal className="grid gap-5 xl:grid-rows-[auto_1fr]">
            <article className="glass-panel rounded-lg p-5">
              <SectionHeader
                eyebrow="Model output"
                title={result ? `Risk level: ${result.risk_level || "Scored"}` : "Awaiting score"}
                action={error ? <StatusPill tone="medium">Fallback view</StatusPill> : null}
              />
              <div className="mt-5 grid gap-5 lg:grid-cols-[280px_minmax(0,1fr)]">
                <PredictionGauge probability={probability} />
                <div className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
                  <h3 className="text-sm font-semibold text-ink">Retention strategy</h3>
                  <p className="mt-3 text-sm leading-6 text-muted">
                    {result ? recommendationFor(probability) : "Submit a customer vector to generate a recommendation."}
                  </p>
                  {error ? <p className="mt-4 text-xs text-warning">{error}</p> : null}
                </div>
              </div>
            </article>

            <article className="glass-panel rounded-lg p-5">
              <SectionHeader eyebrow="Explainability" title="SHAP feature importance" />
              <div className="mt-5">
                <FeatureImportanceBars data={featureImportance} />
              </div>
            </article>
          </section>
        </div>

        {batchResult ? (
          <section data-reveal className="glass-panel mt-5 rounded-lg p-5">
            <SectionHeader eyebrow="Batch preview" title="Latest CSV predictions" />
            <pre className="mt-5 max-h-72 overflow-auto rounded-lg border border-white/10 bg-[#0c0d13] p-4 text-xs text-muted">
              {JSON.stringify(batchResult, null, 2)}
            </pre>
          </section>
        ) : null}
      </div>
    </DashboardShell>
  );
}
