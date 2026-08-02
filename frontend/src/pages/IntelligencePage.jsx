import { useState } from "react";
import { FileText, Send } from "lucide-react";
import DashboardShell from "../components/layout/DashboardShell.jsx";
import SectionHeader from "../components/common/SectionHeader.jsx";
import StatusPill from "../components/common/StatusPill.jsx";
import api from "../services/api.js";
import usePageIntro from "../hooks/usePageIntro.js";

export default function IntelligencePage() {
  const scope = usePageIntro([]);
  const [query, setQuery] = useState("Which customer segment is driving avoidable churn this month?");
  const [output, setOutput] = useState(null);
  const [loading, setLoading] = useState(false);

  async function submitQuery(event) {
    event.preventDefault();
    setLoading(true);

    try {
      const response = await api.intelligence.query({ query });
      setOutput(response);
    } catch (error) {
      setOutput({
        status: "planned",
        answer:
          "GraphRAG endpoint is not enabled in this backend yet. The UI contract is ready for reasoning traces, cited tables, and executive brief generation.",
        reasoning: [
          "Retrieve relevant customer cohorts",
          "Rank churn drivers by SHAP contribution",
          "Generate retention playbook and evidence trail"
        ],
        error: error.message
      });
    } finally {
      setLoading(false);
    }
  }

  async function generateBrief() {
    setLoading(true);

    try {
      const response = await api.intelligence.generateBrief({});
      const brief = response.brief || {};
      setOutput({
        status: "brief ready",
        answer: brief.headline || "Executive brief generated.",
        reasoning: Array.isArray(brief.sections) ? brief.sections : []
      });
    } catch (error) {
      setOutput({ status: "brief unavailable", answer: "Could not generate brief.", error: error.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <DashboardShell>
      <div ref={scope} className="px-5 py-6 sm:px-8">
        <header data-reveal className="mb-6">
          <StatusPill tone="live">Live module</StatusPill>
          <h1 className="mt-3 text-3xl font-semibold text-ink">Intelligence</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
            Natural-language analysis and automated executive briefs derived from the active churn model, SHAP drivers, and segments.
          </p>
        </header>

        <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
          <section data-reveal className="glass-panel rounded-lg p-5">
            <SectionHeader eyebrow="NL query" title="Ask CustomerIQ" />
            <form onSubmit={submitQuery} className="mt-5">
              <textarea
                className="focus-ring min-h-36 w-full resize-y rounded-lg border border-white/10 bg-white/[0.04] p-4 text-sm leading-6 text-ink"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
              <div className="mt-4 flex flex-col gap-3 sm:flex-row">
                <button
                  type="submit"
                  disabled={loading}
                  className="focus-ring inline-flex items-center justify-center gap-2 rounded-lg border border-cyan/40 bg-cyan px-4 py-2.5 text-sm font-semibold text-[#041014] transition hover:bg-[#4ee6ff] disabled:cursor-wait disabled:opacity-60"
                >
                  <Send size={16} aria-hidden="true" />
                  {loading ? "Reasoning" : "Run query"}
                </button>
                <button
                  type="button"
                  className="focus-ring inline-flex items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/[0.04] px-4 py-2.5 text-sm font-semibold text-ink transition hover:border-purple/50 hover:text-purple"
                  onClick={generateBrief}
                  disabled={loading}
                >
                  <FileText size={16} aria-hidden="true" />
                  {loading ? "Generating" : "Generate brief"}
                </button>
              </div>
            </form>
          </section>

          <aside data-reveal className="glass-panel rounded-lg p-5">
            <SectionHeader eyebrow="Reasoning trace" title="GraphRAG output" />
            <div className="mt-5 rounded-lg border border-white/10 bg-[#0c0d13] p-4">
              {output ? (
                <div className="space-y-4">
                  <p className="text-sm leading-6 text-ink">{output.answer || output.status}</p>
                  {output.reasoning ? (
                    <ol className="space-y-2">
                      {output.reasoning.map((item) => (
                        <li key={item} className="rounded border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-muted">
                          {item}
                        </li>
                      ))}
                    </ol>
                  ) : null}
                  {output.error ? <p className="text-xs text-warning">{output.error}</p> : null}
                </div>
              ) : (
                <p className="text-sm leading-6 text-muted">No query output yet.</p>
              )}
            </div>
          </aside>
        </div>
      </div>
    </DashboardShell>
  );
}
